"""Manage binary configuration"""

from dataclasses import dataclass, field
from importlib import import_module
import json
import os
from sys import argv
from types import NoneType
from typing import List, Dict, Any


@dataclass
class Dependency:
    """Dependency information"""

    name: str = ""
    version: str = ""
    resolved_version: str = ""
    user: str = ""
    channel: str = ""
    recipe: str = ""
    dynamic: bool = True
    link_preference: bool = False
    components: Dict[str, str] = field(default_factory=dict)


@dataclass
class Binary:
    """Binary information"""

    name: str = ""
    bin_type: str = ""
    dependencies: Dict[str, Dict[str, bool]] = field(default_factory=dict)
    headers: List[List[str]] = field(default_factory=list)
    sources: List[List[str]] = field(default_factory=list)
    main: List[str] = field(default_factory=list)


def _assert_type(var: Any, *expected_types) -> NoneType:
    """Ensure that a given variable has a given expected type"""
    if type(var) not in expected_types:
        raise BinaryConfigInterpretationError(
            "\n\nExpected one of the following types: "
            + str(expected_types)
            + ", but encountered type '"
            + str(type(var))
            + "' instead\nValue:\n\n"
            + str(var)
            + "\n\n"
        )


def _value_or(
    dictionary: dict, key: Any, default_value: Any, *expected_types
) -> Any:
    """Returns the value for a given key in a given dictionary or a given default value if the key is not found"""
    if key in dictionary:
        value: Any = dictionary[key]
        _assert_type(value, *expected_types)
        return value
    return default_value


class DependencyConfigInterpretationError(Exception):
    """Exception thrown when an error occurs when interpreting the dependency configuration file"""

    def __init__(self, message: str) -> NoneType:
        self.message = message


class Dependencies:
    """Dependency information for the dependency configuration file"""

    def __init__(self, dependencies: Dict[str, Dependency] = {}) -> NoneType:
        self.path = os.path.join(
            os.path.dirname(__file__), "dependency_config.json"
        )
        self.deps = dependencies

    def get(self) -> Dict[str, Dependency]:
        """Returns all dependency information in structured form"""
        return self.deps

    def structured(self, raw_json: dict) -> NoneType:
        """Converts all dependency information from JSON to structured form"""
        _assert_type(raw_json, dict)

        self.deps = {}
        for dep_name, dep in raw_json.items():
            _assert_type(dep_name, str)
            _assert_type(dep, dict)

            # Dependency "Conan recipe" version, user, channel, and revision
            dep_version: str = _value_or(dep, "version", "[*]", str)
            dep_user: str = _value_or(dep, "user", "", str)
            dep_channel: str = _value_or(dep, "channel", "", str)

            if bool(dep_user) ^ bool(dep_channel):  # xor
                raise DependencyConfigInterpretationError(
                    "\n\nBoth the 'user' and 'channel' fields must be defined if either one of them is used.\n\n"
                )

            # Construct the dependency recipe
            dep_recipe: str = dep_name + "/" + dep_version
            if dep_user and dep_channel:
                dep_recipe += "@" + dep_user + "/" + dep_channel

            # Dependency link preference (static or dynamic)
            dep_dynamic: bool = True
            dep_link_preference: bool = False
            if "dynamic" in dep:
                dep_link_preference = dep["dynamic"] != None
                if dep_link_preference:
                    dep_dynamic = dep["dynamic"]
                _assert_type(dep_dynamic, bool)
                _assert_type(dep_link_preference, bool)

            self.deps[dep_name] = Dependency(
                name=dep_name,
                version=dep_version,
                user=dep_user,
                channel=dep_channel,
                recipe=dep_recipe,
                dynamic=dep_dynamic,
                link_preference=dep_link_preference,
            )

    def read(self) -> NoneType:
        """Reads dependency information represented as JSON from the dependency configuration file"""
        raw_json: dict = json.load(open(self.path, "r"))
        self.structured(raw_json)

    def json(self) -> dict:
        """Converts all dependency information from structured form to JSON"""
        raw_json: dict = {}
        for dep_name, dep in self.deps.items():
            raw_json[dep.name] = {
                "version": dep.version,
                "user": dep.user,
                "channel": dep.channel,
                "dynamic": (dep.dynamic if dep.link_preference else None),
            }
        return raw_json

    def write(self) -> NoneType:
        """Writes dependency information to the dependency configuration file represented as JSON"""
        json.dump(self.json(), open(self.path, "w"), indent=4)


class BinaryConfigInterpretationError(Exception):
    """Exception thrown when an error occurs when interpreting the binary configuration file"""

    def __init__(self, message: str) -> NoneType:
        self.message = message


class Binaries:
    """Binary information for the binary configuration file"""

    def __init__(self, binaries: Dict[str, Binary] = {}) -> NoneType:
        self.path = os.path.join(
            os.path.dirname(__file__), "binary_config.json"
        )
        self.binaries = binaries

    def get(self) -> Dict[str, Binary]:
        """Returns all binary information in structured form"""
        return self.binaries

    def _structured_dependencies(
        self, raw_json: dict
    ) -> Dict[str, Dict[str, bool]]:
        """Converts JSON to components"""
        _assert_type(raw_json, dict)

        deps: Dict[str, Dict[str, bool]] = {}

        for dep_name, components in raw_json.items():
            _assert_type(dep_name, str)
            _assert_type(components, dict)

            deps[dep_name] = {}

            for component_name, component_enabled in components.items():
                _assert_type(component_name, str)
                _assert_type(component_enabled, bool)

                deps[dep_name][component_name] = component_enabled

        return deps

    def structured(self, raw_json: dict) -> None:
        """Converts all binary information to JSON to structured form"""
        _assert_type(raw_json, dict)

        self.binaries: Dict[str, Binary] = {}
        for binary_name, binary in raw_json.items():
            _assert_type(binary_name, str)
            _assert_type(binary, dict)

            # Binary type
            bin_type: str = binary["type"]
            _assert_type(bin_type, str)
            valid_bin_types: List[str] = ["application", "library", "test"]
            if bin_type not in valid_bin_types:
                raise BinaryConfigInterpretationError(
                    "The binary type '"
                    + bin_type
                    + "'must be one of "
                    + str(valid_bin_types)
                )

            # Dependencies
            dependencies: Dict[str, Dict[str, bool]] = {}
            if "dependencies" in binary:
                dependencies = self._structured_dependencies(
                    binary["dependencies"]
                )

            # Headers (if applicable)
            headers: List[List[str]] = []
            if bin_type == "library":
                headers = binary["headers"]
                _assert_type(headers, list)
                for header in headers:
                    _assert_type(header, list)
                    for component in header:
                        _assert_type(component, str)
            else:
                if "headers" in binary:
                    print(
                        "Ignoring 'headers' field encountered while interpreting configuration information for binary '"
                        + binary_name
                        + "' of type '"
                        + bin_type
                        + "'"
                    )

            # Sources
            sources: List[List[str]] = binary["sources"]
            _assert_type(sources, list)
            for source in sources:
                _assert_type(source, list)
                for component in source:
                    _assert_type(component, str)

            # Source containing the 'main' function (if applicable)
            main: List[str] = []
            if bin_type == "application":
                main = binary["main"]
                _assert_type(main, list)
                for component in main:
                    _assert_type(component, str)
            elif bin_type == "test":
                # Some testing libraries (i.e. GoogleTest) do not require tests to have a 'main' function, so 'main' functions are optional for tests.
                main = binary["main"] if "main" in binary else []
                _assert_type(main, list)
                for component in main:
                    _assert_type(component, str)
            else:
                if "main" in binary:
                    print(
                        "Ignoring 'main' field encountered while interpreting configuration information for binary '"
                        + binary_name
                        + "' of type '"
                        + bin_type
                        + "'"
                    )

            self.binaries[binary_name] = Binary(
                name=binary_name,
                bin_type=bin_type,
                dependencies=dependencies,
                headers=headers,
                sources=sources,
                main=main,
            )

    def read(self) -> None:
        """Reads binary information represented as JSON from the binary configuration file"""
        raw_json: dict = json.load(open(self.path, "r"))
        self.structured(raw_json)

    def json(self) -> dict:
        """Converts all binary information from structured form to JSON"""
        raw_json: dict = {}
        for binary_name, binary in self.binaries.items():
            raw_json_binary = {}
            raw_json_binary["type"] = binary.bin_type
            raw_json_binary["dependencies"] = binary.dependencies
            if binary.bin_type == "library":
                raw_json_binary["headers"] = binary.headers
            raw_json_binary["sources"] = binary.sources
            if len(binary.main) > 0:
                raw_json_binary["main"] = binary.main
            raw_json[binary.name] = raw_json_binary
        return raw_json

    def write(self) -> None:
        """Writes binary information to the binary configuration file represented as JSON"""
        json.dump(self.json(), open(self.path, "w"), indent=4)


def unstructured(
    binaries: Dict[str, Binary], deps: Dict[str, Dependency]
) -> list:
    """Converts the given binary and dependency information from structured form to an unstructured form comprised entirely of lists (no dictionaries)"""
    raw_data = []

    for binary_name, binary in binaries.items():
        dependencies = []
        for dep_name, dep in binary.dependencies.items():
            components = []
            for component_name, component_enabled in dep.items():
                components.append(
                    [
                        component_name,
                        deps[dep_name].components[component_name],
                        component_enabled,
                    ]
                )
            dependencies.append(
                [
                    dep_name,
                    deps[dep_name].resolved_version,
                    deps[dep_name].link_preference,
                    deps[dep_name].dynamic,
                    components,
                ]
            )
        raw_data.append(
            [
                binary.name,
                binary.bin_type,
                dependencies,
                binary.headers,
                binary.sources,
                binary.main,
            ]
        )
    return raw_data


if __name__ == "__main__":
    """Update dependency information in the binary configuration file"""
    build = import_module("build")
    profiles = import_module("profiles")
    build.conan(
        "build",
        profiles.get_profiles(),
        extra_args=["--options:all", "quit_after_generate=True"]
        + list(argv)[1:],
    )

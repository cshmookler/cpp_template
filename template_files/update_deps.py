"""Manage binary configuration"""

from dataclasses import dataclass
from importlib import import_module
import json
import os
import subprocess
from types import NoneType
from typing import List, Dict


path: str = os.path.join(os.path.dirname(__file__), "binary_config.json")


@dataclass
class Component:
    """Dependency component information"""

    name: str
    enabled: bool


@dataclass
class Dependency:
    """Dependency information"""

    name: str
    version: str
    enabled: bool
    link_preference: bool
    dynamic: bool
    components: List[Component]


@dataclass
class Binary:
    """Binary information"""

    name: str
    bin_type: str
    dependencies: List[Dependency]
    headers: List[List[str]]
    sources: List[List[str]]
    main: List[str]


class BinaryConfigInterpretationError(Exception):
    """Exception thrown when an error occurs when interpreting the binary configuration file"""

    def __init__(self, message: str) -> None:
        self.message = message


def _assert_type(var, *expected_types) -> None:
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


class Binaries:
    """Binary information for the binary configuration file"""

    def __init__(self, binaries: List[Binary] = []) -> None:
        self.binaries = binaries

    def __iter__(self):
        for binary in self.binaries:
            yield binary

    @staticmethod
    def file_exists() -> bool:
        """Returns true if the binary configuration file exists and false otherwise"""
        return os.path.isfile(path)

    def structured(self, raw_json: dict) -> None:
        """Converts all binary information to JSON to structured form"""
        _assert_type(raw_json, dict)

        self.binaries = []
        for binary_name, binary_info in raw_json.items():
            _assert_type(binary_name, str)
            _assert_type(binary_info, dict)

            # Binary type
            bin_type: str = binary_info["type"]
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
            dependencies: List[Dependency] = []
            if "dependencies" in binary_info:
                _assert_type(binary_info["dependencies"], dict)
                for name_and_version, dep_info in binary_info[
                    "dependencies"
                ].items():
                    _assert_type(name_and_version, str)
                    _assert_type(dep_info, dict)

                    # Dependency name and version
                    if name_and_version.find("/") == -1:
                        raise BinaryConfigInterpretationError(
                            "Dependencies must be in the form 'name/version', but no '/' symbol was found in '"
                            + name_and_version
                            + "'"
                        )
                    dep_name, dep_version = name_and_version.rsplit("/", 1)

                    # Dependency status (enabled or not)
                    enabled: bool = True
                    if "enabled" in dep_info:
                        enabled = dep_info["enabled"]
                        _assert_type(enabled, bool)
                        if not enabled:
                            continue

                    # Dependency link preference (static or dynamic)
                    link_preference: bool = False
                    dynamic: bool = True
                    if "dynamic" in dep_info:
                        prefer_dynamic: bool | None = dep_info["dynamic"]
                        _assert_type(prefer_dynamic, bool, NoneType)
                        link_preference = prefer_dynamic is not None
                        dynamic = (
                            prefer_dynamic
                            if prefer_dynamic is not None
                            else True
                        )

                    # Dependency component information
                    components: List[Component] = []
                    if "components" in dep_info:
                        declared_components: dict = dep_info["components"]
                        _assert_type(declared_components, dict)
                        for (
                            component_name,
                            component_enabled,
                        ) in declared_components.items():
                            _assert_type(component_name, str)
                            _assert_type(component_enabled, bool)
                            components.append(
                                Component(
                                    name=component_name,
                                    enabled=component_enabled,
                                )
                            )

                    dependencies.append(
                        Dependency(
                            name=dep_name,
                            version=dep_version,
                            enabled=enabled,
                            link_preference=link_preference,
                            dynamic=dynamic,
                            components=components,
                        )
                    )

            # Headers (if applicable)
            if bin_type == "library":
                headers: List[List[str]] = binary_info["headers"]
                _assert_type(headers, list)
                for header in headers:
                    _assert_type(header, list)
                    for component in header:
                        _assert_type(component, str)
            else:
                headers: List[List[str]] = []
                if "headers" in binary_info:
                    print(
                        "Ignoring 'headers' field encountered while interpreting configuration information for binary '"
                        + binary_name
                        + "' of type '"
                        + bin_type
                        + "'"
                    )

            # Sources
            sources: List[List[str]] = binary_info["sources"]
            _assert_type(sources, list)
            for source in sources:
                _assert_type(source, list)
                for component in source:
                    _assert_type(component, str)

            # Source containing the 'main' function (if applicable)
            if bin_type == "application":
                main: List[str] = binary_info["main"]
                _assert_type(main, list)
                for component in main:
                    _assert_type(component, str)
            elif bin_type == "test":
                # Some testing libraries (i.e. GoogleTest) do not require tests to have a 'main' function, so 'main' functions are optional for tests.
                main: List[str] = (
                    binary_info["main"] if "main" in binary_info else []
                )
                _assert_type(main, list)
                for component in main:
                    _assert_type(component, str)
            else:
                main: List[str] = []
                if "main" in binary_info:
                    print(
                        "Ignoring 'main' field encountered while interpreting configuration information for binary '"
                        + binary_name
                        + "' of type '"
                        + bin_type
                        + "'"
                    )

            self.binaries.append(
                Binary(
                    name=binary_name,
                    bin_type=bin_type,
                    dependencies=dependencies,
                    headers=headers,
                    sources=sources,
                    main=main,
                )
            )

    def read(self) -> None:
        """Reads binary information represented as JSON from the binary configuration file"""
        raw_json: dict = json.load(open(path, "r"))
        self.structured(raw_json)

    @staticmethod
    def _json_deps(
        dependencies: List[Dependency],
    ) -> Dict[str, Dict[str, Dict[str, bool] | bool | None]]:
        """Converts dependencies to JSON"""
        raw_json: Dict[str, Dict[str, Dict[str, bool] | bool | None]] = {}
        for dep in dependencies:
            raw_json[dep.name + "/" + dep.version] = {
                "enabled": dep.enabled,
                "dynamic": (dep.dynamic if dep.link_preference else None),
                "components": {
                    component.name: component.enabled
                    for component in dep.components
                },
            }
        return raw_json

    def json(self) -> Dict[
        str,
        Dict[
            str,
            Dict[str, Dict[str, Dict[str, bool] | bool | None]]
            | List[List[str]]
            | List[str]
            | str,
        ],
    ]:
        """Converts all binary information from structured form to JSON"""
        raw_json: Dict[
            str,
            Dict[
                str,
                Dict[str, Dict[str, Dict[str, bool] | bool | None]]
                | List[List[str]]
                | List[str]
                | str,
            ],
        ] = {}
        for binary in self.binaries:
            raw_json[binary.name] = {}
            raw_json[binary.name]["type"] = binary.bin_type
            raw_json[binary.name]["dependencies"] = Binaries._json_deps(
                binary.dependencies
            )
            if binary.bin_type == "library":
                raw_json[binary.name]["headers"] = binary.headers
            raw_json[binary.name]["sources"] = binary.sources
            if len(binary.main) > 0:
                raw_json[binary.name]["main"] = binary.main
        return raw_json

    def unstructured(
        self,
    ) -> List[
        List[
            str
            | List[str]
            | List[List[str]]
            | List[List[bool | str | List[List[bool | str]]]]
        ]
    ]:
        """Converts all binary information from structured form to an unstructured form comprised entirely of lists (no dictionaries)"""
        raw: List[
            List[
                str
                | List[str]
                | List[List[str]]
                | List[List[bool | str | List[List[bool | str]]]]
            ]
        ] = []

        for binary in self.binaries:
            raw.append(
                [
                    binary.name,
                    binary.bin_type,
                    [
                        [
                            dependency.name,
                            dependency.version,
                            dependency.enabled,
                            dependency.link_preference,
                            dependency.dynamic,
                            [
                                [
                                    component.name,
                                    component.enabled,
                                ]
                                for component in dependency.components
                            ],
                        ]
                        for dependency in binary.dependencies
                    ],
                    binary.headers,
                    binary.sources,
                    binary.main,
                ]
            )
        return raw

        # raw_example = [
        #     [
        #         "cpp_template",  # name
        #         "application",  # type
        #         [],  # dependencies
        #         [],  # headers
        #         [["src", "version.cpp"]],  # sources
        #         ["src", "main.cpp"],  # main
        #     ],
        #     [
        #         "version",  # name
        #         "test",  # type
        #         [  # dependencies
        #             [
        #                 "zlib",  # dep_name
        #                 "1.3.1",  # dep_version
        #                 True,  # enabled
        #                 None,  # dynamic
        #                 [],  # components
        #             ],
        #             [
        #                 "gtest",  # dep_name
        #                 "1.14.0",  # dep_version
        #                 True,  # enabled
        #                 None,  # dynamic
        #                 [  # components
        #                     ["gtest", True],
        #                     ["gtest_main", True],
        #                     ["gmock", True],
        #                     ["gmock_main", True],
        #                 ],
        #             ],
        #         ],
        #         [],  # headers
        #         [  # sources
        #             ["src", "version.test.cpp"],
        #             ["src", "version.cpp"],
        #         ],
        #         [],  # main
        #     ],
        # ]

    def write(self) -> None:
        """Writes binary information to the binary configuration file represented as JSON"""
        json.dump(self.json(), open(path, "w"), indent=4)


if __name__ == "__main__":
    """Update implicit dependencies in the binary configuration file"""
    build = import_module("build")
    profile = import_module("profile")
    build.build(
        profile.get_profile(),
        extra_args=["--options:all", "quit_after_generate=True"],
    )

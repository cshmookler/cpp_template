"""Configure this template project"""

import json
import os
import shutil
import stat
import subprocess
import time
from ast import literal_eval
from configparser import ConfigParser
from dataclasses import dataclass
from importlib import import_module
from os.path import dirname, join
from typing import Callable, Dict, KeysView, List, Union


this_dir: str = dirname(__file__)


def valid_identifier_name(name: str) -> bool:
    """Verify that a given string is a valid C++ identifier name."""

    # At least one character and starts with a letter.
    if len(name) == 0 or not name[0].isalpha():
        return False
    # All characters are either a letter, number, or underscore.
    for c in name:
        if not c.isalnum() and c != "_":
            return False
    return True


def valid_list(list_str: str) -> bool:
    """Verify that a given string represents a valid Python list."""

    try:
        if type(literal_eval(list_str)) != list:
            return False
    except SyntaxError:
        return False
    return True


def optional(_: str) -> bool:
    """Return True regardless of the given string value."""

    return True


def required(given_str: str) -> bool:
    """Verify that a given string is not empty."""

    return given_str != "" and given_str is not None


@dataclass
class ConfigInfo:
    """Information relating to a specific configuration."""

    default: str = ""
    constraint: Callable[[str], bool] = required


def assert_none_missing(
    expected: Union[List[str], KeysView[str]],
    parsed: Union[List[str], KeysView[str]],
    classification: str,
) -> None:
    """Ensure that all items in the expected list are in the parsed list."""

    missing_sections: List[str] = [k for k in expected if k not in parsed]
    if len(missing_sections) <= 0:
        return
    print("Error: The following " + classification + " were not found:")
    for k in missing_sections:
        print(k + " ", end="")
    print(end="\n")
    exit(1)


def get_config() -> Dict[str, str]:
    """Retrieve configuration information"""

    ini_file: str = join(this_dir, "template_config.ini")
    section_name: str = "template_config"
    expected_configs: Dict[str, ConfigInfo] = {
        "package_name": ConfigInfo(
            default="cpp_template", constraint=valid_identifier_name
        ),
        "namespace": ConfigInfo(default="tmpl", constraint=valid_identifier_name),
        "author": ConfigInfo(default=""),
        "description": ConfigInfo(default=""),
        "license": ConfigInfo(default=""),
        "package_type": ConfigInfo(
            default="application",
            constraint=lambda s: s
            in [
                "application",
                "library",
            ],
        ),
        "version_header": ConfigInfo(
            default="true",
            constraint=lambda s: s
            in [
                "true",
                "false",
            ],
        ),
        "conan": ConfigInfo(
            default="true",
            constraint=lambda s: s
            in [
                "true",
                "false",
            ],
        ),
        "dependencies": ConfigInfo(default="[]", constraint=valid_list),
        "email": ConfigInfo(default=""),
        "website_url": ConfigInfo(default=""),
        "git_url": ConfigInfo(default=""),
        "topics": ConfigInfo(default="[]", constraint=valid_list),
        "current_year": ConfigInfo(default=str(time.localtime().tm_year)),
    }

    # Read the configuration file.
    parser = ConfigParser()
    parser.read(ini_file)
    assert_none_missing([section_name], parser.sections(), "sections")
    parsed_configs = parser[section_name]

    # Verify that the given values meet their cooresponding constraints.
    configs: Dict[str, str] = {}
    for key, value in expected_configs.items():
        try:
            parsed_value: str = parsed_configs[key]
        except KeyError:
            parsed_value = value.default

        if not value.constraint(parsed_value):
            configs[key] = value.default
            raise RuntimeError(
                "Invalid option '" + parsed_value + "' for '" + key + "'."
            )

        configs[key] = parsed_value

    # Add options that are derived from others.
    if configs["conan"] == "true":
        if configs["package_type"] == "application":
            configs["version_header_dir"] = "src"
        else:
            configs["version_header_dir"] = "include"
    else:
        configs["version_header_dir"] = "build"

    return configs


def remove(*path: str) -> None:
    """Remove a file or directory (relative to this directory) or do nothing if it doesn't exist."""

    full_path: str = join(this_dir, *path)

    if not os.path.exists(full_path):
        # The path does not exist.  Do nothing.
        return

    if os.path.isfile(full_path):
        # The path is a file.
        os.remove(full_path)
        return

    # The path is a directory.

    def shutil_onerror(func, path, exc_info) -> None:
        """On access error, add write permissions and try again"""

        if os.access(path, os.W_OK):
            raise
        os.chmod(path, stat.S_IWUSR)
        func(path)

    shutil.rmtree(full_path, onerror=shutil_onerror)


def configure() -> None:
    """Configure this template project"""

    config = get_config()

    # Remove unnecessary files.
    remove(".git")
    remove("tests")
    remove(".gitignore")
    remove(".gitattributes")
    remove("LICENSE")
    remove("README.md")

    # Create a fresh git repository.
    subprocess.run(["git", "init", "--initial-branch", "main", this_dir], check=True)

    # Unpack template files.
    for file in os.listdir(join(this_dir, "template_files")):
        shutil.move(join(this_dir, "template_files", file), join(this_dir, file))
    remove("template_files")

    if config["conan"] == "true":
        # The VERSION file is unnecessary if Conan is used.
        remove("VERSION")

    # Create the virtual environment.
    venv = import_module("this_venv")
    venv.create()

    # Configure templates.
    subprocess.run(
        [
            venv.python(),
            join(this_dir, "configure_templates.py"),
            json.dumps(config),
        ],
        check=True,
    )

    # Remove files dependent on the package type.
    if config["package_type"] == "library":
        remove("src", "main.cpp.tmpl")
        if config["conan"] != "true":
            remove("test_package")
            remove("install.py")
    else:
        shutil.move(
            join(this_dir, "include", "version.hpp.in"),
            join(this_dir, "src"),
        )
        remove("include")
        remove("test_package")
        remove("install.py")

    # Remove files dependent on use of the version header
    if config["version_header"] != "true":
        remove("src", "version.cpp")
        if config["package_type"] == "library":
            remove("include", "version.hpp.in")
        else:
            remove("src", "version.hpp.in")
        remove("tests", "version.test.cpp")
        if config["conan"] != "true":
            remove("test_package")

    # Remove files dependent on support for Conan.
    if config["conan"] != "true":
        remove("build_scripts")
        remove("conanfile.py.tmpl")
        remove("clean.py.tmpl")
        remove("build.py")
        remove("clear_cache.py")
        remove("profiles.py")
        remove("this_venv.py")
        remove("update_deps.py")

    if config["conan"] == "true":
        config_module = import_module("update_deps")

        # Accumulate all dependencies and their cooresponding versions
        raw_project_deps = literal_eval(config["dependencies"])
        structured_project_deps: dict = {}
        for dep in raw_project_deps:
            dep_name, dep_version = dep.rsplit("/", 1)
            structured_project_deps[dep_name] = config_module.Dependency(
                name=dep_name,
                version=dep_version,
            )

        # Create the dependency configuration file
        deps = config_module.Dependencies(structured_project_deps)
        deps.write()

        # Accumulate all dependency names
        dep_names: Dict[str, dict] = {}
        for dep_name in structured_project_deps.keys():
            dep_names[dep_name] = {}

        # Construct the binary configuration.
        binary_config = {
            config["package_name"]: config_module.Binary(
                name=config["package_name"],
                bin_type=config["package_type"],
                dependencies=dep_names,
                headers=(
                    [[config["version_header_dir"], "version.hpp"]]
                    if config["version_header"] == "true"
                    and config["package_type"] == "library"
                    else []
                ),
                sources=(
                    [["src", "version.cpp"]]
                    if config["version_header"] == "true"
                    else []
                ),
                main=(
                    [] if config["package_type"] == "library" else ["src", "main.cpp"]
                ),
            )
        }

        if config["version_header"] == "true":
            binary_config["version"] = config_module.Binary(
                name="version",
                bin_type="test",
                dependencies={"gtest": {}},
                headers=[],
                sources=[
                    ["tests", "version.test.cpp"],
                    ["src", "version.cpp"],
                ],
                main=[],
            )

        # Create the binary configuration file
        binaries = config_module.Binaries(binary_config)
        binaries.write()

    # Remove this configuration script, the templater script, and the cooresponding .ini file once project configuration is complete.
    remove("config.py")
    remove("configure_templates.py")
    remove("template_config.ini")

    # Remove the virtual environment and pre-compiled Python bytecode if Conan is not used.
    if config["conan"] != "true":
        remove(venv.name)
        remove("__pycache__")


if __name__ == "__main__":
    configure()

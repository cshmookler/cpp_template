"""Configure this template project"""

from ast import literal_eval
from configparser import ConfigParser
from dataclasses import dataclass
from importlib import import_module
import json
import os
from os import remove, rename, listdir
from os.path import join, dirname
import platform
import shutil
import stat
import subprocess
import time
from typing import Dict, List, KeysView, Union, Callable, Any
from types import NoneType


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
    return given_str != "" and given_str != None


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
    """Retrieve configuration information."""
    ini_file: str = join(this_dir, "template_config.ini")
    section_name: str = "template_config"
    expected_configs: Dict[str, ConfigInfo] = {
        "package_name": ConfigInfo(
            default="cpp_template", constraint=valid_identifier_name
        ),
        "namespace": ConfigInfo(
            default="tmpl", constraint=valid_identifier_name
        ),
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
        "url": ConfigInfo(default=""),
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
    for k, v in expected_configs.items():
        try:
            pv: str = parsed_configs[k]
        except KeyError:
            pv = v.default

        if not v.constraint(pv):
            configs[k] = v.default
            raise RuntimeError(
                "Invalid option '"
                + pv
                + "' for '"
                + k
                + "'. Using '"
                + v.default
                + "' instead."
            )

        configs[k] = pv

    # Add options that are derived from others.
    if configs["conan"] == "true":
        if configs["package_type"] == "application":
            configs["version_header_dir"] = "src"
        else:
            configs["version_header_dir"] = configs["package_name"]
    else:
        configs["version_header_dir"] = "build"

    return configs


def shutil_onerror(func, path, exc_info) -> None:
    """On access error, add write permissions and try again"""
    if os.access(path, os.W_OK):
        raise
    os.chmod(path, stat.S_IWUSR)
    func(path)


def configure() -> None:
    """Configure this template project"""
    config = get_config()

    # Remove unnecessary files.
    shutil.rmtree(join(this_dir, ".git"), onerror=shutil_onerror)
    shutil.rmtree(join(this_dir, "tests"))
    remove(join(this_dir, ".gitignore"))
    remove(join(this_dir, ".gitattributes"))
    remove(join(this_dir, "LICENSE"))
    remove(join(this_dir, "README.md"))

    # Create a fresh git repository.
    subprocess.run(
        ["git", "init", "--initial-branch", "main", this_dir], check=True
    )

    # Unpack template files.
    for file in listdir(join(this_dir, "template_files")):
        shutil.move(
            join(this_dir, "template_files", file), join(this_dir, file)
        )
    shutil.rmtree(join(this_dir, "template_files"))

    # Remove the VERSION file if Conan is used.
    if config["conan"] == "true":
        remove(join(this_dir, "VERSION"))

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
        remove(join(this_dir, "src", "main.cpp.tmpl"))
        rename(
            join(this_dir, "{{ package_name }}"),
            join(this_dir, config["package_name"]),
        )
        if config["conan"] != "true":
            shutil.rmtree(join(this_dir, "test_package"))
            remove(join(this_dir, "install.py"))
    else:
        shutil.move(
            join(this_dir, "{{ package_name }}", "version.hpp.in"),
            join(this_dir, "src"),
        )
        shutil.rmtree(join(this_dir, "{{ package_name }}"))
        shutil.rmtree(join(this_dir, "test_package"))
        remove(join(this_dir, "install.py"))

    # Remove files dependent on support for Conan.
    if config["conan"] != "true":
        shutil.rmtree(join(this_dir, "build_scripts"))
        remove(join(this_dir, "conanfile.py.tmpl"))
        remove(join(this_dir, "clean.py.tmpl"))
        remove(join(this_dir, "build.py"))
        remove(join(this_dir, "clear_cache.py"))
        remove(join(this_dir, "profiles.py"))
        remove(join(this_dir, "this_venv.py"))
        remove(join(this_dir, "update_deps.py"))

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

        # Create the binary configuration file
        binaries = config_module.Binaries(
            {
                config["package_name"]: config_module.Binary(
                    name=config["package_name"],
                    bin_type=config["package_type"],
                    dependencies=dep_names,
                    headers=[
                        (
                            [config["version_header_dir"], "version.hpp"]
                            if config["package_type"] == "library"
                            else []
                        )
                    ],
                    sources=[["src", "version.cpp"]],
                    main=(
                        []
                        if config["package_type"] == "library"
                        else ["src", "main.cpp"]
                    ),
                ),
                "version": config_module.Binary(
                    name="version",
                    bin_type="test",
                    dependencies={"gtest": {}},
                    headers=[],
                    sources=[
                        ["src", "version.test.cpp"],
                        ["src", "version.cpp"],
                    ],
                    main=[],
                ),
            }
        )
        binaries.write()

    # Remove this configuration script, the templater script, and the cooresponding .ini file once project configuration is complete.
    remove(join(this_dir, "config.py"))
    remove(join(this_dir, "configure_templates.py"))
    remove(join(this_dir, "template_config.ini"))

    # Remove the virtual environment and pre-compiled Python bytecode if Conan is not used.
    if config["conan"] != "true":
        shutil.rmtree(join(this_dir, venv.name))
        shutil.rmtree(join(this_dir, "__pycache__"))


if __name__ == "__main__":
    configure()

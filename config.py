"""Configure this template project"""

from ast import literal_eval
from configparser import ConfigParser
from dataclasses import dataclass
from importlib import import_module
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


def inline_print(return_val: Any, print_msg: str) -> Any:
    """Prints a given message and returns a given value."""
    print(print_msg)
    return return_val


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
    return True


def required(given_str: str) -> bool:
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
        "operating_system": ConfigInfo(default=platform.system()),
        "architecture": ConfigInfo(default=platform.machine()),
        "package_name": ConfigInfo(
            default="cpp_template", constraint=valid_identifier_name
        ),
        "namespace": ConfigInfo(
            default="tmpl", constraint=valid_identifier_name
        ),
        "package_type": ConfigInfo(
            default="application",
            constraint=lambda s: s
            in [
                "application",
                "library",
                "header-library",
                "shared_library",
                "static-library",
            ],
        ),
        "dependencies": ConfigInfo(default="[]", constraint=valid_list),
        "current_year": ConfigInfo(default=str(time.localtime().tm_year)),
        "author": ConfigInfo(default=""),
        "email": ConfigInfo(default=""),
        "license": ConfigInfo(default=""),
        "url": ConfigInfo(default=""),
        "description": ConfigInfo(default=""),
        "topics": ConfigInfo(default="[]", constraint=valid_list),
    }

    parser = ConfigParser()
    parser.read(ini_file)
    assert_none_missing([section_name], parser.sections(), "sections")
    parsed_configs = parser[section_name]

    configs: Dict[str, str] = {}
    for k, v in expected_configs.items():
        try:
            pv: str = parsed_configs[k]
        except KeyError:
            pv = v.default
        configs[k] = (
            pv
            if v.constraint(pv)
            else inline_print(
                v.default,
                "Warning: Invalid option '"
                + pv
                + "' for '"
                + k
                + "'. Using '"
                + v.default
                + "' instead.",
            )
        )

    configs["version_header_dir"] = (
        "src"
        if configs["package_type"] == "application"
        else configs["package_name"]
    )

    return configs


@dataclass
class EscapeInfo:
    """Information relating to a specific identifier."""

    prefix: str
    postfix: str


class InvalidTemplateFile(Exception):
    """Exception thrown when a template_file does not have a template file extension"""

    def __init__(self, message: str) -> None:
        self.message = message


def configure_template(path: str, config: Dict[str, str]) -> None:
    """Insert configuration information into the provided template file."""
    template_file_extension = ".tmpl"
    if not path.endswith(template_file_extension):
        raise InvalidTemplateFile(
            "Template files must have a template file extension ("
            + template_file_extension
            + ")"
        )

    newline_char: str = "\n"
    template = open(path, mode="r", newline=newline_char)
    escape_strings: List[EscapeInfo] = [
        EscapeInfo("___", "___"),
        EscapeInfo('["<<', '>>"]'),
    ]

    active_escape: Union[EscapeInfo, NoneType] = None
    read_so_far: str = ""
    cols_since_newline = 0
    newlines_so_far: int = 0
    id_start: int = 0

    c: str
    while c := template.read(1):
        read_so_far += c
        cols_since_newline += 1

        if c == newline_char:
            newlines_so_far += 1
            cols_since_newline = 0

        if active_escape is not None:
            if not read_so_far.endswith(active_escape.postfix):
                continue

            id: str = read_so_far[
                id_start : -len(active_escape.postfix)
            ].strip()

            cutoff_i: int = id_start - len(active_escape.prefix)

            if id not in config:
                raise RuntimeError(
                    "Unknown identifier '"
                    + id
                    + "' at line "
                    + str(newlines_so_far + 1)
                    + " column "
                    + str(cols_since_newline + 1)
                    + " in '"
                    + path
                    + "'"
                )

            id_value: str = config[id]
            read_so_far = read_so_far[:cutoff_i] + id_value
            active_escape = None

        e: EscapeInfo
        for e in escape_strings:
            if not read_so_far.endswith(e.prefix):
                continue

            active_escape = e
            id_start = len(read_so_far)
            break

    template.close()

    # Remove the template file.
    remove(path)

    # Write to a new file.
    template = open(
        path.removesuffix(template_file_extension),
        mode="w",
        newline=newline_char,
    )
    template.write(read_so_far)
    template.close()


class CommandFailure(Exception):
    """Exception thrown when a command run in a subprocess fails"""

    def __init__(self, message) -> None:
        self.message = message


def cmd(args: List[str]) -> None:
    """Execute a command in a subprocess and throw an exception upon failure"""
    if subprocess.call(args) != 0:
        raise CommandFailure("Command failed: " + str(args))


def shutil_onerror(func, path, exc_info):
    """On access error, add write permissions and try again"""
    if os.access(path, os.W_OK):
        raise
    os.chmod(path, stat.S_IWUSR)
    func(path)


def configure():
    """Configure this template project"""
    config = get_config()

    # Remove unnecessary files.
    shutil.rmtree(join(this_dir, ".git"), onerror=shutil_onerror)
    remove(join(this_dir, ".gitattributes"))
    remove(join(this_dir, "LICENSE"))
    remove(join(this_dir, "README.md"))

    # Create a fresh git repository.
    cmd(["git", "init", "--initial-branch", "main", this_dir])

    # Unpack template files.
    for file in listdir(join(this_dir, "template_files")):
        shutil.move(
            join(this_dir, "template_files", file), join(this_dir, file)
        )
    shutil.rmtree(join(this_dir, "template_files"))

    # Generate a LICENSE file if the selected license is 'Zlib'.
    if config["license"] == "Zlib":
        configure_template(join(this_dir, "LICENSE.tmpl"), config)
    else:
        remove(join(this_dir, "LICENSE.tmpl"))

    # Configure templates.
    configure_template(
        join(this_dir, "___package_name___", "version.hpp.in.tmpl"),
        config,
    )
    configure_template(
        join(this_dir, "src", "version.cpp.tmpl"),
        config,
    )
    configure_template(
        join(this_dir, "src", "version.test.cpp.tmpl"),
        config,
    )
    configure_template(join(this_dir, "conanfile.py.tmpl"), config)
    configure_template(join(this_dir, "meson.build.tmpl"), config)
    configure_template(join(this_dir, ".gitignore.tmpl"), config)
    configure_template(join(this_dir, "README.md.tmpl"), config)
    configure_template(
        join(this_dir, "profiles", "default.profile.tmpl"),
        config,
    )
    if config["package_type"] == "application":
        configure_template(join(this_dir, "clean-app.py.tmpl"), config)
        rename(join(this_dir, "clean-app.py"), join(this_dir, "clean.py"))
        remove(join(this_dir, "clean-lib.py.tmpl"))
        configure_template(
            join(this_dir, "src", "main.cpp.tmpl"),
            config,
        )
        shutil.move(
            join(this_dir, "___package_name___", "version.hpp.in"), "src"
        )
        shutil.rmtree(join(this_dir, "___package_name___"))
        shutil.rmtree(join(this_dir, "test_package"))
        remove(join(this_dir, "install.py"))
    else:
        configure_template(join(this_dir, "clean-lib.py.tmpl"), config)
        rename(join(this_dir, "clean-lib.py"), join(this_dir, "clean.py"))
        remove(join(this_dir, "clean-app.py.tmpl"))
        remove(join(this_dir, "src", "main.cpp.tmpl"))
        configure_template(
            join(this_dir, "test_package", "conanfile.py.tmpl"),
            config,
        )
        configure_template(
            join(this_dir, "test_package", "src", "main.cpp.tmpl"),
            config,
        )
        rename(
            join(this_dir, "___package_name___"),
            join(this_dir, config["package_name"]),
        )

    # Declare explicit dependencies
    dep_module = import_module("update_deps")
    explicit_deps = []
    for dep in literal_eval(config["dependencies"]):
        name, version = dep.rsplit("/", 1)
        explicit_deps.append(dep_module.Dependency(name, version, True))
    deps = dep_module.Dependencies(
        join(this_dir, "dependencies.ini"),
        explicit=explicit_deps,
    )
    deps.write()

    # Remove this configuration script and the cooresponding .ini file once all previous operations succeeded.
    remove(join(this_dir, "config.py"))
    remove(join(this_dir, "template_config.ini"))


if __name__ == "__main__":
    configure()

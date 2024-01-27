"""Configure this template project"""

from ast import literal_eval
from configparser import ConfigParser
from dataclasses import dataclass
from os import remove, rename, listdir
from os.path import join
import platform
import shutil
import subprocess
import time
from typing import Dict, List, KeysView, Union, Callable, Any
from types import NoneType


def inline_print(return_val: Any, print_msg: str) -> Any:
    """Prints a given message and returns a given value."""
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
    ini_file: str = "template_config.ini"
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

    if configs["package_type"] == "library":
        configs["version_header_dir"] = join("include", configs["package_name"])
    elif configs["package_type"] == "application":
        configs["version_header_dir"] = "src"

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
    # newline: int = 0
    newlines_so_far: int = 0
    id_start: int = 0

    c: str
    while c := template.read(1):
        read_so_far += c
        cols_since_newline += 1

        if c == newline_char:
            # newline = len(read_so_far)
            newlines_so_far += 1
            cols_since_newline = 0

        if active_escape is not None:
            if not read_so_far.endswith(active_escape.postfix):
                continue

            id: str = read_so_far[
                id_start : -len(active_escape.postfix)
            ].strip()

            # if active_escape.replace_line:
            #     cutoff_i: int = max(0, newline)
            # else:
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
            # if active_escape.insert_quotations:
            #     id_value = '"' + id_value + '"'

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

    # Remove template file.
    remove(path)

    # Write to new file.
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


def configure():
    """Configure this template project"""
    config = get_config()

    # Remove unnecessary files.
    shutil.rmtree(".git")
    remove(".gitattributes")
    remove("config.py")
    remove("LICENSE")
    remove("README.md")
    remove("template_config.ini")

    # Create a fresh git repository.
    cmd(["git", "init", "--initial-branch", "main"])

    # Unpack template files.
    for f in listdir("template_files"):
        shutil.move(join("template_files", f), f)
    shutil.rmtree("template_files")

    # Generate a LICENSE file if the selected license is 'Zlib'.
    if config["license"] == "Zlib":
        configure_template("LICENSE.tmpl", config)
    else:
        remove("LICENSE.tmpl")

    # Configure templates.
    configure_template(
        join("include", "cpp_template", "version.hpp.in.tmpl"),
        config,
    )
    configure_template(
        join("src", "version.cpp.tmpl"),
        config,
    )
    configure_template(
        join("src", "version.test.cpp.tmpl"),
        config,
    )
    configure_template("conanfile.py.tmpl", config)
    configure_template("meson.build.tmpl", config)
    configure_template(".gitignore.tmpl", config)
    configure_template("README.md.tmpl", config)
    configure_template(
        join("profiles", "default.profile.tmpl"),
        config,
    )
    configure_template(join("scripts", "clean.py.tmpl"), config)
    if config["package_type"] == "application":
        configure_template(
            join("src", "main.cpp.tmpl"),
            config,
        )
        shutil.move(join("include", "cpp_template", "version.hpp.in"), "src")
        shutil.rmtree("include")
        shutil.rmtree("test_package")
    else:
        remove(join("src", "main.cpp.tmpl"))
        configure_template(
            join("test_package", "conanfile.py.tmpl"),
            config,
        )
        configure_template(
            join("test_package", "src", "main.cpp.tmpl"),
            config,
        )
        rename(
            join("include", "cpp_template"),
            join("include", config["package_name"]),
        )


if __name__ == "__main__":
    configure()

"""Configure this template project"""

from ast import literal_eval
from configparser import ConfigParser
from dataclasses import dataclass
from os import system as os_system
from os import rename
from os import remove
from os.path import join as join_path
from os import listdir
import platform
from shutil import move
from shutil import rmtree
from typing import Dict, List, KeysView, Union, Callable, Any
from types import NoneType


def inline_print(return_val: Any, print_msg: str) -> Any:
    """Prints a given message and returns a given value."""
    return return_val


def system(cmd: str) -> None:
    """Executes a given command and prints a warning if it fails."""
    code: int = os_system(cmd)
    if code != 0:
        print("Warning: '" + cmd + "' failed with code " + str(code))


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
        configs["version_header_dir"] = "include/" + configs["package_name"]
    elif configs["package_type"] == "application":
        configs["version_header_dir"] = "src"

    return configs


@dataclass
class EscapeInfo:
    """Information relating to a specific identifier."""

    prefix: str
    postfix: str


def configure_template(
    path: str, new_path: str, config: Dict[str, str]
) -> None:
    """Insert configuration information into the provided template file."""

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
    template = open(new_path, mode="w", newline=newline_char)
    template.write(read_so_far)
    template.close()


def configure():
    """Configure this template project"""
    config = get_config()

    # Remove unnecessary files.
    rmtree(".git", ignore_errors=True)
    remove(".gitattributes")
    remove("config.py")
    remove("LICENSE")
    remove("README.md")
    remove("template_config.ini")

    # Create a fresh git repository.
    system("git init -b main")

    # Unpack template files.
    for f in listdir("template_files"):
        move(join_path("template_files", f), f)
    rmtree("template_files", ignore_errors=True)

    # Generate a LICENSE file if the selected license is 'Zlib'.
    if config["license"] == "Zlib":
        configure_template("LICENSE.tmpl", "LICENSE", config)
    else:
        remove("LICENSE.tmpl")

    # Configure templates.
    configure_template(
        join_path("include", "cpp_template", "version.hpp.in.tmpl"),
        join_path("include", "cpp_template", "version.hpp.in"),
        config,
    )
    configure_template(
        join_path("src", "version.cpp.tmpl"),
        join_path("src", "version.cpp"),
        config,
    )
    configure_template(
        join_path("src", "version.test.cpp.tmpl"),
        join_path("src", "version.test.cpp"),
        config,
    )
    configure_template("conanfile.py.tmpl", "conanfile.py", config)
    configure_template("meson.build.tmpl", "meson.build", config)
    configure_template(".gitignore.tmpl", ".gitignore", config)
    configure_template("README.md.tmpl", "README.md", config)
    configure_template(
        join_path("default.profile.tmpl"), join_path("default.profile"), config
    )
    if config["package_type"] == "application":
        configure_template(
            join_path("src", "main.cpp.tmpl"),
            join_path("src", "main.cpp"),
            config,
        )
        move(join_path("include", "cpp_template", "version.hpp.in"), "src")
        rmtree("include", ignore_errors=True)
        rmtree("test_package", ignore_errors=True)
    else:
        remove(join_path("src", "main.cpp.tmpl"))
        configure_template(
            join_path("test_package", "conanfile.py.tmpl"),
            join_path("test_package", "conanfile.py"),
            config,
        )
        configure_template(
            join_path("test_package", "src", "main.cpp.tmpl"),
            join_path("test_package", "src", "main.cpp"),
            config,
        )
        rename(
            join_path("include", "cpp_template"),
            join_path("include", config["package_name"]),
        )


if __name__ == "__main__":
    configure()

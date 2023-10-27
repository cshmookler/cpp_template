"""Configure a template project"""

from configparser import ConfigParser
from dataclasses import dataclass
from typing import Dict, List, KeysView, Union, Callable, Any
from types import NoneType
from ast import literal_eval
from shutil import move
from shutil import rmtree
from os import rename
from os import remove
from os.path import join as join_path


def inline_print(return_val: Any, print_msg: str) -> Any:
    """Prints a given message and returns a given value."""
    print(print_msg)
    return return_val


@dataclass
class ConfigInfo:
    """Information relating to a specific configuration."""
    default: str
    options: Callable[[str], bool] = lambda _: True


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


def assert_none_missing(expected: Union[List[str], KeysView[str]],
                        parsed: Union[List[str], KeysView[str]],
                        classify: str) -> None:
    """Ensure that all items in the expected list are in the parsed list."""
    missing_sections: List[str] = [k for k in expected if k not in parsed]
    if len(missing_sections) <= 0:
        return
    print("Error: The following " + classify + " were not found:")
    for k in missing_sections:
        print(k + " ", end="")
    print(end="\n")
    exit(1)


def get_config() -> Dict[str, str]:
    """Retrieve configuration information."""
    ini_file: str = "template_config.ini"
    section_name: str = "template_config"
    expected_configs: Dict[str, ConfigInfo] = {
        "package_name": ConfigInfo(default = "cpp_template", options = valid_identifier_name),
        "namespace": ConfigInfo(default = "tmpl", options = valid_identifier_name),
        "package_type": ConfigInfo(default = "application", options = lambda s: s in ["library", "application"]),
        "dependencies": ConfigInfo(default = "[]", options = valid_list),
        "author": ConfigInfo(default = ""),
        "license": ConfigInfo(default = ""),
        "url": ConfigInfo(default = ""),
        "description": ConfigInfo(default = ""),
        "topics": ConfigInfo(default = "[]", options = valid_list),
    }

    parser = ConfigParser()
    parser.read(ini_file)
    assert_none_missing([section_name], parser.sections(), "sections")
    parsed_configs = parser[section_name]
    assert_none_missing(expected_configs.keys(), parsed_configs.keys(), "keys")

    configs: Dict[str, str] = {}
    for k, v in expected_configs.items():
        pv: str = parsed_configs[k]
        configs[k] = pv if v.options(pv) else inline_print(v.default,
                "Warning: Invalid option '" + pv + "' for '" + k + "'. Using '"
                + v.default + "' instead.")

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


def setup_template(path: str, new_path: str, config: Dict[str, str]) -> None:
    """Insert configuration information into the provided template file."""

    newline_char: str = "\n"
    template = open(path, mode="r", newline=newline_char)
    escape_strings: List[EscapeInfo] = [
        EscapeInfo('___', '___'),
        EscapeInfo('"<<', '>>"'),
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
                    id_start:-len(active_escape.postfix)].strip()

            # if active_escape.replace_line:
            #     cutoff_i: int = max(0, newline)
            # else:
            cutoff_i: int = id_start-len(active_escape.prefix)

            if id not in config:
                raise RuntimeError("Unknown identifier '" + id + "' at line "
                        + str(newlines_so_far+1) + " column "
                        + str(cols_since_newline+1) + " in '" + path + "'")

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

    template = open(new_path, mode="w", newline=newline_char)
    template.write(read_so_far)
    template.close()


def configure():
    """Configure this template"""
    config = get_config()
    setup_template("conanfile.py.tmpl", "conanfile.py", config)
    setup_template("meson.build.tmpl", "meson.build", config)
    setup_template(
        join_path("include", "cpp_template", "version.hpp.in.tmpl"),
        join_path("include", "cpp_template", "version.hpp.in"),
        config)
    setup_template(
        join_path("src", "version.cpp.tmpl"),
        join_path("src", "version.cpp"),
        config)
    if config["package_type"] == "library":
        setup_template(
            join_path("test_package", "conanfile.py.tmpl"),
            join_path("test_package", "conanfile.py"),
            config)
        setup_template(
            join_path("test_package", "src", "main.cpp.tmpl"),
            join_path("test_package", "src", "main.cpp"),
            config)
        rename(
            join_path("include", "cpp_template"),
            join_path("include", config["package_name"]))
    elif config["package_type"] == "application":
        setup_template(
            join_path("src", "main.cpp.tmpl"),
            join_path("src", "main.cpp"),
            config)
        move(join_path("include", "cpp_template", "version.hpp.in"), "src")


def confirm():
    """Remove files related to configuration""" 
    config = get_config()
    remove("conanfile.py.tmpl")
    remove("meson.build.tmpl")
    remove(join_path("test_package", "conanfile.py.tmpl"))
    remove(join_path("include", config["package_name"], "version.hpp.in.tmpl"))
    remove(join_path("src", "version.cpp.tmpl"))
    remove(join_path("src", "main.cpp.tmpl"))
    remove(join_path("test_package", "src", "main.cpp.tmpl"))
    if config["package_type"] == "application":
        rmtree("include")
        rmtree("test_package")
    remove("template_config.ini")
    remove("config.py")
    remove("confirm.py")
    rmtree("__pycache__/")


if __name__ == "__main__":
    configure()

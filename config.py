"""Configure a template project"""

from configparser import ConfigParser
from dataclasses import dataclass
from typing import Dict, List, KeysView, Union
from types import NoneType
from os import rename
from os.path import join as join_path


@dataclass
class ConfigInfo:
    """Information relating to a specific configuration."""
    value: str = ""


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
    expected_configs: Dict[str, str] = {
        "package_name": "cpp_template",
        "package_type": "executable",
        "dependencies": "[]",
        "author": "",
        "license": "",
        "url": "",
        "description": "",
        "topics": "[]",
    }

    parser = ConfigParser()
    parser.read(ini_file)
    assert_none_missing([ section_name ], parser.sections(), "sections")
    parsed_configs = parser[section_name]
    assert_none_missing(expected_configs.keys(), parsed_configs.keys(), "keys")

    for k in expected_configs.keys():
        pv: str = parsed_configs[k]
        if pv != "" and pv != None:
            expected_configs[k] = pv

    return expected_configs


@dataclass
class EscapeInfo:
    """Information relating to a specific identifier."""
    prefix: str = '"{{'
    postfix: str = '}}"'
    replace_line: bool = False
    insert_quotations: bool = True


def setup_template(path: str, new_path: str, config: Dict[str, str]) -> None:
    """Insert configuration information into the provided template file."""

    newline_char: str = "\n"
    template = open(path, mode="r", newline=newline_char)
    escape_strings: List[EscapeInfo] = [
        EscapeInfo('"{{', '}}"'),
        EscapeInfo('"--', '--"', replace_line=True),
        EscapeInfo('____', '____', insert_quotations=False),
    ]

    active_escape: Union[EscapeInfo, NoneType] = None
    read_so_far: str = ""
    newline: int = 0
    id_start: int = 0

    while True:
        c: str = template.read(1)
        if not c:
            break

        read_so_far += c

        if c == newline_char:
            newline = len(read_so_far)

        if active_escape is not None:
            if not read_so_far.endswith(active_escape.postfix):
                continue

            id: str = read_so_far[
                    id_start:-len(active_escape.postfix)].strip()

            if active_escape.replace_line:
                cutoff_i: int = max(0, newline)
            else:
                cutoff_i: int = id_start-len(active_escape.prefix)

            if id not in config:
                raise RuntimeError("Error: Unknown identifier '"
                        + id + "' in '" + path + "'")

            id_value: str = config[id]
            if active_escape.insert_quotations:
                id_value = '"' + id_value + '"'

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


if __name__ == "__main__":
    config = get_config()
    setup_template("conanfile.py.tmpl", "conanfile.py", config)
    setup_template(
        join_path("test_package", "conanfile.py.tmpl"),
        join_path("test_package", "conanfile.py"),
        config)
    setup_template(
        join_path("include", "cpp_template", "version.hpp.in.tmpl"),
        join_path("include", "cpp_template", "version.hpp.in"),
        config)
    setup_template(
        join_path("src", "version.cpp.tmpl"),
        join_path("src", "version.cpp"),
        config)
    setup_template(
        join_path("test_package", "src", "main.cpp.tmpl"),
        join_path("test_package", "src", "main.cpp"),
        config)
    rename(
        join_path("include", "cpp_template"),
        join_path("include", config["package_name"]))


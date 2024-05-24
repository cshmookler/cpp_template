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
        "package_type": ConfigInfo(
            default="application",
            constraint=lambda s: s
            in [
                "application",
                "library",
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

    # Add options that are derived from others.
    configs["version_header_dir"] = (
        "src"
        if configs["package_type"] == "application"
        else configs["package_name"]
    )

    return configs


@dataclass
class EscapeSequence:
    """An escape sequence consisting of a specific prefix and postfix that are unlikely to naturally occur in a file"""

    prefix: str
    postfix: str


class InvalidTemplateFile(Exception):
    """Exception thrown when a template file does not have the correct file extension"""

    def __init__(self, message: str) -> None:
        self.message = message


class TemplateParsingError(Exception):
    """Exception thrown when an error occurs during template parsing"""

    def __init__(self, message: str) -> None:
        self.message = message


def configure_template(path: str, config: Dict[str, str]) -> None:
    """Insert configuration information into the provided template file."""
    # Verify that the template has the correct file extension.
    template_file_extension = ".tmpl"
    if not path.endswith(template_file_extension):
        raise InvalidTemplateFile(
            "Template files must have a template file extension ("
            + template_file_extension
            + ")"
        )

    # A list of escape sequences to search for in the file.
    escape_strings: List[EscapeSequence] = [
        EscapeSequence("___", "___"),
        EscapeSequence('["<<', '>>"]'),
    ]

    # The newline character.
    newline_char: str = "\n"

    # The escape sequence currently being read.
    active_escape: Union[EscapeSequence, NoneType] = None

    # The entire file that has so far been read.
    read_so_far: str = ""

    # The number of characters encountered since the last newline.
    cols_since_newline = 0

    # The number of newlines encountered so far in the file.
    newlines_so_far: int = 0

    # The index of the beginning of an identifier enclosed within the current escape sequence.
    id_start: int = 0

    # Open the template file in read mode.
    template = open(path, mode="r", newline=newline_char)

    # Read the entire template file one character at a time.
    c: str
    while c := template.read(1):
        # Keep track of everything read so far for extracting identifier names.
        read_so_far += c

        # Keep track of line and column numbers for constructing helpful error messages.
        cols_since_newline += 1
        if c == newline_char:
            newlines_so_far += 1
            cols_since_newline = 0

        if active_escape is None:
            # Search for an escape sequence prefix.
            e: EscapeSequence
            for e in escape_strings:
                if read_so_far.endswith(e.prefix):
                    active_escape = e
                    id_start = len(read_so_far)
                    break
            continue

        # The prefix of an escape sequence was found, so search for its postfix.
        if not read_so_far.endswith(active_escape.postfix):
            continue

        # Extract the identifier name once the escape sequence postifx is found.
        id: str = read_so_far[id_start : -len(active_escape.postfix)].strip()

        if id not in config:
            raise TemplateParsingError(
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

        # Insert the cooresponding configuration value into the text.
        id_value: str = config[id]
        cutoff_i: int = id_start - len(active_escape.prefix)
        read_so_far = read_so_far[:cutoff_i] + id_value

        # Finished reading the escape sequence. Begin searching for another.
        active_escape = None

    # Incomplete escape sequences are not allowed.
    if active_escape is not None:
        raise TemplateParsingError("EOF encountered while reading identifier")

    # Close and delete the original template file.
    template.close()
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
    configure_template(join(this_dir, "meson.build.tmpl"), config)
    configure_template(join(this_dir, ".gitignore.tmpl"), config)
    configure_template(join(this_dir, "README.md.tmpl"), config)
    if config["package_type"] == "library":
        # Configure this project as a library
        configure_template(join(this_dir, "conanfile-lib.py.tmpl"), config)
        rename(
            join(this_dir, "conanfile-lib.py"), join(this_dir, "conanfile.py")
        )
        remove(join(this_dir, "conanfile-app.py.tmpl"))
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
    else:
        # Configure this project as an application
        configure_template(join(this_dir, "conanfile-app.py.tmpl"), config)
        rename(
            join(this_dir, "conanfile-app.py"), join(this_dir, "conanfile.py")
        )
        remove(join(this_dir, "conanfile-lib.py.tmpl"))
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

    # Declare binaries
    binary_config_module = import_module("update_deps")
    binaries = binary_config_module.Binaries(
        [
            binary_config_module.Binary(
                name=config["package_name"],
                bin_type=config["package_type"],
                dependencies=[
                    binary_config_module.Dependency(
                        name=dep.rsplit("/", 1)[0],
                        version=dep.rsplit("/", 1)[1],
                        enabled=True,
                        link_preference=False,
                        dynamic=True,
                        components=[],
                    )
                    for dep in literal_eval(config["dependencies"])
                ],
                sources=[["src", "version.cpp"]],
                main=(
                    []
                    if config["package_type"] == "library"
                    else ["src", "main.cpp"]
                ),
            ),
            binary_config_module.Binary(
                name="version",
                bin_type="test",
                dependencies=[
                    binary_config_module.Dependency(
                        name="gtest",
                        version="1.14.0",
                        enabled=True,
                        link_preference=False,
                        dynamic=True,
                        components=[],
                    )
                ],
                sources=[["src", "version.test.cpp"], ["src", "version.cpp"]],
                main=[],
            ),
        ]
    )
    binaries.write()

    # Remove this configuration script and the cooresponding .ini file once all previous operations have succeeded.
    remove(join(this_dir, "config.py"))
    remove(join(this_dir, "template_config.ini"))


if __name__ == "__main__":
    configure()

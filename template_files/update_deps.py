"""Manage dependencies"""

from configparser import ConfigParser, SectionProxy
from dataclasses import dataclass
from importlib import import_module
import os
import subprocess
from typing import List


@dataclass
class Dependency:
    """Dependency information"""

    name: str
    version: str
    status: bool


class Dependencies:
    """Dependency information for the dependency configuration file"""

    def __init__(
        self,
        file_path: str,
        explicit: List[Dependency] = [],
        implicit: List[Dependency] = [],
    ) -> None:
        self.file_path = file_path
        self.explicit = explicit
        self.implicit = implicit

    def file_exists(self) -> bool:
        """Returns true if the dependency configuration file exists and false otherwise"""
        return os.path.isfile(self.file_path)

    @staticmethod
    def _read_section(section: SectionProxy) -> List[Dependency]:
        """Reads a specific section of the dependency configuration file"""
        deps: List[Dependency] = []
        for dep in section:
            name, version = dep.rsplit("/", 1)
            status = section[dep] == "yes"
            deps.append(Dependency(name, version, status))
        return deps

    def read(self) -> None:
        """Reads dependency information from the dependency configuration file"""
        parser = ConfigParser()
        parser.read(self.file_path)
        self.explicit = Dependencies._read_section(parser["explicit"])
        self.implicit = Dependencies._read_section(parser["implicit"])

    @staticmethod
    def _write_section(section: SectionProxy, deps: List[Dependency]) -> None:
        """Write dependency information to a specific section"""
        for dep in deps:
            key = dep.name + "/" + dep.version
            value = "yes" if dep.status else "no"
            section[key] = value

    def write(self) -> None:
        """Write dependency information to the dependency configuration file"""
        parser = ConfigParser()
        parser.add_section("explicit")
        parser.add_section("implicit")

        Dependencies._write_section(parser["explicit"], self.explicit)
        Dependencies._write_section(parser["implicit"], self.implicit)

        with open(self.file_path, "w") as config_file:
            config_file.write(
                "# Find explicit dependencies at https://conan.io/center\n"
                "# Implicit dependencies are identified during the build process\n\n"
            )
            parser.write(config_file, space_around_delimiters=True)


if __name__ == "__main__":
    build = import_module("build")
    profile = import_module("profile")
    build.build(
        profile.get_profile(), ["--options:all", "quit_after_generate=True"]
    )

"""Process template files with Jinja"""

import json
import os
from sys import argv
from typing import Dict

from jinja2 import Environment, FileSystemLoader


this_dir: str = os.path.dirname(__file__)
template_file_extension: str = ".tmpl"


class InvalidTemplateFile(Exception):
    """Exception thrown when a template file does not have the correct file extension"""

    def __init__(self, message: str) -> None:
        self.message = message


class TemplateConfigurer:
    """Uses Jinja to render template files in the same directory as this script"""

    def __init__(self, config: Dict[str, str]):
        self.env = Environment(
            loader=FileSystemLoader(searchpath=this_dir),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False,
        )
        self.config = config

    def configure(self, path: str) -> None:
        """Uses Jinja to render a template file and replace the original on the filesystem"""
        # Verify that the template has the correct file extension.
        if not path.endswith(template_file_extension):
            raise InvalidTemplateFile(
                "Template files must have a template file extension ("
                + template_file_extension
                + ")"
            )

        # Render the template and save it to the filesystem
        template = self.env.get_template(path)
        with open(
            os.path.join(this_dir, path.removesuffix(template_file_extension)),
            "w",
        ) as configured:
            configured.write(template.render(self.config))

        # Remove the original template file
        os.remove(os.path.join(this_dir, path))


if __name__ == "__main__":
    if len(argv) < 2:
        raise RuntimeError(
            "Not enough arguments. Execute the 'config.py' script instead."
        )

    # Get the configuration information.
    config = json.loads(argv[1])

    # Initialize the template engine.
    templater = TemplateConfigurer(config)

    # Generate a LICENSE file if the selected license is 'Zlib'.
    if config["license"] == "Zlib":
        templater.configure("LICENSE.tmpl")
    else:
        os.remove(os.path.join(this_dir, "LICENSE.tmpl"))

    # Configure C++ source file templates.
    templater.configure(os.path.join("include", "version.hpp.in.tmpl"))
    templater.configure(os.path.join("src", "version.cpp.tmpl"))
    templater.configure(os.path.join("tests", "version.test.cpp.tmpl"))

    # Configure build-related templates.
    if config["conan"] == "true":
        templater.configure("conanfile.py.tmpl")
    templater.configure("meson.build.tmpl")

    # Configure script templates.
    if config["conan"] == "true":
        templater.configure("clean.py.tmpl")

    # Configure miscellaneous templates.
    templater.configure(".gitignore.tmpl")
    templater.configure("README.md.tmpl")

    # Perform operations dependent on the package type.
    if config["package_type"] == "library":
        if config["conan"] == "true":
            templater.configure(os.path.join("test_package", "conanfile.py.tmpl"))
            templater.configure(os.path.join("test_package", "src", "main.cpp.tmpl"))
    else:
        templater.configure(os.path.join("src", "main.cpp.tmpl"))

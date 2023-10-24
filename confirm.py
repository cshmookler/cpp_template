"""Remove files related to configuration"""

from os import remove
from os.path import join as join_path
from shutil import rmtree

from config import get_config


if __name__ == "__main__":
    config = get_config()
    remove("conanfile.py.tmpl")
    remove(join_path("test_package", "conanfile.py.tmpl"))
    remove(join_path("include", config["package_name"], "version.hpp.in.tmpl"))
    remove(join_path("src", "version.cpp.tmpl"))
    remove(join_path("test_package", "src", "main.cpp.tmpl"))
    remove("template_config.ini")
    remove("config.py")
    remove("confirm.py")
    rmtree("__pycache__/")


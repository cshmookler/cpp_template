"""Install this library using Conan so other projects can use it"""

from importlib import import_module
from sys import argv


if __name__ == "__main__":
    profiles = import_module("profiles")
    build = import_module("build")
    build.conan("install", profiles.get_profiles_abs_paths(), list(argv)[1:])

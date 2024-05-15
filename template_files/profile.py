"""Set the Conan profile for this project"""

from configparser import ConfigParser
from importlib import import_module
import os
from sys import argv as args


config_path: str = os.path.join(os.path.dirname(__file__), "profile.ini")
default_profile: str = "default.profile"


def abs_path_to_profile(relative_path: str) -> str:
    """Determines the absolute path to the given profile relative to the profile directory"""
    return os.path.join(os.path.dirname(__file__), "profiles", relative_path)


def set_profile(profile: str) -> None:
    """Set the path to the active Conan profile"""
    parser = ConfigParser()
    parser.add_section("profile")
    parser["profile"]["profile"] = profile
    with open(config_path, "w") as ini_file:
        parser.write(ini_file, space_around_delimiters=True)


def get_profile() -> str:
    """Get the path to the active Conan profile"""
    parser = ConfigParser()
    parser.read(config_path)
    if parser.has_option("profile", "profile"):
        profile = parser["profile"]["profile"]
    else:
        set_profile(default_profile)
        profile = default_profile
    return abs_path_to_profile(profile)


def generate_default() -> None:
    """Use Conan to automatically generate the default profile"""
    """This method requires the Conan API"""
    with open(abs_path_to_profile(default_profile), "w") as profile:
        profile.write(
            import_module("conan.api.conan_api").ProfilesAPI.detect().dumps()
        )


if __name__ == "__main__":
    """Set the path to the active Conan profile and display the change"""
    old_profile: str = get_profile()
    new_profile: str = default_profile if len(args) <= 1 else args[1]
    set_profile(new_profile)
    print(old_profile + " -> " + get_profile())

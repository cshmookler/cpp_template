"""Set the Conan profile for this project"""

from configparser import ConfigParser
import os
from sys import argv as args


config_path: str = os.path.join(os.path.dirname(__file__), "profile.ini")
default_profile: str = os.path.join("default.profile")


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
    return os.path.join(os.path.dirname(__file__), "profiles", profile)


if __name__ == "__main__":
    """Set the path to the active Conan profile and display the change"""
    old_profile: str = get_profile()
    new_profile: str = default_profile if len(args) <= 1 else args[1]
    set_profile(new_profile)
    print(old_profile + " -> " + get_profile())

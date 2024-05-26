"""Set the Conan profile for this project"""

from configparser import ConfigParser
from importlib import import_module
import os
import subprocess
from sys import argv as args


config_path: str = os.path.join(os.path.dirname(__file__), "profile.ini")
profile_dir: str = os.path.join(os.path.dirname(__file__), "profiles")
default_profile: str = "default.profile"


def abs_path_to_profile(relative_path: str) -> str:
    """Determines the absolute path to the given profile relative to the profile directory"""
    return os.path.join(profile_dir, relative_path)


def set_profile(profile: str) -> None:
    """Set the path to the active Conan profile"""
    parser = ConfigParser()
    parser.add_section("profile")
    parser["profile"]["profile"] = profile
    with open(config_path, "w") as ini_file:
        parser.write(ini_file, space_around_delimiters=True)


def generate_default() -> None:
    """Use Conan to automatically generate the default profile"""
    venv_module = import_module("this_venv")
    if not venv_module.exists():
        venv_module.create()
    if not os.path.isdir(profile_dir):
        os.mkdir(profile_dir)
    subprocess.run(
        [
            venv_module.python(),
            "-c",
            "from importlib import import_module\n"
            "with open('"
            + abs_path_to_profile(default_profile)
            + "', 'w') as profile:\n"
            "    profile.write(\n"
            "        import_module('conan.api.conan_api').ProfilesAPI.detect().dumps()\n"
            "    )\n",
        ]
    )


def get_profile() -> str:
    """Get the path to the active Conan profile"""
    parser = ConfigParser()
    parser.read(config_path)
    if parser.has_option("profile", "profile"):
        profile = abs_path_to_profile(parser["profile"]["profile"])
        if os.path.isfile(profile):
            return profile

    # Use the default profile if the configuration file is invalid or the profile does not exist.
    set_profile(default_profile)
    if not os.path.isfile(abs_path_to_profile(default_profile)):
        generate_default()
    return abs_path_to_profile(default_profile)


if __name__ == "__main__":
    """Set the path to the active Conan profile and display the change"""
    old_profile: str = get_profile()
    new_profile: str = default_profile if len(args) <= 1 else args[1]
    set_profile(new_profile)
    print(old_profile + " -> " + get_profile())

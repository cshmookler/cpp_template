"""Set the Conan profile for this project"""

from argparse import ArgumentParser, Namespace
from configparser import ConfigParser
from dataclasses import dataclass
from importlib import import_module
import os
import subprocess


profile_dir: str = os.path.join(os.path.dirname(__file__), "profiles")
config_path: str = os.path.join(os.path.dirname(__file__), "profiles.ini")
default_profile: str = "default.profile"
profile_section: str = "profiles"
profile_build_type: str = "build"
profile_host_type: str = "host"


@dataclass
class Profiles:
    host: str
    build: str


def abs_path_to_profile(relative_path: str) -> str:
    """Determines the absolute path to the given profile relative to the profile directory"""
    return os.path.join(profile_dir, relative_path)


def set_profiles(profiles: Profiles) -> None:
    """Set the active Conan profile for a given type ('host' or 'build')"""
    parser = ConfigParser()
    parser.add_section(profile_section)
    parser[profile_section][profile_build_type] = profiles.build
    parser[profile_section][profile_host_type] = profiles.host
    parser.write(open(config_path, "w"), space_around_delimiters=True)


def _get_profile(parser: ConfigParser, profile_type: str) -> str:
    """Get the path to one of the active Conan profiles"""
    if parser.has_option(profile_section, profile_type):
        profile = abs_path_to_profile(parser[profile_section][profile_type])
        if os.path.isfile(profile):
            return profile

    # Use the default profile if the configuration file is invalid or the profile does not exist.
    # NOTE: The updated profile is not written to the configuration file.
    if not os.path.isfile(abs_path_to_profile(default_profile)):
        generate_default()
    return abs_path_to_profile(default_profile)


def get_profiles() -> Profiles:
    """Get the paths to the active Conan host and build profiles"""
    # Read the existing profile paths listed in the configuration file
    parser = ConfigParser()
    parser.read(config_path)

    # Verify that the existing profile paths are valid. If either are invalid, replace them with the default profile.
    profiles = Profiles(
        host=_get_profile(parser, profile_host_type),
        build=_get_profile(parser, profile_build_type),
    )

    # Ensure that the configuration file is updated if changes were made to the profile paths.
    set_profiles(profiles)

    return profiles


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
            "with open(r'"
            + abs_path_to_profile(default_profile)
            + "', 'w') as profile:\n"
            "    profile.write(\n"
            "        import_module('conan.api.conan_api').ProfilesAPI.detect().dumps()\n"
            "    )\n",
        ],
        check=True,
    )


if __name__ == "__main__":
    """Set the path to the active Conan profile and display the change"""
    # Setup the command line argument parser
    arg_parser = ArgumentParser(
        prog="python profiles.py",
        description="This script manages Conan profiles for this project. When run, this script verifies the existence of the active Conan profiles and writes the paths of the build and host profiles to standard out. If an active Conan profile does not exist on the file system or its entry in the configuration file is invalid, then it is replaced with the default profile. The default profile is automatically generated if it is an active profile but does not exist on the file system.",
        epilog="Refer to the official Conan documentation for help with writing profiles (https://docs.conan.io/2/reference/config_files/profiles.html).",
    )
    arg_parser.add_argument(
        "--build", help="set the active Conan build profile"
    )
    arg_parser.add_argument("--host", help="set the active Conan host profile")

    # Parse command line arguments.
    args: Namespace = arg_parser.parse_args()

    # Read the current profile configuration from the configuration file.
    profiles: Profiles = get_profiles()

    # Set the build or host profiles if given as command line arguments.
    if args.build != None:
        profiles.build = args.build
    if args.host != None:
        profiles.host = args.host

    # Save the updated profile configuration to the configuration file.
    set_profiles(profiles)

    # Read the updated profile configuration from the configuration file.
    # If either of the active profiles are invalid, they are replaced with the default profile.
    profiles = get_profiles()

    # Write the paths to the host and build profiles to standard out.
    print("build: " + profiles.build + "\n" + "host: " + profiles.host)

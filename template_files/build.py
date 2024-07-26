"""Build this project using Conan"""

from importlib import import_module
import os
import subprocess
from sys import argv
from typing import List


this_dir: str = os.path.dirname(__file__)


def conan(command: str, profiles, extra_args: List[str] = []) -> None:
    """Execute Conan with the given command, profiles, and extra arguments"""
    venv = import_module("this_venv")
    if not venv.exists():
        venv.create()
    subprocess.run(
        [
            venv.conan(),
            command,
            "--build=missing",
            "--profile:build",
            profiles.build,
            "--profile:host",
            profiles.host,
            "--conf:host",
            "tools.system.package_manager:mode=install",
            "--conf:host",
            "tools.system.package_manager:sudo=True",
            this_dir,
        ]
        + extra_args,
        check=True,
    )


if __name__ == "__main__":
    profiles = import_module("profiles")
    conan("build", profiles.get_profiles(), list(argv)[1:])

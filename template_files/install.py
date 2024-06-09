"""Install this library using Conan so other projects can use it"""

from importlib import import_module
import os
import subprocess
from sys import argv
from typing import List


this_dir: str = os.path.dirname(__file__)


def install(profiles, extra_args: List[str] = []) -> None:
    """Install this project using Conan"""
    venv = import_module("this_venv")
    if not venv.exists():
        venv.create()
    subprocess.run(
        [
            venv.conan(),
            "create",
            "--build=missing",
            "--profile:build",
            profiles.build,
            "--profile:host",
            profiles.host,
            "--conf:host",
            "tools.system.package_manager:mode=install",
            "--conf:host",
            "tools.system.package_manager:sudo=True",
            os.path.dirname(__file__),
        ]
        + extra_args,
        check=True,
    )


if __name__ == "__main__":
    profiles = import_module("profiles")
    install(profiles.get_profiles(), list(argv)[1:])

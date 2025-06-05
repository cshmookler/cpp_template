"""Build this project using Conan"""

import os
import subprocess
from importlib import import_module
from sys import argv
from typing import List


this_dir: str = os.path.dirname(__file__)


def conan(command: str, profiles_abs_paths, extra_args: List[str] = []) -> None:
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
            profiles_abs_paths.build,
            "--profile:host",
            profiles_abs_paths.host,
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
    conan("build", profiles.get_profiles_abs_paths(), list(argv)[1:])

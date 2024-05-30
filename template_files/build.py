"""Build this project using Conan"""

from importlib import import_module
import os
import subprocess
from typing import List


this_dir: str = os.path.dirname(__file__)


def build(profiles, extra_args: List[str] = []) -> None:
    """Build this project using Conan"""
    venv = import_module("this_venv")
    if not venv.exists():
        venv.create()
    subprocess.run(
        [
            venv.conan(),
            "build",
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
    build(profiles.get_profiles())

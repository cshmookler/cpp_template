"""Build this project"""

import os
import subprocess
from sys import argv as args
import this_venv as venv


def build(profile: str) -> None:
    """Build this project"""
    if not venv.exists():
        venv.create()
    subprocess.run(
        [
            venv.conan,
            "build",
            "--build=missing",
            "--profile:all",
            profile,
            "--conf:host",
            "tools.system.package_manager:mode=install",
            "--conf:host",
            "tools.system.package_manager:sudo=True",
            os.curdir,
        ]
    )


if __name__ == "__main__":
    build(
        os.path.join("profiles", "default.profile")
        if len(args) <= 1
        else args[0]
    )

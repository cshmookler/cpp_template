"""Build this project using Conan"""

from importlib import import_module
import os
import subprocess


def build(profile: str) -> None:
    """Build this project using Conan"""
    venv = import_module("this_venv")
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
    profile = import_module("profile")
    build(profile.get_profile())

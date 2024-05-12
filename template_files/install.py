"""Install this library using Conan so other projects can use it"""

from importlib import import_module
import os
import subprocess


this_dir: str = os.path.dirname(__file__)


def install(profile: str) -> None:
    """Install this project using Conan"""
    venv = import_module("this_venv")
    if not venv.exists():
        venv.create()
    subprocess.run(
        [
            venv.conan,
            "create",
            "--build=missing",
            "--profile:all",
            profile,
            "--conf:host",
            "tools.system.package_manager:mode=install",
            "--conf:host",
            "tools.system.package_manager:sudo=True",
            os.path.dirname(__file__),
        ]
    )


if __name__ == "__main__":
    profile = import_module("profile")
    install(profile.get_profile())

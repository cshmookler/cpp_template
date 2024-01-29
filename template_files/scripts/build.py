"""Build this project"""

import os
import subprocess
from . import this_venv as venv


def build() -> None:
    """Build this project"""
    if not venv.exists():
        venv.create()
    subprocess.run(
        [
            venv.conan,
            "build",
            "--build=missing",
            "--profile:all",
            os.path.join("profiles", "default.profile"),
            "--conf:host",
            "tools.system.package_manager:mode=install",
            "--conf:host",
            "tools.system.package_manager:sudo=True",
            os.curdir,
        ]
    )


if __name__ == "__main__":
    build()

"""Build this project"""

import os
import subprocess
from venv import EnvBuilder


def venv_gen(path: str) -> None:
    """Create a Python virtual environment and install conan 2.x"""
    print(
        "Creating virtual environment: "
        + os.linesep
        + os.path.join(os.path.abspath(os.curdir), path)
    )
    venv = EnvBuilder(with_pip=True)
    venv.create(path)
    pip = os.path.join(path, "bin", "pip")
    subprocess.call([pip, "install", "conan>=2.0.0"])


def build() -> None:
    """Build this project"""
    venv_path = ".venv"
    if not os.path.isdir(venv_path):
        venv_gen(venv_path)
    conan = os.path.join(venv_path, "bin", "conan")
    subprocess.call(
        [
            conan,
            "build",
            "--build=missing",
            "--profile:all",
            "default.profile",
            os.curdir,
        ]
    )


if __name__ == "__main__":
    build()

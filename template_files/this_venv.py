"""Create a Python virtual environment and install Conan 2.x"""

import os
import shutil
import subprocess
from venv import EnvBuilder


path: str = os.path.join(os.path.dirname(__file__), ".venv")
python: str = os.path.join(path, "bin", "python")
pip: str = os.path.join(path, "bin", "pip")
conan: str = os.path.join(path, "bin", "conan")


def create() -> None:
    """Create a Python virtual environment and install Conan 2.x"""
    if os.path.isdir(path):
        shutil.rmtree(path)
    print(
        "Creating virtual environment in "
        + os.path.join(os.path.abspath(os.curdir), path)
    )
    venv = EnvBuilder(with_pip=True)
    venv.create(path)
    subprocess.run([pip, "install", "conan>=2.0.0"])


def exists() -> bool:
    """Return true if the virtual environment exists and contains critical files. Return false otherwise"""
    return (
        os.path.isdir(path)
        and os.path.isfile(python)
        and os.path.isfile(pip)
        and os.path.isfile(conan)
    )


if __name__ == "__main__":
    if not exists():
        create()

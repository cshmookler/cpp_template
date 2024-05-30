"""Python virtual environment management"""

import os
import shutil
import subprocess
from types import SimpleNamespace
from typing import List
from venv import EnvBuilder


name: str = ".venv"


def _abs_path(path: str):
    """Returns the absolute form of the given path relative to the directory containing this file"""
    return os.path.join(os.path.dirname(__file__), path)


def path() -> str:
    """Returns the absolute path to this virtual environment"""
    return _abs_path(name)


def _context() -> SimpleNamespace:
    """Returns context information related to this virtual environment"""
    venv = EnvBuilder(with_pip=True)
    return venv.ensure_directories(path())


def python() -> str:
    """Returns the absolute path to the python executable within this virtual environment"""
    return _abs_path(_context().env_exe)


def _exe_path(name_without_extension: str) -> str:
    """Returns the absolute path to a given executable within this virtual environment"""
    bin_path, python_path = os.path.split(python())
    python_split_by_extension: List[str] = python_path.split(".", 1)
    exe_extension: str = (
        "." + python_split_by_extension[1]
        if len(python_split_by_extension) > 1
        else ""
    )
    return os.path.join(bin_path, name_without_extension + exe_extension)


def pip() -> str:
    """Returns the absolute path to the pip executable within this virtual environment"""
    return _exe_path("pip")


def conan() -> str:
    """Returns the absolute path to the conan executable within this virtual environment"""
    return _exe_path("conan")


def create() -> None:
    """Create a Python virtual environment and install Conan"""
    if os.path.isdir(path()):
        shutil.rmtree(path())
    print("Creating virtual environment in " + path())
    venv = EnvBuilder(with_pip=True)
    venv.create(path())
    subprocess.run([pip(), "install", "conan>=2.3.0"], check=True)


def exists() -> bool:
    """Return true if the virtual environment exists and contains critical files. Return false otherwise"""
    return (
        os.path.isdir(path())
        and os.path.isfile(python())
        and os.path.isfile(pip())
        and os.path.isfile(conan())
    )


if __name__ == "__main__":
    if not exists():
        create()

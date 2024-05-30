"""Clear the Conan cache"""

import subprocess
from importlib import import_module


def clear_cache() -> None:
    """Clear the Conan cache"""
    venv = import_module("this_venv")
    if not venv.exists():
        venv.create()
    subprocess.run([venv.conan(), "remove", "--confirm", "*"], check=True)


if __name__ == "__main__":
    clear_cache()

"""Clear the Conan cache"""

import os
import subprocess
import this_venv as venv


def clear_cache() -> None:
    """Clear the Conan cache"""
    if not venv.exists():
        venv.create()
    subprocess.run([venv.conan, "remove", "--confirm", "*"])


if __name__ == "__main__":
    clear_cache()

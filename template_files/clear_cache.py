"""Clear the Conan cache"""

from subprocess import run


if __name__ == "__main__":
    run(["python3", "-m", "scripts.clear_cache"])

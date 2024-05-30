"""Test this template project"""

import os
import shutil
import stat
import subprocess
from typing import List
import colorama


this_dir: str = os.path.dirname(__file__)
root_dir: str = os.path.abspath(os.path.join(this_dir, os.path.pardir))


def _shutil_onerror(func, path, exc_info) -> None:
    """On access error, add write permissions and try again"""
    if os.access(path, os.W_OK):
        raise
    os.chmod(path, stat.S_IWUSR)
    func(path)


class Tester:
    """Tester class for this template project"""

    def __init__(self, name: str):
        print(name + ":")

        self.root_dir = os.path.join(this_dir, name)
        self.test_dir = os.path.join(self.root_dir, "files")
        self.log_dir = os.path.join(self.root_dir, "logs")

        self._prepare()

    def _prepare(self) -> None:
        """Prepare a fresh copy of this template project for the test"""

        # Remove the root directory for this test if it already exists
        if os.path.exists(self.root_dir):
            shutil.rmtree(
                self.root_dir, onerror=_shutil_onerror, ignore_errors=True
            )

        # Create directories
        os.mkdir(self.root_dir)
        os.mkdir(self.test_dir)
        os.mkdir(self.log_dir)

        # Copy all template files to the test directory
        for file_name in os.listdir(root_dir):
            file_abs_path = os.path.join(root_dir, file_name)

            # Do not copy the 'tests' directory
            if file_abs_path == this_dir:
                # Create a placeholder 'tests' directory in the test directory
                os.mkdir(os.path.join(self.test_dir, file_name))
                continue

            if os.path.isdir(file_abs_path):
                shutil.copytree(
                    file_abs_path, os.path.join(self.test_dir, file_name)
                )
            else:
                shutil.copy(
                    file_abs_path, os.path.join(self.test_dir, file_name)
                )

    def run(self, log_file: str, script: str, *args: str) -> bool:
        """Execute a given python script in the test directory and append output to a given log file in the log directory"""
        cmd: List[str] = [
            "python",
            os.path.join(self.test_dir, script),
        ] + list(args)

        print("    executing script '" + log_file + "':\n        ", end="")
        for arg in cmd:
            print(arg + " ", end="")
        print("\n", end="")

        log_path = os.path.join(self.log_dir, log_file)
        with open(log_path, "a+") as log:
            status = subprocess.run(cmd, stdout=log, stderr=log).returncode

        success: bool = status == 0

        if success:
            print(
                "        "
                + colorama.Fore.GREEN
                + "success"
                + colorama.Fore.RESET
            )
        else:
            print(
                "        "
                + colorama.Fore.RED
                + "failure"
                + colorama.Fore.RESET
                + " (return code: "
                + str(status)
                + ")"
            )

        return success


if __name__ == "__main__":
    colorama.init()

    tester = Tester("test_default_application")

    if not tester.run("config", "config.py"):
        exit(1)
    if not tester.run("clear_cache", "clear_cache.py"):
        exit(1)
    if not tester.run("first_build", "build.py"):
        exit(1)
    if not tester.run("clean", "clean.py"):
        exit(1)
    if not tester.run("second_build", "build.py"):
        exit(1)

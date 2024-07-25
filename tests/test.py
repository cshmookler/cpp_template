"""Test this template project"""

import os
import shutil
import stat
import subprocess
from sys import argv
from typing import List


this_dir: str = os.path.dirname(__file__)
root_dir: str = os.path.abspath(os.path.join(this_dir, os.path.pardir))


def _shutil_onerror(func, path, exc_info) -> None:
    """On access error, add write permissions and try again"""

    if os.access(path, os.W_OK):
        raise
    os.chmod(path, stat.S_IWUSR)
    func(path)


def rmtree(dir_path: str) -> None:
    """Recursively delete a given directory with shutil.rmtree while ignoring all errors"""

    shutil.rmtree(dir_path, onerror=_shutil_onerror, ignore_errors=True)


class Test:
    """Testing class for this template project"""

    def __init__(
        self,
        test_dir: str,
        expect_failure: bool = False,
        prepare: bool = True,
    ):
        self.test_dir = test_dir
        self.files_dir = os.path.join(self.test_dir, "files")
        self.log_dir = os.path.join(self.test_dir, "logs")
        self._pycache_dir = os.path.join(self.test_dir, "__pycache__")

        self.expect_failure = expect_failure

        if prepare:
            print(os.path.basename(test_dir))
            self.clean()
            self.setup()

    def clean(self) -> None:
        """Remove old files from a previous test"""

        rmtree(self.files_dir)
        rmtree(self.log_dir)
        rmtree(self._pycache_dir)

    def setup(self) -> None:
        """Prepare a fresh copy of this template project in the 'files' directory"""

        # Create directories
        os.mkdir(self.files_dir)
        os.mkdir(self.log_dir)

        # Copy all template files to the 'files' directory
        for file_name in os.listdir(root_dir):
            file_abs_path = os.path.join(root_dir, file_name)

            # Do not copy the 'tests' directory
            if file_abs_path == this_dir:
                # Create a placeholder 'tests' directory in the test directory
                os.mkdir(os.path.join(self.files_dir, file_name))
                continue

            if os.path.isdir(file_abs_path):
                shutil.copytree(
                    file_abs_path,
                    os.path.join(self.files_dir, file_name),
                    symlinks=True,
                )
            else:
                shutil.copy(
                    file_abs_path,
                    os.path.join(self.files_dir, file_name),
                    follow_symlinks=False,
                )

    def call(self, log_file: str, cmd: List[str] = []) -> None:
        """Execute a given program with the given arguments in the 'files' directory and append output to a given log file in the 'log' directory"""

        # Write the command to stdout for debug purposes
        print("    " + log_file + "\n        ", end="")
        for arg in cmd:
            print(arg + " ", end="")
        print("\n", end="")

        # Execute the command and write output to the log file
        log_path = os.path.join(self.log_dir, log_file)
        with open(log_path, "a+") as log:
            returncode: int = subprocess.run(
                cmd, stdout=log, stderr=log
            ).returncode

            if bool(returncode != 0) ^ bool(self.expect_failure):
                exit(1)

    def run(self, log_file: str, script: str, args: List[str] = []) -> None:
        """Execute a given python script in the 'files' directory and append output to a given log file in the 'log' directory"""

        # Construct the command to execute
        cmd: List[str] = [
            "python",
            os.path.join(self.files_dir, script),
        ] + list(args)

        self.call(log_file, cmd)

    def copy(self, src: str, dest: str = "") -> None:
        """Copy a file from the test directory to the 'files' directory"""

        src_abs_path = os.path.join(self.test_dir, src)
        dest_abs_path = os.path.join(self.files_dir, dest)

        print("    " + src_abs_path + " -> " + dest_abs_path)

        shutil.copy(src_abs_path, dest_abs_path, follow_symlinks=False)


if __name__ == "__main__":
    # Set the working directory to the project root so tests can be executed as modules and use relative importing to import from this script
    working_dir: str = os.path.dirname(this_dir)
    os.chdir(working_dir)

    # Remove the name of this script from the argument list
    args: list = argv[1:]

    # Search for the optional 'clean' flag
    cleaning: bool = False
    if len(args) >= 1:
        cleaning = args[0] == "-c" or args[0] == "--clean"

        if cleaning:
            args = args[1:]

    # Use all tests if no arguments are given
    if len(args) == 0:
        if cleaning:
            # If cleaning, remove the '__pycache__' directory
            rmtree(os.path.join(this_dir, "__pycache__"))

        args = os.listdir(this_dir)

    tests = {}

    for dir_name in args:
        dir_abs_path = os.path.join(this_dir, dir_name)

        # Verify that the given path is valid
        if not os.path.exists(dir_abs_path):
            raise RuntimeError("Invalid test name: " + dir_name)

        # Ignore files and directories that are not tests
        if not os.path.isdir(dir_abs_path) or dir_name == "__pycache__":
            continue

        if cleaning:
            # Clean the test
            Test(os.path.join(this_dir, dir_name), prepare=False).clean()
        else:
            # Execute the test
            returncode = subprocess.run(
                [
                    "python",
                    "-m",
                    os.path.basename(this_dir)
                    + "."
                    + dir_name.removesuffix(os.sep)
                    + ".test",
                ]
            ).returncode

            # Record whether the test succeeded or failed
            tests[dir_name] = returncode == 0

    if not cleaning:
        # Report of the status of each executed test to stdout
        print("\n", end="")
        for test, success in tests.items():
            status_msg = "~~SUCCESS~~" if success else "//FAILURE//"
            print(test + ": " + status_msg)

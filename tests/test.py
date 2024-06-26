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


class Test:
    """Testing class for this template project"""

    def __init__(self, test_dir: str):
        print(os.path.basename(test_dir))

        self.test_dir = test_dir
        self.files_dir = os.path.join(self.test_dir, "files")
        self.log_dir = os.path.join(self.test_dir, "logs")

        self._prepare()

    def _prepare(self) -> None:
        """Prepare a fresh copy of this template project in the 'files' directory"""

        # Remove old files in the 'files' directory
        if os.path.exists(self.files_dir):
            shutil.rmtree(
                self.files_dir, onerror=_shutil_onerror, ignore_errors=True
            )

        # Remove old files in the 'log' directory
        if os.path.exists(self.log_dir):
            shutil.rmtree(
                self.log_dir, onerror=_shutil_onerror, ignore_errors=True
            )

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
                    file_abs_path, os.path.join(self.files_dir, file_name)
                )
            else:
                shutil.copy(
                    file_abs_path, os.path.join(self.files_dir, file_name)
                )

    def run(self, log_file: str, script: str, *args: str) -> None:
        """Execute a given python script in the 'files' directory and append output to a given log file in the 'log' directory"""

        # Construct the command to execute
        cmd: List[str] = [
            "python",
            os.path.join(self.files_dir, script),
        ] + list(args)

        # Write the command to stdout for debug purposes
        print("    " + log_file + "\n        ", end="")
        for arg in cmd:
            print(arg + " ", end="")
        print("\n", end="")

        # Execute the command and write output to the log file
        log_path = os.path.join(self.log_dir, log_file)
        with open(log_path, "a+") as log:
            subprocess.run(cmd, stdout=log, stderr=log, check=True)

    def copy(self, src: str, dest: str = "") -> None:
        """Copy a file from the test directory to the 'files' directory"""

        src_abs_path = os.path.join(self.test_dir, src)
        dest_abs_path = os.path.join(self.files_dir, dest)

        print("    " + src_abs_path + " -> " + dest_abs_path)

        shutil.copy(src_abs_path, dest_abs_path)


if __name__ == "__main__":
    # Set the working directory to the project root so tests can be executed as modules and use relative importing to import from this script
    working_dir: str = os.path.dirname(this_dir)
    os.chdir(working_dir)

    if len(argv) > 1:
        # If given arguments on the command line, interpret them as the names of tests to execute
        dirs = argv[1:]
    else:
        # If not given arguments on the command line, execute all tests
        dirs = os.listdir(this_dir)

    tests = {}

    for dir_name in dirs:
        dir_abs_path = os.path.join(this_dir, dir_name)

        # Verify that the given path is valid
        if not os.path.exists(dir_abs_path):
            raise RuntimeError("Invalid test name: " + dir_name)

        # Search for test directories
        if not os.path.isdir(dir_abs_path) or dir_name == "__pycache__":
            continue

        # Execute the test in the discovered test directory
        returncode = subprocess.run(
            [
                "python",
                "-m",
                os.path.basename(this_dir) + "." + dir_name + ".test",
            ]
        ).returncode

        # Record whether the test succeeded or failed
        tests[dir_name] = returncode == 0

    # Report of the status of each executed test to stdout
    print("\n", end="")
    for test, success in tests.items():
        status_msg = "~~SUCCESS~~" if success else "//FAILURE//"
        print(test + ": " + status_msg)

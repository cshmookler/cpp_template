"""Copy a file from the Meson build directory to the Meson source directory"""

import os, sys, shutil


def get_ev(name: str) -> str:
    """Retrieve an environment variable and ensure that it exists"""
    ev: str | None = os.getenv(name)
    if ev is None:
        raise RuntimeError(
            "The environment variable '" + name + "' does not exist"
        )
    return ev


if __name__ == "__main__":
    # Get the paths to the Meson build and source directories
    meson_build: str = get_ev("MESON_BUILD_ROOT")
    meson_source: str = get_ev("MESON_SOURCE_ROOT")

    # Get the absolute input and output paths
    input_path: str = os.path.join(meson_build, sys.argv[1])
    output_path: str = os.path.join(meson_source, sys.argv[2])

    # Copy the file to its destination
    shutil.copyfile(input_path, output_path)

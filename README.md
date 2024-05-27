# C++ Project Template

A template for modern C++ projects. Uses Conan for dependency management and Meson as the build system.

This project template includes:

- Convenient [Python](https://www.python.org/) scripts for managing the build environment.
- Different layouts for library and application projects.
- Automatic versioning through introspection of the latest [Git](https://git-scm.com/) tag.
    - Set by creating a [Git tag](https://git-scm.com/book/en/v2/Git-Basics-Tagging) (the name of the tag is the version).
    - Accessible within the code via the "version" namespace.
    - The default version "0.0.0" is used when there are no Git tags.
- Configuration files for [LLVM](https://llvm.org/) C++ tools (clangd, clang-format, and clang-tidy).
    - [clangd](https://clangd.llvm.org/) -- A language server configured by the ".clangd" file.
    - [clang-format](https://clang.llvm.org/docs/ClangFormat.html) -- A code formatter configured by the ".clang-format" file.
    - [clang-tidy](https://clang.llvm.org/extra/clang-tidy/) -- A code linter configured by the ".clang-tidy" file.
- Dependency management through [Conan](https://conan.io).
    - Add and remove dependencies and binaries by editing the "binary_config.json" file.
    - GoogleTest added by default.
- A [Meson](https://mesonbuild.com/) build file that receives dependency and binary information from Conan.
- A configuration file for the code formatting feature of [muon](https://git.sr.ht/~lattis/muon) (an implementation of Meson with a builtin code formatter and static analyzer).
- An automatically generated [README.md](https://en.wikipedia.org/wiki/README) file with detailed build instructions.
- A [gitignore](https://github.com/github/gitignore) file for C++ and Python.
- An example sub-project to demo how other programs can use your project (if it's a library).

## Setup

### 1.&nbsp; Install Git, Python, and a C++ compiler

#### Windows:

Install Git and Python:

1. [Git](https://git-scm.com/downloads/) (distributed version control)
2. [Python](https://python.org/downloads/) (interpreted scripting language)
    - Select the "Add python.exe to PATH" option.

Install one of the following C++ compilers:

- [Visual Studio's C++ compiler](https://visualstudio.microsoft.com/downloads/) (MSVC)
    - Select the "Desktop development with C++" option.
- [MinGW](https://sourceforge.net/projects/mingw/) (GCC for Windows)
    - Mark "mingw32-gcc-g++" for installation. Then select "Apply Changes" within the "Installation" dropdown.
    - Add the MinGW bin directory (C:\\MinGW\\bin\\) to your [PATH](https://stackoverflow.com/questions/5733220/how-do-i-add-the-mingw-bin-directory-to-my-system-path).

#### Mac:

Install [Homebrew](https://brew.sh/) (package manager for Mac) by opening a terminal and entering the following command:

```zsh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Use Homebrew to install Git, Python, and GCC (C++ compiler):

```zsh
brew install git python gcc
```

#### Linux (Ubuntu):

```bash
sudo apt install git python3 build-essential
```

#### Linux (Arch):

```bash
sudo pacman -S git python base-devel
```

### 2.&nbsp; Clone this template

Open command prompt (Windows) or a shell (Linux & Mac) and enter the commands below. The template will be downloaded to the current working directory.

```
git clone https://github.com/cshmookler/cpp_template.git
cd cpp_template
```

### 3.&nbsp; Edit "template_config.ini" to suit your project

Any text editor (Notepad, TextEdit, Nano, Vim, etc.) can be used as long as the file name and format are not changed.

#### Windows:

```shell
notepad template_config.ini
```

#### Mac:

```zsh
open -t template_config.ini
```

#### Linux:

```bash
nano template_config.ini
```

### 4.&nbsp; Configure this template

Use Python to execute the "config.py" script. Use command prompt (Windows) or a shell (Mac & Linux) so errors are shown.

```
python config.py
```

If errors occur, troubleshoot to isolate the issue and repeat steps 2-4.

## Build

Use Python to execute the "build.py" script. Use command prompt (Windows) or a shell (Mac & Linux) so errors are shown.

```
python build.py
```

## Manage Binaries

Binary configuration information is stored in the "binary_config.json" file. This JSON file contains a dictionary of binary names associated with information describing the corresponding binaries.

An example of a "binary_config.json" file annotated with comments prefixed with "//" is shown below. This example file describes a library named "cpp_template" that depends on Zlib and a test named "version" that depends on GoogleTest.

```json5
{
    "cpp_template": {                   // binary name
        "type": "library",              // * binary type:
                                        //     "application" -- generate an executable
                                        //     "library"     -- generate a library
                                        //     "test"        -- generate and execute a test
        "dependencies": {               // * dependencies (optional)
            "zlib/1.3.1": {             //   * dependency (example: Zlib)
                "enabled": true,        //     * enabled (optional):
                                        //         true  -- (default) link with this binary
                                        //         false -- do not link with this binary
                "dynamic": null,        //     * link method (optional):
                                        //         null  -- (default) no linking preference
                                        //         true  -- prefer dynamic linking
                                        //         false -- prefer static linking
                "components": {         //     * components (optional)
                    "zlib": true        //       * component (example: "zlib") (optional):
                                        //           true  -- (default) link with this component
                                        //           false -- do not link with this component
                }                       //
            }                           //
        },                              //
        "headers": [                    // * header file paths (only for libraries)
            [                           //   * header file path:
                "cpp_template",         //       (represented as a list of path components)
                "version.hpp"           //
            ]                           //
        ],                              //
        "sources": [                    // * source file paths
            [                           //   * source file path:
                "src",                  //       (represented as a list of path components)
                "version.cpp"           //
            ]                           //
        ],                              //
        // "main": ["src", "main.cpp"]  // * 'main' function file path:
                                        //     (only for applications and tests)
                                        //     (represented as a list of path components)
    },                                  //
    "version": {                        // binary name
        "type": "test",                 // * binary type:
                                        //     "application" -- generate an executable
                                        //     "library"     -- generate a library
                                        //     "test"        -- generate and execute a test
        "dependencies": {               // * dependencies (optional)
            "gtest/1.14.0": {           //   * dependency (example: GoogleTest)
                "enabled": true,        //     * enabled (optional):
                                        //         true  -- (default) link with this binary
                                        //         false -- do not link with this binary
                "dynamic": null,        //     * link method (optional):
                                        //         null  -- (default) no linking preference
                                        //         true  -- prefer dynamic linking
                                        //         false -- prefer static linking
                "components": {         //     * components (optional)
                    "gtest": true,      //       * component (example: "gtest") (optional):
                                        //           true  -- (default) link with this component
                                        //           false -- do not link with this component
                    "gtest_main": true, //       * component (example: "gtest_main") (optional):
                                        //           true  -- (default) link with this component
                                        //           false -- do not link with this component
                    "gmock": true,      //       * component (example: "gmock") (optional):
                                        //           true  -- (default) link with this component
                                        //           false -- do not link with this component
                    "gmock_main": true  //       * component (example: "gmock_main") (optional):
                                        //           true  -- (default) link with this component
                                        //           false -- do not link with this component
                }                       //
            }                           //
        },                              //
        "sources": [                    // * source file paths
            [                           //   * source file path:
                "src",                  //       (represented as a list of path components)
                "version.test.cpp"      //  
            ],                          //
            [                           //   * source file path:
                "src",                  //       (represented as a list of path components)
                "version.cpp"           //
            ]                           //
        ]                               //
    }                                   //
}                                       //
```

## Manage Dependencies

### Add dependencies

Browse [Conan Center](https://conan.io/center/) (the Conan central repository) for dependencies. Use the search bar to find the "name/version" of the dependencies you would like to add (example: "boost/1.85.0").

Add your chosen dependencies to the "dependencies" field of a binary within the "binary_config.json" file. Examples of dependencies in this file are shown in the [example above](#manage-binaries).

> Note: Existing build files may need to be [removed](#remove-build-files) for changes to take effect.

### Remove dependencies

Open the "binary_config.json" file and remove the dependencies from the "dependencies" field of a binary.

> Note: Existing build files may need to be [removed](#remove-build-files) for changes to take effect.

### Update the lists of dependency components

Some dependencies contain multiple components that can be individually enabled or disabled. The list of components for dependencies is automatically updated after each build.

To update the lists of dependency components without building, use Python to execute the "update_deps.py" script. Use command prompt (Windows) or a shell (Mac & Linux) so errors are shown.

```
python update_deps.py
```

## Remove Build Files

If the build system is changed (the "binary_config.json", "meson.build", or "conanfile.py" files are edited) then the existing build files may need to be regenerated. Removing the build files forces them to be regenerated when the project is built.

Use Python to execute the "clean.py" script. Use command prompt (Windows) or a shell (Mac & Linux) so errors are shown.

```
python clean.py
```

## Clear the Conan Cache

Clearing the Conan cache removes all downloaded dependencies. Required dependencies will be re-downloaded when the project is built.

Use Python to execute the "clear_cache.py" script. Use command prompt (Windows) or a shell (Mac & Linux) so errors are shown.

```
python clear_cache.py
```

## Conan Profile Management

The active Conan profiles list system architecture, operating system, C++ compiler, and other configuration information for Conan. All profiles are stored in the "profiles" directory and have a ".profile" extension. The default profile ("default.profile") is automatically generated if it does not exist.

Conan uses two active profiles: build and host. The build profile defines the platform where the binaries are built, and the host profile defines the platform where the binaries are executed. Using different build and host profiles is useful for [cross-compiling](https://docs.conan.io/2/tutorial/consuming_packages/cross_building_with_conan.html).

### View the active profiles

The paths to the active profiles are stored in the "profiles.ini" configuration file. If either of those profiles do not exist when the project is built, then the default profile is used instead.

To view the paths to the profiles that will actually be used when the project is built, use Python to execute the "profiles.py" script without any arguments. Use command prompt (Windows) or a shell (Mac & Linux) to show output and display errors.

```
python profiles.py
```

### Switch profiles

To change the active build profile, use Python to execute the "profiles.py" script with the new profile path following the "--build" option. Use command prompt (Windows) or a shell (Mac & Linux) to show output and display errors. The example below sets the active build profile to "new-build.profile".

```
python profiles.py --build new-build.profile
```

> Note: The new profile must exist in the "profiles" directory else the default profile will be used instead.

To change the active host profile, use the "--host" option instead. The example below sets the active host profile to "new-host.profile".

```
python profiles.py --host new-host.profile
```

### Regenerate the default profile

The default Conan profile is automatically regenerated if it is an active profile but does not exist when the project is built.

Delete the "default.profile" file in the "profiles" directory. Delete the "profiles.ini" file as well to ensure that the default profile is selected as an active profile. Use python to execute the "profiles.py" script without passing any arguments. Use command prompt (Windows) or a shell (Mac & Linux) to show output and display errors.

```
python profiles.py
```

## Install (for libraries)

Installing a project exports its source files and generated binaries to the Conan cache so that other projects can use it as a dependency.

Use Python to execute the "install.py" script. Use command prompt (Windows) or a shell (Mac & Linux) so errors are shown.

```
python install.py
```

## TODO

- [X] Proper GoogleTest integration.
- [X] ~~Some dependencies fail to build from source~~ Resolved by remote recipes adapting to Conan 2.
- [X] Provide options for controlling what modules are linked from dependencies.
- [X] Provide a more intuitive method for adding more executables, libraries and tests.
- [X] Generate different "conanfile.py" files for different package types.
- [X] Provide more detailed documentation.
- [X] Allow regeneration of the default Conan profile.
- [X] Use Jinja for templating.
- [X] Add support for different host and build profiles.
- [X] Add option for static or dynamic linking of dependencies.
- [X] Add build targets by editing a configuration file instead of manually editing the "meson.build" file.
- [ ] Add tests.
- [ ] ~~Generate SPDX licenses from templates.~~
- [ ] ~~Allow a template to be configured multiple times.~~


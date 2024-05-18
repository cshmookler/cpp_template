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
    - Add and remove dependencies by editing the "dependencies.ini" file.
    - GoogleTest added by default.
- A [Meson](https://mesonbuild.com/) build file that receives dependency information from Conan.
- A configuration file for the code formatting feature of [muon](https://git.sr.ht/~lattis/muon) (an implementation of Meson with a builtin code formatter and static analyzer).
- An automatically generated [README.md](https://en.wikipedia.org/wiki/README) file with detailed build instructions.
- A [gitignore](https://github.com/github/gitignore) file for C++ and Python.
- An example sub-project to demo how other programs can use your project (if it's a library).

## Setup

#### 1.&nbsp; Install Git, Python, and a C++ compiler

###### Windows:

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

###### Mac:

Install [Homebrew](https://brew.sh/) (package manager for Mac) by opening a terminal and entering the following command:

```zsh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Use Homebrew to install Git, Python, and GCC (C++ compiler):

```zsh
brew install git python gcc
```

###### Linux (Ubuntu):

```bash
sudo apt install git python3 build-essential
```

###### Linux (Arch):

```bash
sudo pacman -S git python base-devel
```

#### 2.&nbsp; Clone this template

Open command prompt (Windows) or a shell (Linux & Mac) and enter the commands below. The template will be downloaded to the current working directory.

```
git clone https://github.com/cshmookler/cpp_template.git
cd cpp_template
```

#### 3.&nbsp; Edit "template_config.ini" to suit your project

Any text editor (Notepad, TextEdit, Nano, Vim, etc.) can be used as long as the file name and format are not changed.

###### Windows:

```shell
notepad template_config.ini
```

###### Mac:

```zsh
open -t template_config.ini
```

###### Linux:

```bash
nano template_config.ini
```

#### 4.&nbsp; Configure this template

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

## Manage Dependencies

#### Add dependencies

Browse [Conan Center](https://conan.io/center/) (the Conan central repository) for dependencies. Use the search bar to find the "name/version" of the dependencies you would like to add (example: "boost/1.85.0").

Open the "dependencies.ini" file and add the dependencies underneath the "[explicit]" tag. Each dependency must be on its own line and be of the form "name/version = yes".

#### Remove dependencies

Open the "dependencies.ini" file and change the cooresponding "yes" to "no". Alternatively, delete the lines containing the dependencies.

#### Update implicit dependencies

Implicit dependencies are required dependencies of those that are explicitly declared. The list of implicit dependencies in the "dependencies.ini" file is automatically updated after each build.

To update the list of implicit dependencies without building, use Python to execute the "update_deps.py" script. Use command prompt (Windows) or a shell (Mac & Linux) so errors are shown.

```
python update_deps.py
```

## Remove Build Files

If the build system is changed (the "meson.build" or "conanfile.py" files are edited) then the existing build files may need to be regenerated. Removing the build files forces them to be regenerated once the project is built.

Use Python to execute the "clean.py" script. Use command prompt (Windows) or a shell (Mac & Linux) so errors are shown.

```
python clean.py
```

## Clear the Conan Cache

Clearing the Conan cache removes all downloaded dependencies. Required dependencies will be re-downloaded once the project is built.

Use Python to execute the "clear_cache.py" script. Use command prompt (Windows) or a shell (Mac & Linux) so errors are shown.

```
python clear_cache.py
```

## Change the Conan Profile

The active Conan profile lists the system architecture, operating system, C++ compiler, and other configuration information for Conan. All profiles are stored in the "profiles" directory and have a ".profile" extension. The default profile ("default.profile") is automatically generated during setup.

To change the active Conan profile to another stored in the "profiles" directory, edit the "profile.ini" file. Alternatively, use Python to execute the "profile.py" script and provide the name of the new Conan profile as a command line argument ("new.profile" in the example below). Use command prompt (Windows) or a shell (Mac & Linux) to provide the new profile name, show output, and display errors.

```
python profile.py new.profile
```

To reset the active profile to the default profile ("default.profile"), execute the "profile.py" script without any arguments.

```
python profile.py
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
- [ ] Create a script for generating the default profile with Conan.
- [ ] Use Jinja for templating.
- [ ] Add support for different host and build profiles.
- [ ] Add option for static or dynamic linking of dependencies.
- [ ] Add build targets by editing a configuration file instead of manually editing the "meson.build" file.
- [ ] Add support for clang-analyzer.
- [ ] Add tests.
- [ ] ~~Generate SPDX licenses from templates.~~
- [ ] ~~Allow a template to be configured multiple times.~~


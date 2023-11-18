# **C++ Project Template**

C++ project template with automatic versioning, LLVM tools, Conan, Meson, and GoogleTest integration.

## **Make it your own (for Unix-like systems)**

**1.** Install Python >= 3.7 (Example: apt).

```bash
sudo apt install -y python3
```

**2.** Modify the `template_config.ini` file to suite your project.

**3.** Configure this template.

```bash
python3 config.py
```

## **Build and install this project with Conan (for Unix-like systems)**

> Note: Configure this template before building it for the first time! -> [configure](#make-it-your-own-for-unix-like-systems)

**1.** Install a C++ compiler (Example: clang), Git, and Python >=3.7 (Example: apt).

```bash
sudo apt install -y clang git python3
```

**2.** (Optional) Create a Python >=3.7 virtual environment and activate it. Install the Python Virtual Environment if you haven't already.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**3.** Install Conan.

```bash
pip3 install "conan>=2.0.0"
```

**4.** Create the default Conan profile.

```bash
conan profile detect
```

**5.** Build and install with Conan.

```bash
conan create . --build=missing
```

Alternatively, build with Conan without installing.

```bash
conan build . --build=missing
```

<details>
<summary> <strong>Click here if you get an error while building with Conan</strong> </summary>

- #### Failed to build dependency from source

```
CMake Error at /usr/local/share/cmake-3.26/Modules/CmakeTestCXXCompiler.cmake:60 (message):
  The C++ compiler

    "/usr/bin/c++"

  is not able to compile a simple test program.
```

<details>
<summary> <strong>Click here if this is your error</strong> </summary>

A dependency likely passed invalid compiler flags. Try using a different compiler.

**1.** Clear the Conan cache.

```bash
yes | conan remove "*"
```

**2.** If you ran 'conan build', delete the build directory (do not do this if you ran 'conan create').

```bash
rm -rf build
```

**3.** Set a different compiler for CMake to use.

- For Clang:

```bash
export CC=clang
export CXX=clang++
```

- For GCC:

```bash
export CC=gcc
export CXX=g++
```

</details>

- #### Conan related error

See the official [Conan FAQ](https://docs.conan.io/2/knowledge/faq.html) for help with common errors.

</details>

## **TODO**

- [X] Proper GoogleTest integration.
- [ ] Some dependencies fail to build from source (may just be a Conan problem).
- [ ] Provide options for controlling what modules are linked from dependencies.
- [ ] Allow a template to be configured multiple times.
- [X] Provide a more intuitive method for adding more executables, libraries and tests.


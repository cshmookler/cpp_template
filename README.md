# **C++ Template Project**
C++ project template with automatic versioning, LLVM tools, Conan, and Meson.

## **Build and install this project with Conan (for Unix-like systems)**
**1.** Install a C++ compiler (Example: clang), Git, and Python >=3.7 (Example: apt).
```bash
$ sudo apt install clang git python3
```
**2.** (Optional) Create a Python >=3.7 virtual environment and activate it. You may need to install the Python Virtual Environment if you haven't already.
```bash
$ python3 -m venv .venv
$ source .venv/bin/activate
```
**3.** Install Conan.
```bash
$ pip3 install "conan>=2.0.0"
```
**4.** Create the default Conan profile.
```bash
$ conan profile detect
```
**5.** Build and install this project with Conan.
```bash
$ conan create .
```

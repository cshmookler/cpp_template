# **C++ Project Template**

C++ project template with automatic versioning, LLVM tools, Conan, and Meson.

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

**4.** Remove template files.

```bash
python3 confirm.py
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

**5.** Build and install this project with Conan.

```bash
conan create .
```

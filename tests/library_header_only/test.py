import os

from tests.test import Test


this_dir: str = os.path.dirname(__file__)

test = Test(this_dir)

test.copy("template_config.ini")
test.run("config", "config.py")
test.run("clear_cache", "clear_cache.py")
test.copy("binary_config.json")
test.run("build", "build.py")
test.run("clean", "clean.py")
test.run("update_deps", "update_deps.py")
test.run("install", "install.py")

from tests.test import Test
import os


this_dir: str = os.path.dirname(__file__)

test = Test(this_dir)

test.copy("template_config.ini")
test.run("config", "config.py")
test.run("clear_cache", "clear_cache.py")
test.run("first_build", "build.py")
test.run("clean", "clean.py")
test.run("update_deps", "update_deps.py")
test.run("second_build", "build.py")

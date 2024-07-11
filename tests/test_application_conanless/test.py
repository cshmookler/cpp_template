from tests.test import Test
import os


this_dir: str = os.path.dirname(__file__)

test = Test(this_dir)

test.copy("template_config.ini")
test.run("config", "config.py")
test.call(
    "setup",
    ["meson", "setup", os.path.join(test.files_dir, "build"), test.files_dir],
)
test.call(
    "build",
    ["ninja", "-C", os.path.join(test.files_dir, "build")],
)

from tests.test import Test
import os


this_dir: str = os.path.dirname(__file__)

test = Test(this_dir, expect_failure=True)

test.copy("template_config.ini")
test.run("config", "config.py")

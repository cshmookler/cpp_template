from conan import ConanFile
from os.path import join as join_path
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.gnu import PkgConfigDeps
from conan.tools.build import can_run

required_conan_version = ">=2.0.6"

class ansiesTestPackage(ConanFile):
    # Required
    name = "test_package"
    version = "1.0.0"

    # Configuration
    settings = "os", "compiler", "build_type", "arch"

    def build_requirements(self):
        self.tool_requires("meson/1.2.1")
        self.tool_requires("pkgconf/2.0.3")

    def requirements(self):
        self.requires(self.tested_reference_str)
        self._meson_dependencies = [self.tested_reference_str.split("/")[0]]

    def layout(self):
        self.folders.build = "build"
        self.folders.generators = join_path(self.folders.build, "generators")

    def generate(self):
        deps = PkgConfigDeps(self)
        deps.generate()
        tc = MesonToolchain(self)
        tc.properties = {
            "name" : self.name,
            "version" : self.version,
            "deps" : self._meson_dependencies
        }
        tc.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()
    
    def test(self):
        if can_run(self):
            cmd = join_path(self.build_folder, "test_package")
            self.run(cmd, env="conanrun")

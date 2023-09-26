from conan import ConanFile
from conan.tools.scm import Git
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.gnu import PkgConfigDeps
from conan.tools.files import copy as copy_file
from os.path import join as join_path

required_conan_version = ">=2.0.6"

class ansies(ConanFile):
    # Required
    name = "cpp_template"

    # Metadata
    license = "Zlib"
    author = "Caden Shmookler (cshmookler@gmail.com)"
    url = "https://github.com/cshmookler/cpp-template.git"
    description = "C++ project template with automatic versioning, LLVM tools, Conan, and Meson."
    topics = "c++"

    # Configuration
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }
    build_policy = "missing"

    # Essential files
    exports_sources = ".git/*", "include/*", "src/*", "meson.build", "LICENSE"

    # Paths
    _build_folder = "build"
    _generator_folder = join_path(_build_folder, "generators")

    def set_version(self):
        git = Git(self, folder=self.recipe_folder)
        full_version = git.run("describe --tags")
        fragmented_version = full_version.split("-")
        if len(fragmented_version) > 1:
            fragmented_version = [fragmented_version[0], fragmented_version[1]]
        self.version = ".".join(fragmented_version)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
    
    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def build_requirements(self):
        self.tool_requires("meson/1.2.1")
        self.tool_requires("pkgconf/2.0.3")

    def requirements(self):
        # self.requires("boost/1.83.0")
        # self.requires("eigen/3.4.0")
        self._meson_dependencies = [
            # "boost",
            # "eigen3"
        ]

    def layout(self):
        self.folders.build = self._build_folder
        self.folders.generators = self._generator_folder
    
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
        copy_file(self,
            "version.hpp",
            self.build_folder,
            join_path(self.source_folder, "include", self.name))
        copy_file(self,
            "version.cpp",
            self.build_folder,
            join_path(self.source_folder, "src"))
        meson.build()

    def package(self):
        meson = Meson(self)
        meson.install()

    def package_info(self):
        self.cpp_info.libs = [self.name]
        self.cpp_info.includedirs = ["include"]

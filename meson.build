project(meson.get_external_property('name', 'unknown'),
        'cpp',
        version : meson.get_external_property('version', 'unknown'),
        default_options : ['cpp_std=c++11'])

project_name = meson.project_name()
if project_name == 'unknown'
    error('Failed to get library name from Conan.')
endif

project_version = meson.project_version()
if project_version == 'unknown'
    error('Failed to get library version from Conan.')
endif

project_dep_strings = meson.get_external_property('deps', ['unknown'])
if project_dep_strings == ['unknown']
    error('Failed to get library dependencies from Conan.')
endif

project_deps = []
foreach dep : project_dep_strings
    project_deps += dependency(dep)
endforeach

include_dir = meson.source_root()/'include'/project_name
src_dir = meson.source_root()/'src'
build_dir = meson.build_root()

conf_data = configuration_data()
conf_data.set('name', project_name)
conf_data.set('version', project_version)
configure_file(configuration : conf_data,
               input : include_dir/'version.hpp.in',
               output : 'version.hpp')
configure_file(configuration : conf_data,
               input : src_dir/'version.cpp.in',
               output : 'version.cpp')

headers = files(build_dir/'version.hpp')
sources = files(build_dir/'version.cpp')

ansies = library(project_name,
                 sources,
                 dependencies : project_deps,
                 version : project_version,
                 install : true)
install_headers(headers, subdir : project_name)

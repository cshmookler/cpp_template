project(
    meson.get_external_property('_name', 'unknown'),
    'cpp',
    version : meson.get_external_property('_version', 'unknown'),
    default_options : [ 'cpp_std=c++11' ],
)

project_name = meson.project_name()
if project_name == 'unknown'
    error('Failed to get project name from Conan.')
endif

project_version = meson.project_version()
if project_version == 'unknown'
    error('Failed to get project version from Conan.')
endif

project_dep_strings = meson.get_external_property('_deps', [ 'unknown' ])
if project_dep_strings == [ 'unknown' ]
    error('Failed to get project dependencies from Conan.')
endif

project_deps = []
foreach dep : project_dep_strings
    project_deps += dependency(dep)
endforeach

executable(
    meson.project_name(),
    'src' / 'main.cpp',
    dependencies : project_deps,
)


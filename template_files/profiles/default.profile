{% set compiler, version, compiler_exe = detect_api.detect_default_compiler() %}
{% set runtime, _ = detect_api.default_msvc_runtime(compiler) %}
[settings]
os={{detect_api.detect_os()}}
arch={{detect_api.detect_arch()}}
build_type=Release
compiler={{compiler}}
compiler.version={{detect_api.default_compiler_version(compiler, version)}}
compiler.runtime={{runtime}}
compiler.cppstd={{detect_api.default_cppstd(compiler, version)}}
compiler.libcxx={{detect_api.detect_libcxx(compiler, version, compiler_exe)}}

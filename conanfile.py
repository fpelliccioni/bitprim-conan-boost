from conans import ConanFile, CMake
from conans import tools
import os, sys

class BitprimconanboostConan(ConanFile):
    name = "bitprim-conan-boost"
    version = "1.64.0"
    license = "http://www.boost.org/LICENSE_1_0.txt"
    url = "https://github.com/bitprim/bitprim-conan-boost/blob/master/conanfile.py"
    description = "Parameterized Conan recipe for Boost"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    exports_sources = "src/*"
    exports = ["FindBoost.cmake", "OriginalFindBoost*"]
    short_paths = True
    FOLDER_NAME = "boost_%s" % version.replace(".", "_")
    options = {
        "shared": [True, False],
        "header_only": [True, False],
        "fPIC": [True, False],
        "python": [True, False],
        "without_atomic": [True, False],
        "without_chrono": [True, False],
        "without_container": [True, False],
        "without_context": [True, False],
        "without_coroutine": [True, False],
        "without_coroutine2": [True, False],
        "without_date_time": [True, False],
        "without_exception": [True, False],
        "without_filesystem": [True, False],
        "without_graph": [True, False],
        "without_graph_parallel": [True, False],
        "without_iostreams": [True, False],
        "without_locale": [True, False],
        "without_log": [True, False],
        "without_math": [True, False],
        "without_mpi": [True, False],
        "without_program_options": [True, False],
        "without_random": [True, False],
        "without_regex": [True, False],
        "without_serialization": [True, False],
        "without_signals": [True, False],
        "without_system": [True, False],
        "without_test": [True, False],
        "without_thread": [True, False],
        "without_timer": [True, False],
        "without_type_erasure": [True, False],
        "without_wave": [True, False]
    }

    default_options = "shared=False", \
        "header_only=False", \
        "fPIC=True", \
        "python=True", \
        "without_atomic=False", \
        "without_chrono=False", \
        "without_container=True", \
        "without_context=True", \
        "without_coroutine=True", \
        "without_coroutine2=True", \
        "without_date_time=False", \
        "without_exception=True", \
        "without_filesystem=False", \
        "without_graph=True", \
        "without_graph_parallel=True", \
        "without_iostreams=False", \
        "without_locale=False", \
        "without_log=False", \
        "without_math=True", \
        "without_mpi=True", \
        "without_program_options=False", \
        "without_random=False", \
        "without_regex=False", \
        "without_serialization=True", \
        "without_signals=True", \
        "without_system=False", \
        "without_test=False", \
        "without_thread=False", \
        "without_timer=False", \
        "without_type_erasure=True", \
        "without_wave=True"

    def build(self):
        if self.options.header_only:
            self.output.warn("Header only package, skipping build")
            return

        toolset = "darwin" if self.settings.os == "Macos" else self.settings.compiler
        
        # command = "bootstrap" if self.settings.os == "Windows" else "./bootstrap.sh --with-toolset=%s" % self.settings.compiler
        command = "bootstrap" if self.settings.os == "Windows" else "./bootstrap.sh --with-toolset=%s" % toolset
        
        try:
            self.run("cd %s && %s" % (self.FOLDER_NAME, command))
        except:
            self.run("cd %s && type bootstrap.log" % self.FOLDER_NAME
                    if self.settings.os == "Windows"
                    else "cd %s && cat bootstrap.log" % self.FOLDER_NAME)
            raise

        flags = []
        if self.settings.compiler == "Visual Studio":
            flags.append("toolset=msvc-%s" % self._msvc_version())
        elif self.settings.compiler == "gcc":
            # For GCC we only need the major version otherwhise Boost doesn't find the compiler
            #flags.append("toolset=%s-%s"% (self.settings.compiler, self._gcc_short_version(self.settings.compiler.version)))
            flags.append("toolset=gcc")
        elif str(self.settings.compiler) in ["clang"]:
            flags.append("toolset=%s-%s"% (self.settings.compiler, self.settings.compiler.version))

        flags.append("link=%s" % ("static" if not self.options.shared else "shared"))
        if self.settings.compiler == "Visual Studio" and self.settings.compiler.runtime:
            flags.append("runtime-link=%s" % ("static" if "MT" in str(self.settings.compiler.runtime) else "shared"))
        flags.append("variant=%s" % str(self.settings.build_type).lower())
        flags.append("address-model=%s" % ("32" if self.settings.arch == "x86" else "64"))

        option_names = {
            "--without-atomic": self.options.without_atomic,
            "--without-chrono": self.options.without_chrono,
            "--without-container": self.options.without_container,
            "--without-coroutine": self.options.without_coroutine,
            "--without-coroutine2": self.options.without_coroutine2,
            "--without-date_time": self.options.without_date_time,
            "--without-exception": self.options.without_exception,
            "--without-filesystem": self.options.without_filesystem,
            "--without-graph": self.options.without_graph,
            "--without-graph_parallel": self.options.without_graph_parallel,
            "--without-iostreams": self.options.without_iostreams,
            "--without-locale": self.options.without_locale,
            "--without-log": self.options.without_log,
            "--without-math": self.options.without_math,
            "--without-mpi": self.options.without_mpi,
            "--without-program_options": self.options.without_program_options,
            "--without-random": self.options.without_random,
            "--without-regex": self.options.without_regex,
            "--without-serialization": self.options.without_serialization,
            "--without-signals": self.options.without_signals,
            "--without-system": self.options.without_system,
            "--without-test": self.options.without_test,
            "--without-thread": self.options.without_thread,
            "--without-timer": self.options.without_timer,
            "--without-type_erasure": self.options.without_type_erasure,
            "--without-wave": self.options.without_wave
        }

        for option_name, activated in option_names.items():
            if activated:
                flags.append(option_name)

        cxx_flags = []
        # fPIC DEFINITION
        if self.settings.compiler != "Visual Studio":
            if self.options.fPIC:
                cxx_flags.append("-fPIC")


        # LIBCXX DEFINITION FOR BOOST B2
        try:
            if str(self.settings.compiler.libcxx) == "libstdc++":
                flags.append("define=_GLIBCXX_USE_CXX11_ABI=0")
            elif str(self.settings.compiler.libcxx) == "libstdc++11":
                flags.append("define=_GLIBCXX_USE_CXX11_ABI=1")
            if "clang" in str(self.settings.compiler):
                if str(self.settings.compiler.libcxx) == "libc++":
                    cxx_flags.append("-stdlib=libc++")
                    cxx_flags.append("-std=c++11")
                    flags.append('linkflags="-stdlib=libc++"')
                else:
                    cxx_flags.append("-stdlib=libstdc++")
                    cxx_flags.append("-std=c++11")
        except BaseException as e:
            self.output.warn(e.message)

        cxx_flags = 'cxxflags="%s"' % " ".join(cxx_flags) if cxx_flags else ""
        flags.append(cxx_flags)
        flags.append("--without-python")

        # JOIN ALL FLAGS
        b2_flags = " ".join(flags)

        command = "b2" if self.settings.os == "Windows" else "./b2"

        full_command = "cd %s && %s %s -j%s" % (
            self.FOLDER_NAME,
            command,
            b2_flags,
            tools.cpu_count())
        self.output.warn(full_command)

        envs = self.prepare_deps_options_env()
        with tools.environment_append(envs):
            self.run(full_command)#, output=False)

    def config_options(self):
        """ First configuration step. Only settings are defined. Options can be removed
        according to these settings
        """
        if self.settings.compiler == "Visual Studio":
            self.options.remove("fPIC")

    def configure(self):
        """ Second configuration step. Both settings and options have values, in this case
        we can force static library if MT was specified as runtime
        """
        if self.settings.compiler == "Visual Studio" and \
           self.options.shared and "MT" in str(self.settings.compiler.runtime):
            self.options.shared = False

        if self.options.header_only:
            # Should be doable in conan_info() but the UX is not ready
            self.options.remove("shared")
            self.options.remove("fPIC")

        if not self.options.without_iostreams:
            if self.settings.os == "Linux" or self.settings.os == "Macos":
                self.requires("bzip2/1.0.6@lasote/stable")
                if not self.options.header_only:
                    self.options["bzip2/1.0.6"].shared = self.options.shared
            self.requires("zlib/1.2.11@lasote/stable")
            if not self.options.header_only:
                self.options["zlib"].shared = self.options.shared

    def package(self):
        # Copy findZLIB.cmake to package
        self.copy("FindBoost.cmake", ".", ".")
        self.copy("OriginalFindBoost*", ".", ".")

        self.copy(pattern="*", dst="include/boost", src="%s/boost" % self.FOLDER_NAME)
        self.copy(pattern="*.a", dst="lib", src="%s/stage/lib" % self.FOLDER_NAME)
        self.copy(pattern="*.so", dst="lib", src="%s/stage/lib" % self.FOLDER_NAME)
        self.copy(pattern="*.so.*", dst="lib", src="%s/stage/lib" % self.FOLDER_NAME)
        self.copy(pattern="*.dylib*", dst="lib", src="%s/stage/lib" % self.FOLDER_NAME)
        self.copy(pattern="*.lib", dst="lib", src="%s/stage/lib" % self.FOLDER_NAME)
        self.copy(pattern="*.dll", dst="bin", src="%s/stage/lib" % self.FOLDER_NAME)

    def package_id(self):
        """ if it is header only, the requirements, settings and options do not affect the package ID
        so they should be removed, so just 1 package for header only is generated, not one for each
        different compiler and option. This is the last step, after build, and package
        """
        if self.options.header_only:
            self.info.requires.clear()
            self.info.settings.clear()

    def package_info(self):

        if not self.options.header_only and self.options.shared:
            self.cpp_info.defines.append("BOOST_ALL_DYN_LINK")
        else:
            self.cpp_info.defines.append("BOOST_USE_STATIC_LIBS")

        if self.options.header_only:
            return

        libs = ("wave unit_test_framework prg_exec_monitor test_exec_monitor container exception "
                "graph iostreams locale log log_setup math_c99 math_c99f math_c99l math_tr1 "
                "math_tr1f math_tr1l program_options random regex wserialization serialization "
                "signals coroutine context timer thread chrono date_time atomic filesystem system").split()

        if self.settings.compiler != "Visual Studio":
            self.cpp_info.libs.extend(["boost_%s" % lib for lib in libs])
        else:
            win_libs = []
            # http://www.boost.org/doc/libs/1_55_0/more/getting_started/windows.html
            visual_version = self._msvc_version()
            runtime = "mt" # str(self.settings.compiler.runtime).lower()

            abi_tags = []
            if self.settings.compiler.runtime in ("MTd", "MT"):
                abi_tags.append("s")

            if self.settings.build_type == "Debug":
                abi_tags.append("gd")

            abi_tags = ("-%s" % "".join(abi_tags)) if abi_tags else ""

            version = "_".join(self.version.split(".")[0:2])
            suffix = "vc%s-%s%s-%s" %  (visual_version.replace(".", ""), runtime, abi_tags, version)
            prefix = "lib" if not self.options.shared else ""


            win_libs.extend(["%sboost_%s-%s" % (prefix, lib, suffix) for lib in libs if lib not in ["exception", "test_exec_monitor"]])
            win_libs.extend(["libboost_exception-%s" % suffix, "libboost_test_exec_monitor-%s" % suffix])

            #self.output.warn("EXPORTED BOOST LIBRARIES: %s" % win_libs)
            self.cpp_info.libs.extend(win_libs)
            self.cpp_info.defines.extend(["BOOST_ALL_NO_LIB"]) # DISABLES AUTO LINKING! NO SMART AND MAGIC DECISIONS THANKS!

    def prepare_deps_options_env(self):
        ret = {}
#         if self.settings.os == "Linux" and "bzip2" in self.requires:
#             include_path = self.deps_cpp_info["bzip2"].include_paths[0]
#             lib_path = self.deps_cpp_info["bzip2"].lib_paths[0]
#             lib_name = self.deps_cpp_info["bzip2"].libs[0]
#             ret["BZIP2_BINARY"] = lib_name
#             ret["BZIP2_INCLUDE"] = include_path
#             ret["BZIP2_LIBPATH"] = lib_path

        return ret

    def source(self):
        zip_name = "%s.zip" % self.FOLDER_NAME if sys.platform == "win32" else "%s.tar.gz" % self.FOLDER_NAME
        url = "http://sourceforge.net/projects/boost/files/boost/%s/%s/download" % (self.version, zip_name)
        self.output.info("Downloading %s..." % url)
        tools.download(url, zip_name)
        tools.unzip(zip_name, ".")
        os.unlink(zip_name)

    def _msvc_version(self):
        if self.settings.compiler.version == "15":
            return "14.1"
        else:
            return "%s.0" % self.settings.compiler.version

    def _gcc_short_version(self, version):
        return str(version)[0]

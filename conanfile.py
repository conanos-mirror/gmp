#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools, AutoToolsBuildEnvironment,CMake
import os

from conanos.build import config_scheme,pkgconfig_adaption

def _abspath(folder):
    return os.path.abspath(folder).replace('\\','/')

class GmpConan(ConanFile):
    name = "gmp"
    version = "6.1.2"
    url = "https://github.com/bincrafters/conan-gmp"
    description = "GMP is a free library for arbitrary precision arithmetic, operating on signed integers, rational numbers, and floating-point numbers."
    website = "https://gmplib.org"
    license = "LGPL-3.0, GPL-2.0"
    exports = ["LICENSE.md"]
    exports_sources = ["FindGMP.cmake",'CMakeLists.txt','cmake/*']
    source_subfolder = "source_subfolder"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "disable_assembly": [True, False]}#, "run_checks": [True, False]}
    default_options = "shared=False", "fPIC=True", "disable_assembly=True"#, "run_checks=False"
    generators = "cmake"

    _source_folder    ='_source'
    _pkgconfig_folder ='_pkgconfig'
    _build_folder     ='_build'

    @property
    def is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    @property
    def run_checks(self):
        CONANOS_RUN_CHECKS = os.environ.get('CONANOS_RUN_CHECKS')
        if CONANOS_RUN_CHECKS:
            return self.name in CONANOS_RUN_CHECKS.split()
        return False

    def configure(self):
        # Because this is pure C
        del self.settings.compiler.libcxx
        if self.is_msvc:
            del self.options.fPIC
            if self.options.shared:
               raise tools.ConanException("The gmp package cannot be built shared on Visual Studio.")
               
    def requirements(self):
        config_scheme(self)

    def source(self):
        source_url = "https://gmplib.org/download/gmp"
        tools.get("{0}/{1}-{2}.tar.bz2".format(source_url, self.name, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_folder)

    def autotool_build(self):
        env_build = AutoToolsBuildEnvironment(self)
        env_build.fpic = self.options.fPIC
        with tools.environment_append(env_build.vars):

            with tools.chdir(self._source_folder):

                if self.settings.os == "Macos":
                    tools.replace_in_file("configure", r"-install_name \$rpath/", "-install_name ")

                self.run("chmod +x configure")

                configure_args = []
                if self.options.disable_assembly:
                    configure_args.append('--disable-assembly')
                if self.options.shared:
                    configure_args.extend(["--enable-shared", "--disable-static"])
                else:
                    configure_args.extend(["--disable-shared", "--enable-static"])

                env_build.configure(args=configure_args)
                env_build.make()

                # According to the gmp readme file, make check should not be omitted, but it causes timeouts on the CI server.
                #if self.options.run_checks:
                if self.run_checks:
                    env_build.make(args=['check'])
                env_build.install()

    def cmake_build(self):
        GMP_PROJECT_DIR = os.path.abspath(self._source_folder).replace('\\','/')
        
        cmake = CMake(self)
        cmake.configure(source_folder= '.',build_folder='~build',
            defs={'USE_CONAN_IO':True,
                  'GMP_PROJECT_DIR':GMP_PROJECT_DIR,
                  'ENABLE_UNIT_TESTS':self.run_checks
            })
        cmake.build()
        if self.run_checks:
            cmake.test()
        cmake.install()

    def build(self):
        pkgconfig_adaption(self,_abspath(self._source_folder))
        
        if self.is_msvc:
            self.cmake_build()
        else:
            self.autotool_build()

    def package(self):
        return
        # dual license
        self.copy("COPYINGv2", dst="licenses", src=self._source_folder)
        self.copy("COPYING.LESSERv3", dst="licenses", src=self._source_folder)
        self.copy(pattern="gmp.h", dst="include", src=self._source_folder)
        self.copy("FindGMP.cmake")
        if self.options.shared:
            self.copy(pattern="libgmp.so*", dst="lib", src="%s/.libs" % self._source_folder, keep_path=False)
            self.copy(pattern="libgmp.dylib", dst="lib", src="%s/.libs" % self._source_folder, keep_path=False)
            self.copy(pattern="libgmp.*.dylib", dst="lib", src="%s/.libs" % self._source_folder, keep_path=False)
        else:
            self.copy(pattern="libgmp.a", dst="lib", src="%s/.libs" % self._source_folder, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

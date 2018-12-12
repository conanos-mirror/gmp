#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools, AutoToolsBuildEnvironment,MSBuild
import os
from conanos.build import config_scheme

class GmpConan(ConanFile):
    name = "gmp"
    version = "6.1.2-5"
    description = "GMP is a free library for arbitrary precision arithmetic, operating on signed integers, rational numbers, and floating-point numbers."
    url = "https://github.com/conanos/gmp"
    homepage = "https://gmplib.org"
    license = "LGPL-3.0, GPL-2.0"
    exports = ["COPYINGv3","COPYINGv2"]
    generators = "visual_studio", "gcc"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "disable_assembly": [True, False]}#, "run_checks": [True, False]}
    default_options = { 'shared': True, 'fPIC': True, 'disable_assembly' : False } #, "run_checks=False"

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        config_scheme(self)

    def source(self):
        url_ = "https://github.com/ShiftMediaProject/gmp/archive/{version}.tar.gz".format(version=self.version)
        tools.get(url_)
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    #def autotool_build(self):
    #    env_build = AutoToolsBuildEnvironment(self)
    #    env_build.fpic = self.options.fPIC
    #    with tools.environment_append(env_build.vars):

    #        with tools.chdir(self._source_folder):

    #            if self.settings.os == "Macos":
    #                tools.replace_in_file("configure", r"-install_name \$rpath/", "-install_name ")

    #            self.run("chmod +x configure")

    #            configure_args = []
    #            if self.options.disable_assembly:
    #                configure_args.append('--disable-assembly')
    #            if self.options.shared:
    #                configure_args.extend(["--enable-shared", "--disable-static"])
    #            else:
    #                configure_args.extend(["--disable-shared", "--enable-static"])

    #            env_build.configure(args=configure_args)
    #            env_build.make()

    #            # According to the gmp readme file, make check should not be omitted, but it causes timeouts on the CI server.
    #            #if self.options.run_checks:
    #            if self.run_checks:
    #                env_build.make(args=['check'])
    #            env_build.install()

    #def cmake_build(self):
    #    GMP_PROJECT_DIR = os.path.abspath(self._source_folder).replace('\\','/')
    #    
    #    cmake = CMake(self)
    #    cmake.configure(source_folder= '.',build_folder='~build',
    #        defs={'USE_CONAN_IO':True,
    #              'GMP_PROJECT_DIR':GMP_PROJECT_DIR,
    #              'ENABLE_UNIT_TESTS':self.run_checks
    #        })
    #    cmake.build()
    #    if self.run_checks:
    #        cmake.test()
    #    cmake.install()

    #def build(self):
    #    #pkgconfig_adaption(self,_abspath(self._source_folder))
    #    
    #    if self.is_msvc:
    #        self.cmake_build()
    #    else:
    #        self.autotool_build()
    
    def build(self):
        if self.settings.os == "Windows":
            with tools.chdir(os.path.join(self._source_subfolder,"SMP")):
                msbuild = MSBuild(self)
                build_type = str(self.settings.build_type) + ("DLL" if self.options.shared else "")
                msbuild.build("libgmp.sln",upgrade_project=True, build_type=build_type)


    #def package(self):
    #    return
    #    # dual license
    #    self.copy("COPYINGv2", dst="licenses", src=self._source_folder)
    #    self.copy("COPYING.LESSERv3", dst="licenses", src=self._source_folder)
    #    self.copy(pattern="gmp.h", dst="include", src=self._source_folder)
    #    self.copy("FindGMP.cmake")
    #    if self.options.shared:
    #        self.copy(pattern="libgmp.so*", dst="lib", src="%s/.libs" % self._source_folder, keep_path=False)
    #        self.copy(pattern="libgmp.dylib", dst="lib", src="%s/.libs" % self._source_folder, keep_path=False)
    #        self.copy(pattern="libgmp.*.dylib", dst="lib", src="%s/.libs" % self._source_folder, keep_path=False)
    #    else:
    #        self.copy(pattern="libgmp.a", dst="lib", src="%s/.libs" % self._source_folder, keep_path=False)
    
    def package(self):
        if self.settings.os == "Windows":
            platform = {'x86': 'x86','x86_64': 'x64'}
            rplatform = platform.get(str(self.settings.arch))
            self.copy("*", dst=os.path.join(self.package_folder,"include"), src=os.path.join(self.build_folder,"..", "msvc","include"))
            for i in ["lib","bin"]:
                self.copy("*", dst=os.path.join(self.package_folder,i), src=os.path.join(self.build_folder,"..","msvc",i,rplatform))
            self.copy("*", dst=os.path.join(self.package_folder,"licenses"), src=os.path.join(self.build_folder,"..", "msvc","licenses"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

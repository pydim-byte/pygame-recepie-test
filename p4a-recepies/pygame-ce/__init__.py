import os
from os.path import join, exists
import re
from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from pythonforandroid.toolchain import current_directory
from pythonforandroid.logger import shprint
import sh

class Pygame2Recipe(CompiledComponentsPythonRecipe):
    version = "2.5.0"
    url = "https://github.com/pygame-community/pygame-ce/archive/refs/tags/{version}.tar.gz"
    site_packages_name = "pygame-ce"
    name = "pygame-ce"
    depends = ['sdl2', 'sdl2_image', 'sdl2_mixer', 'sdl2_ttf', 'setuptools', 'jpeg', 'png']
    call_hostpython_via_targetpython = False
    install_in_hostpython = False

    def prebuild_arch(self, arch):
        super().prebuild_arch(arch)
        build_dir = self.get_build_dir(arch.arch)
        with current_directory(build_dir):
            # 1. Neutralize [build-system] in pyproject.toml to disable mesonpy
            pyproject_path = join(build_dir, "pyproject.toml")
            if exists(pyproject_path):
                with open(pyproject_path, "r") as f:
                    pyproj_content = f.read()
                pyproj_content = re.sub(r'\[build-system\][\s\S]*?(?=\n\[|\Z)', '', pyproj_content)
                with open(pyproject_path, "w") as f:
                    f.write(pyproj_content)

            # 2. Patch Setup configuration for SDL2
            setup_template = open(join("buildconfig", "Setup.Android.SDL2.in")).read()
            env = self.get_recipe_env(arch)
            env['ANDROID_ROOT'] = join(self.ctx.ndk.sysroot, 'usr')
            png = self.get_recipe('png', self.ctx)
            png_lib_dir = join(png.get_build_dir(arch.arch), '.libs')
            png_inc_dir = png.get_build_dir(arch)
            jpeg = self.get_recipe('jpeg', self.ctx)
            jpeg_inc_dir = jpeg_lib_dir = jpeg.get_build_dir(arch.arch)
            sdl_mixer_includes = ""
            sdl2_mixer_recipe = self.get_recipe('sdl2_mixer', self.ctx)
            for include_dir in sdl2_mixer_recipe.get_include_dirs(arch):
                sdl_mixer_includes += f"-I{include_dir} "
            sdl2_image_includes = ""
            sdl2_image_recipe = self.get_recipe('sdl2_image', self.ctx)
            for include_dir in sdl2_image_recipe.get_include_dirs(arch):
                sdl2_image_includes += f"-I{include_dir} "
            setup_file = setup_template.format(
                sdl_includes=(
                    " -I" + join(self.ctx.bootstrap.build_dir, 'jni', 'SDL', 'include') +
                    " -L" + join(self.ctx.bootstrap.build_dir, "libs", str(arch)) +
                    " -L" + png_lib_dir + " -L" + jpeg_lib_dir + " -L" + arch.ndk_lib_dir_versioned),
                sdl_ttf_includes="-I"+join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_ttf'),
                sdl_image_includes=sdl2_image_includes,
                sdl_mixer_includes=sdl_mixer_includes,
                jpeg_includes="-I"+jpeg_inc_dir,
                png_includes="-I"+png_inc_dir,
                freetype_includes=""
            )
            open("Setup", "w").write(setup_file)

            # 3. Patch setup.py
            with open("setup.py", "r") as f:
                content = f.read()
            broken_line = "distutils.ccompiler.spawn(cmd, dry_run=self.dry_run, **kwargs)"
            fixed_line = "__import__('subprocess').check_call(cmd, **kwargs)"
            if broken_line in content:
                content = content.replace(broken_line, fixed_line)
            
            avx2_patch = "import platform as _p4a_platform\n_p4a_platform.machine = lambda: 'aarch64'\n"
            if avx2_patch not in content:
                content = avx2_patch + content
            
            with open("setup.py", "w") as f:
                f.write(content)

    def build_compiled_components(self, arch):
        hostpython_bin = self.hostpython_location
        # Ensure Cython is installed in hostpython environment
        shprint(
            sh.Command(hostpython_bin),
            '-m', 'pip', 'install', 'cython==3.0.11', '-q',
            _tail=20, _critical=True
        )
        super().build_compiled_components(arch)

    def install_python_package(self, arch, name=None, env=None, is_dir=True):
        if env is None:
            env = self.get_recipe_env(arch)
        env = dict(env)
        env['PIP_NO_BUILD_ISOLATION'] = '0' # Disable inside env as well
        
        # Override the pip arguments p4a uses to include --no-build-isolation
        with current_directory(self.get_build_dir(arch.arch)):
            shprint(
                self._host_recipe.pip,
                'install', '.',
                '--no-build-isolation',
                '--no-deps',
                '--compile',
                '--target', self.ctx.get_python_install_dir(arch.arch),
                _env=env,
                _tail=20,
                _critical=True
            )

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        env['USE_SDL2'] = '1'
        env["PYGAME_CROSS_COMPILE"] = "TRUE"
        env["PYGAME_ANDROID"] = "TRUE"
        return env

recipe = Pygame2Recipe()

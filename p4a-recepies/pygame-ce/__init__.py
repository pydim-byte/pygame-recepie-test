import os
from os.path import join
import sh
from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from pythonforandroid.toolchain import current_directory
from pythonforandroid.logger import shprint

class Pygame2Recipe(CompiledComponentsPythonRecipe):
    version = "2.5.0"
    url = "https://github.com/pygame-community/pygame-ce/archive/refs/tags/{version}.tar.gz"
    site_packages_name = "pygame-ce"
    name = "pygame-ce"
    depends = ['sdl2', 'sdl2_image', 'sdl2_mixer', 'sdl2_ttf', 'setuptools', 'jpeg', 'png']
    call_hostpython_via_targetpython = False  # Due to setuptools
    install_in_hostpython = False

    def prebuild_arch(self, arch):
        super().prebuild_arch(arch)
        with current_directory(self.get_build_dir(arch.arch)):
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
            with open("setup.py", "r") as f:
                content = f.read()
            broken_line = "distutils.ccompiler.spawn(cmd, dry_run=self.dry_run, **kwargs)"
            fixed_line = "__import__('subprocess').check_call(cmd, **kwargs)"
            if broken_line in content:
                content = content.replace(broken_line, fixed_line)
                print("Patched pygame-ce setup.py: fixed distutils.ccompiler.spawn call")
            else:
                print("WARNING: spawn patch target not found — check manually")
            avx2_patch = "import platform as _p4a_platform\n_p4a_platform.machine = lambda: 'aarch64'\n"
            if avx2_patch not in content:
                content = avx2_patch + content
                print("Patched pygame-ce setup.py: forced platform.machine() "
                      "to 'aarch64' to prevent incorrect -mavx2 injection")
            with open("setup.py", "w") as f:
                f.write(content)

    def build_compiled_components(self, arch):
        hostpython_bin = join(
            self.ctx.build_dir, 'other_builds', 'hostpython3', 'desktop',
            'hostpython3', 'native-build', 'root', 'usr', 'local', 'bin', 'python'
        )
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
        env['PIP_USE_PEP517'] = '0'
        
        # Pass flags to pip to prevent isolated build directory creation
        extra_args = ['--no-build-isolation', '--no-deps']
        
        print("Forcing --no-build-isolation and PIP_USE_PEP517=0 to bypass isolated build environment")
        super().install_python_package(arch, name=name, env=env, is_dir=is_dir, extra_args=extra_args)

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        env['USE_SDL2'] = '1'
        env["PYGAME_CROSS_COMPILE"] = "TRUE"
        env["PYGAME_ANDROID"] = "TRUE"
        return env

recipe = Pygame2Recipe()

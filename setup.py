from cx_Freeze import setup


build_exe_options = {
    'include_files': ['data'],
    'excludes': ['tkinter', 'unittest'],
}


setup(
    name='Coyote',
    version='0.1.0',
    description='Path generator for FTC Robotics',
    options={'build_exe': build_exe_options},
    executables=[{'script': 'main.py', 'base': 'gui'}],
)


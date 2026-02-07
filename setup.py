from cx_Freeze import setup


build_exe_options = {
    "include_files": ["field.png"],
    "excludes": ["tkinter", "unittest"],
}


setup(
    name="FTC Field",
    version="0.1.0",
    description="FTC Field Path Planner",
    options={"build_exe": build_exe_options},
    executables=[{"script": "main.py", "base": "gui"}],
)


import sys
import subprocess
import shutil


pyside6_rcc = shutil.which("pyside6-rcc")
if not pyside6_rcc:
    print("pyside6-rcc not found")
    sys.exit(1)


pyinstaller = shutil.which("pyinstaller")
if not pyinstaller:
    print("pyinstaller not found")
    sys.exit(1)


print("Generating resources_rc.py")
subprocess.check_call(
    [
        pyside6_rcc,
        "-o",
        "src/cocktail/resources/resources_rc.py",
        "resources/resources.qrc",
    ]
)

print("Building executable")
subprocess.check_call(
    [
        pyinstaller,
        "--clean",
        "--onefile",
        "--noconfirm",
        "--name",
        "cocktail",
        "src/cocktail/__main__.py",
    ]
)

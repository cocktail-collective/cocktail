#!/usr/bin/env python
import sys
import subprocess
import shutil
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--no-exe")

args = parser.parse_args()

pyside6_rcc = shutil.which("pyside6-rcc")
if not pyside6_rcc:
    print("pyside6-rcc not found")
    sys.exit(1)


pyinstaller = shutil.which("pyinstaller")
if not pyinstaller or args.no_exe:
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

if not args.no_exe:
    print("Building executable")
    subprocess.check_call(
        [
            pyinstaller,
            "--clean",
            "--onefile",
            "--noconfirm",
            "--name",
            "cocktail",
            "src/cocktail/ui/__main__.py",
        ]
    )

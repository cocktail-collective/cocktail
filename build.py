import argparse
import subprocess
import shutil


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dist", action="store_true")

    args = parser.parse_args()
    pyside6_rcc = shutil.which("pyside6-rcc")
    assert pyside6_rcc is not None, "pyside6-rcc not found"

    print("Generating resources_rc.py")

    subprocess.run(
        [
            pyside6_rcc,
            "-o",
            "src/cocktail/resources/resources_rc.py",
            "resources/resources.qrc",
        ]
    )

    if not args.dist:
        return

    pyinstaller = shutil.which("pyinstaller")
    assert pyinstaller is not None, "pyinstaller not found"

    print("Building executable")
    subprocess.run(
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


main()

import shutil
import subprocess
from setuptools import setup, find_namespace_packages

import setuptools.command.install


class Install(setuptools.command.install.install):
    """
    Generate resources_rc.py before building the source distribution.
    """

    def run(self):
        pyside6_rcc = shutil.which("pyside6-rcc")
        subprocess.check_call(
            [
                pyside6_rcc,
                "-o",
                "src/cocktail/resources/resources_rc.py",
                "resources/resources.qrc",
            ]
        )
        setuptools.command.install.install.run(self)


setup(
    name="cocktail",
    version="0.3.0",
    description="Cocktail",
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src"),
    install_requires=[
        "PySide6",
        "qtawesome",
        "platformdirs",
    ],
    entry_points={
        "console_scripts": [
            "cocktail = cocktail.__main__:main",
        ],
    },
    extras_require={
        "dev": ["pre-commit", "black", "pyinstaller"],
        "dist": ["pyinstaller"],
    },
    cmdclass={
        "install": Install,
    },
)

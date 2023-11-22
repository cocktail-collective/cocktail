import shutil
import subprocess
from setuptools import setup, find_namespace_packages

import setuptools.command.sdist
import setuptools.command.develop


class SDist(setuptools.command.sdist.sdist):
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
        setuptools.command.sdist.sdist.run(self)


setup(
    name="cocktail",
    version="0.2.0",
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
        "sdist": SDist,
    },
)

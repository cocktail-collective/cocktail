import setuptools
from setuptools import setup, find_namespace_packages


setup(
    name="cocktail",
    version="0.1.0",
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
)

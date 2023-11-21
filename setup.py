from setuptools import setup, find_namespace_packages

setup(
    name="cocktail",
    version="0.0.0",
    description="Cocktail",
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src"),
    install_requires=[
        "PySide6",
        "requests",
        "cachecontrol[filecache]",
        "filelock",
        "qtawesome",
        "backoff",
    ],
    entry_points={
        "console_scripts": [
            "cocktail = cocktail.__main__:main",
        ],
    },
)

import argparse
import sys
import platform
import subprocess


parser = argparse.ArgumentParser()
parser.add_argument("tag")
args = parser.parse_args()

if platform.system() == "Windows":
    artifact = f"dist/cocktail.exe#{platform.platform()}"
else:
    artifact = f"dist/cocktail#{platform.platform()}"


cmd = [
    "gh",
    "release",
    "upload",
    args.tag,
    artifact,
]

subprocess.check_call(cmd)

<center> <h1>🍸Cocktail Model Manager</h1></center>

![alt text](img/browser.jpg)

Cocktail is a standalone browser for Stable Diffusion models, designed with the goal of making managing your models easy and fast.
<br> <br>

## Installing
### Binary Releases

Download the latest [release](https://github.com/cocktail-collective/cocktail/releases/latest)


or install in a virual environment.

`Note: Git LFS is required to checkout this repository, without LFS Images will be missing.`

``` bash
git clone https://github.com/cocktail-collective/cocktail.git
cd cocktail
python3 -m venv venv
source venv/bin/activate
pip install .
python ci/build.py --skip-pyinstaller
cocktail
```

## Features

### 🚀 Fast Search
By utilising a local database Cocktail is able to offer a near instant search.

### 🗂️ Download Manager
Cocktail stores your downloaded models using configurable templates allowing 1 click downloads.

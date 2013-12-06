# -*- coding: utf-8 -*-
from setuptools import setup
import os
import platform

import pdfparanoia

long_description = open(os.path.join(os.path.dirname(__file__), "README.md")).read()

# pdfminer isn't cross-version compatible but a py3k port is in PyPI
if platform.python_version() >= "3.0.0":
    dependencies = ["pdfminer3k>=1.3.0"]
else:
    dependencies = ["pdfminer>=20131113"]

packages = [
    "pdfparanoia",
    "pdfparanoia.plugins",
]

setup(
    name="pdfparanoia",
    version=pdfparanoia.__version__,
    url="https://github.com/kanzure/pdfparanoia",
    license="BSD",
    author="Bryan Bishop",
    author_email="kanzure@gmail.com",
    maintainer="Bryan Bishop",
    maintainer_email="kanzure@gmail.com",
    description="pdf watermark remover library for academic papers",
    long_description=long_description,
    install_requires=dependencies,
    packages=packages,
    scripts=["bin/pdfparanoia"],
    platforms="any",
    zip_safe=False,
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        # Uses argparse and with statement; 2.7+
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
    ]
)

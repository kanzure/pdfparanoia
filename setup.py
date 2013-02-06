# -*- coding: utf-8 -*-
from setuptools import setup
import os

import pdfparanoia

long_description = open(os.path.join(os.path.dirname(__file__), "README.md")).read()

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
    packages=packages,
    install_requires=["pdfminer>=0"],
    platforms="any",
    zip_safe=False,
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        #"Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
    ]
)

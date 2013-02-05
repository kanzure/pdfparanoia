# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name="pdfparanoia",
    version="0.0.1",
    url="https://github.com/kanzure/pdfparanoia",
    license="BSD",
    author="Bryan Bishop",
    author_email="kanzure@gmail.com",
    description="pdf watermark remover library for academic papers",
    long_description=open("README.md", "r").read(),
    packages=["pdfparanoia"],
    zip_safe=False,
    include_package_data=True,
    install_requires=["pdfminer>=0", "pdfquery>=0"],
    platforms="any",
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

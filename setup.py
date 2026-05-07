# -*- coding: utf-8 -*-
from setuptools import setup
import os
import platform

import pdfparanoia

long_description = open(os.path.join(os.path.dirname(__file__), "README.md")).read()

# pdfminer is still required by publisher plugins (aip, ieee, jstor, rsc).
# pdfminer.six is the actively-maintained Python 3 fork.
# pikepdf is required by the CustomStrings plugin for TJ-aware content-stream
# and metadata scrubbing.
if platform.python_version() >= "3.0.0":
    dependencies = ["pdfminer.six", "pikepdf"]
else:
    dependencies = ["pdfminer>=20131113", "pikepdf"]

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
    long_description_content_type="text/markdown",
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

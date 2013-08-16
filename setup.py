#!/usr/bin/env python

#
# Copyright (c) 2013, Digium, Inc.
#

import os

from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="swagger.py",
    version="0.0.1",
    license="BSD 3-Clause License",
    description="Swagger code generator, using Python and mustache templates",
    long_description=read("README.md"),
    author="Digium, Inc.",
    url="https://github.com/leedm777/swagger.py",
    packages=['swagger'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    setup_requires = ['nose>=1.1'],
    tests_require = ['coverage'],
    install_requires = [
    ],
    entry_points = """
    [console_scripts]
    swagger.py = swagger:main
    """
)

#!/usr/bin/env python
# Copyright (c) 2013, Digium, Inc.
# Copyright (c) 2014-2015, Yelp, Inc.

import os

from setuptools import setup

import bravado

setup(
    name="bravado",
    version=bravado.version,
    license="BSD 3-Clause License",
    description="Library for accessing Swagger-enabled API's",
    long_description=open(os.path.join(os.path.dirname(__file__),
                                       "README.rst")).read(),
    author="Digium, Inc. and Yelp, Inc.",
    author_email="opensource+bravado@yelp.com",
    url="https://github.com/Yelp/bravado",
    packages=["bravado"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    install_requires=[
        "fido >= 1.0.1",
        "jsonref",
        "python-dateutil",
        "requests",
        "swagger-spec-validator",
        "yelp_uri",
    ],
)

#!/usr/bin/env python
# Copyright (c) 2013, Digium, Inc.
# Copyright (c) 2014-2016, Yelp, Inc.

import os

from setuptools import setup

import bravado

setup(
    name="bravado",
    # cloudlock version, no twisted dependency
    version=bravado.version + "-py3", 
    license="BSD 3-Clause License",
    description="Library for accessing Swagger-enabled API's",
    long_description=open(os.path.join(os.path.dirname(__file__),
                                       "README.rst")).read(),
    author="Digium, Inc. and Yelp, Inc.",
    author_email="opensource+bravado@yelp.com",
    url="https://github.com/Yelp/bravado",
    packages=["bravado"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
    ],
    install_requires=[
        "bravado-core >= 4.2.2",
        "yelp-bytes==0.3.0",
        "python-dateutil==2.8.0",
        "pyyaml",
        "requests==2.10.0",
        "six==1.12.0",
    ],
    extras_require={
    },
)

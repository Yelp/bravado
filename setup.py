#!/usr/bin/env python
# Copyright (c) 2013, Digium, Inc.
# Copyright (c) 2014, Yelp, Inc.

import os

from setuptools import setup

async_packages = ["crochet", "twisted"]

setup(
    name="swaggerpy",
    version="0.7.1",
    license="BSD 3-Clause License",
    description="Library for accessing Swagger-enabled API's",
    long_description=open(os.path.join(os.path.dirname(__file__),
                                       "README.rst")).read(),
    author="Digium, Inc. and Yelp, Inc.",
    author_email="opensource+swaggerpy@yelp.com",
    url="https://github.com/Yelp/swagger-py",
    packages=["swaggerpy"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    tests_require=[
        "nose",
        "tissue",
        "coverage",
        "ordereddict",
        "httpretty",
        "bottle"
    ],
    install_requires=[
        "requests",
        "python-dateutil",
        "crochet",
        "twisted",
    ],
)

#!/usr/bin/env python

#
# Copyright (c) 2013, Digium, Inc.
# Copyright (c) 2014, Yelp, Inc.
#

"""Setup script
"""

import os

from setuptools import setup

websocket_packages = ["websocket-client"]
async_packages = ["crochet", "twisted"]

setup(
    name="swaggerpy",
    version="0.5.1",
    license="BSD 3-Clause License",
    description="Library for accessing Swagger-enabled API's",
    long_description=open(os.path.join(os.path.dirname(__file__),
                                       "README.rst")).read(),
    author="Digium, Inc.",
    author_email="dlee@digium.com",
    url="https://github.com/Yelp/swagger-py",
    packages=["swaggerpy"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    tests_require=["nose", "tissue", "coverage", "httpretty"],
    install_requires=(["requests", "python-dateutil"] + websocket_packages +
        async_packages),
)

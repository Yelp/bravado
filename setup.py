#!/usr/bin/env python

#
# Copyright (c) 2013, Digium, Inc.
#

import os

from setuptools import setup

setup(
    name="swaggerpy",
    version="0.0.1",
    license="BSD 3-Clause License",
    description="Swagger code generator, using Python and mustache templates",
    long_description=open(os.path.join(os.path.dirname(__file__),
                                       "README.md")).read(),
    author="Digium, Inc.",
    url="https://github.com/leedm777/swaggerpy",
    packages=['swaggerpy'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    setup_requires=['nose>=1.3'],
    tests_require=['coverage', 'tissue', 'httpretty'],
    install_requires=['requests'],
    entry_points="""
    [console_scripts]
    swagger-codegen = swaggerpy.codegen:main
    """
)

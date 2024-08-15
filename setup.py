#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2013, Digium, Inc.
# Copyright (c) 2014-2016, Yelp, Inc.
import os

from setuptools import find_packages
from setuptools import setup

import bravado

setup(
    name='bravado',
    version=bravado.version,
    license='BSD 3-Clause License',
    description='Library for accessing Swagger-enabled API\'s',
    long_description=open(os.path.join(os.path.dirname(__file__),
                                       'README.rst')).read(),
    author='Digium, Inc. and Yelp, Inc.',
    author_email='opensource+bravado@yelp.com',
    url='https://github.com/Yelp/bravado',
    packages=find_packages(include=['bravado*']),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
    ],
    package_data={
        'bravado': ['py.typed'],
    },
    install_requires=[
        'bravado-core >= 5.16.1',
        'msgpack',
        'python-dateutil',
        'pyyaml',
        'requests >= 2.17',
        'six',
        'simplejson',
        'monotonic',
        'typing_extensions',
    ],
    extras_require={
        'fido': ['fido >= 4.2.1'],
        ':python_version<"3.5"': ['typing'],
        'integration-tests': [
            'bottle',
            'ephemeral_port_reserve',
            'pytest',
        ],
    },
    python_requires='!=3.0,!=3.1,!=3.2,!=3.3,!=3.4,!=3.5.0',
)

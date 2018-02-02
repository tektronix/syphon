#!python3
"""setup.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
import io
import os

from setuptools import find_packages, setup

# Package meta-data
NAME = 'syphon'
DESCRIPTION = 'A storage and management engine for CSV data.'
URL = 'https://github.com/ethall/syphon'
EMAIL = 'evan.tom.hall@gmail.com'
AUTHOR = 'Evan Hall'

# Required packages
REQUIRED = [
    'pandas'
]

HERE = os.path.abspath(os.path.dirname(__file__))

# Import README to use as the long-description
with io.open(os.path.join(HERE, 'README.rst'), encoding='utf-8') as f:
    LONG_DESCRIPTION = '\n' + f.read()

setup(
    name=NAME,
    version='1.3.0',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages(),
    install_requires=REQUIRED,
    include_package_data=True,
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering'
    ]
)

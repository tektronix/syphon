#!/usr/bin/env python
"""setup.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
import io
import os
import versioneer
from setuptools import find_packages, setup

from syphon import __url__

HERE = os.path.abspath(os.path.dirname(__file__))

# Import README to use as the long-description
with io.open(os.path.join(HERE, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = '\n' + f.read()

# Trove classifiers
# Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Operating System :: Microsoft :: Windows',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Topic :: Scientific/Engineering',
]

PROJECT_URLS = {
    'Source': 'https://github.com/ethall/syphon',
    'Tracker': 'https://github.com/ethall/syphon/issues',
}

INSTALL_REQUIRES = [
    'pandas',
    'sortedcontainers'
]

EXTRAS_REQUIRE = {
    'dev': ['check-manifest'],
    'test': [
        'tox',
        'pytest',
        'pytest-cov',
    ],
}

setup(
    name='syphon',
    version=versioneer.get_version(),
    description='A data storage and management engine.',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url=__url__,
    author='Evan Hall',
    license='MIT',
    classifiers=CLASSIFIERS,
    project_urls=PROJECT_URLS,
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    python_requires='>=3,!=3.0.*,!=3.2.*,!=3.3.*,!=3.4.*,<4',
    maintainer='Keithley Instruments, LLC. et al.',
    include_package_data=True,
    cmdclass=versioneer.get_cmdclass(),
)

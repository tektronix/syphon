#!/usr/bin/env python
"""setup.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
import io
import os
from setuptools import find_packages, setup

import versioneer

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
    'Source': 'https://github.com/tektronix/syphon',
    'Tracker': 'https://github.com/tektronix/syphon/issues',
}

INSTALL_REQUIRES = [
    'pandas<=0.23.*',
    'sortedcontainers<=1.6.*'
]

EXTRAS_REQUIRE = {
    'dev': ['check-manifest'],
    'test': [
        'tox',
        'pylint',
        'pytest',
        'pytest-cov',
    ],
}

ENTRY_POINTS = {
    'console_scripts': [
        'syphon=syphon.__main__:bootstrap'
    ]
}

setup(
    name='syphon',
    version=versioneer.get_version(),
    description='A data storage and management engine.',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://github.com/tektronix/syphon',
    author='Evan Hall',
    license='MIT',
    classifiers=CLASSIFIERS,
    project_urls=PROJECT_URLS,
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    python_requires='>=3,!=3.0.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.7.*,<4',
    entry_points=ENTRY_POINTS,
    maintainer='Keithley Instruments, LLC. et al.',
    include_package_data=True,
    cmdclass=versioneer.get_cmdclass(),
)

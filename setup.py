#!/usr/bin/env python
"""setup.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
import io
import os

from setuptools import find_packages, setup

HERE = os.path.abspath(os.path.dirname(__file__))

# Manually import versioneer.
versioneer = {}
with open(os.path.join(HERE, "versioneer.py")) as fp:
    exec(fp.read(), versioneer)

# Import README to use as the long-description
with io.open(os.path.join(HERE, "README.md"), encoding="utf-8") as f:
    LONG_DESCRIPTION = "\n" + f.read()

# Trove classifiers
# Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Topic :: Scientific/Engineering",
    "Topic :: Utilities",
]

PROJECT_URLS = {
    "Source": "https://github.com/tektronix/syphon",
    "Tracker": "https://github.com/tektronix/syphon/issues",
}

INSTALL_REQUIRES = ["pandas<0.26", "sortedcontainers~=2.1"]

ENTRY_POINTS = {"console_scripts": ["syphon=syphon.__main__:main"]}

setup(
    name="syphon",
    version=versioneer["get_version"](),
    description="A CSV data storage and management engine.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/tektronix/syphon",
    author="Evan Hall",
    license="MIT",
    classifiers=CLASSIFIERS,
    project_urls=PROJECT_URLS,
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    python_requires=">=3,!=3.0.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*,<4",
    entry_points=ENTRY_POINTS,
    maintainer="Keithley Instruments, LLC. et al.",
    include_package_data=True,
    cmdclass=versioneer["get_cmdclass"](),
)

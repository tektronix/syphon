# Syphon

> A data storage and management engine.

[![build](https://api.travis-ci.com/tektronix/syphon.svg?branch=master)](https://travis-ci.com/tektronix/syphon) [![codecov](https://codecov.io/gh/tektronix/syphon/branch/master/graph/badge.svg)](https://codecov.io/gh/tektronix/syphon) [![PyPI](https://img.shields.io/pypi/v/syphon.svg)](https://pypi.org/project/syphon/) [![PyPI - License](https://img.shields.io/pypi/l/syphon.svg)](https://pypi.org/project/syphon/)

Syphon is a Python package that provides a simple interface to perform common tasks on labelled data.  Its aim is to fit seamlessly into any automation pipeline that requires organization and collation of large datasets.


## Features

* Archive file(s) into a data storage directory.
* Automatic archive organization based on the value of a data column (if a `.schema.json` file is present).
* Combine new data with additional "meta" data before archival.
* Build a single data file from the contents of the archive directory.
* Initialize new archive directories by creating a new `.schema.json` file.


## Basic Usage

Archive a single file or multiple files with a wildcard pattern:
```
python -m syphon archive ./storage/folder -d /path/to/data.csv

python -m syphon archive ./storage/folder -d /path/to/*.csv
```

Build a single data file from an archive directory:
```
python -m syphon build /path/to/storage/folder all_data.csv
```

General command line documentation and subcommand documentation can be accessed via
```
 python -m syphon --help

 python -m syphon SUBCOMMAND --help
```


## Contribute

See a typo? Know how to fix an issue? Implement a requested feature?

We'd love to accept your patches and contributions! The [Contributing](CONTRIBUTING.md) document guides you through checkout, unit testing, and building.


## Maintainer

* [Evan Hall](https://github.com/ethall)


## Disclaimer

This is not an officially supported Tektronix product. It is maintained by a small group of employees in their spare time. We lack the resources typical of most Tektronix products, so please bear with us! We will do our best to address your issues and answer any questions directly related to this extension in a timely manner.


## License

Copyright Keithley Instruments, LLC. All rights reserved.

Licensed under the [MIT](License) License.
<br/>
<br/>
<br/>
Made with &#10084; at Keithley Instruments

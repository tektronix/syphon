# Syphon

> A CSV data storage and management engine.

[![build](https://api.travis-ci.com/tektronix/syphon.svg?branch=master)](https://travis-ci.com/tektronix/syphon) [![codecov](https://codecov.io/gh/tektronix/syphon/branch/master/graph/badge.svg)](https://codecov.io/gh/tektronix/syphon) [![CodeFactor](https://www.codefactor.io/repository/github/tektronix/syphon/badge)](https://www.codefactor.io/repository/github/tektronix/syphon) [![PyPI](https://img.shields.io/pypi/v/syphon)](https://pypi.org/project/syphon/) [![PyPI - License](https://img.shields.io/pypi/l/syphon.svg)](https://pypi.org/project/syphon/)

[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

[![Keithley](https://tektronix.github.io/media/Keithley-opensource_badge-flat.svg)](https://github.com/tektronix)

Syphon is a Python package that provides a simple interface to perform common tasks on labelled data.  Its aim is to fit seamlessly into any automation pipeline that requires organization and collation of large datasets.


## Features

* Archive file(s) into a data storage directory.
  * Automatic archive organization based on the value of a data column (if a `.schema.json` file is present).
  * Quickly append new archive files onto a previously built data file.
* Build a single data file from the contents of the archive directory.
* Initialize new archive directories by creating a storage schema (`.schema.json`) file.


## Basic Usage

Initialize an archive directory:
```
python -m syphon init ./storage/folder some_column_header "another column header"
```

Archive one or more files with direct paths, wildcard patterns, or a combination of both:
```
python -m syphon archive /path/to/data.csv ./storage/folder

python -m syphon archive /path/to/data.csv /path/to/more/*.csv ./storage/folder
```

Build a single data file from an archive directory:
```
python -m syphon build ./storage/folder all_data.csv
```

Archive additional data and append it to a previously built data file:
```
python -m syphon archive /path/to/still/more/*.csv ./storage/folder -i all_data.csv
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

Licensed under the [MIT](LICENSE) License.
<br/>
<br/>
<br/>
Made with &#10084; at Keithley Instruments

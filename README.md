syphon
======

> A data storage and management engine.

**syphon** is a Python package that provides a simple interface to perform common tasks on labelled data.  Its aim is to fit seamlessly into any automation pipeline that requires organization and collation of large datasets.

Features
========

* Archive file(s) into a data storage directory.
* Automatic archive organization based on the value of a data column (if a `.schema.json` file is present).
* Combine new data with additional "meta" data before archival.
* Build a single data file from the contents of the archive directory.
* Initialize new archive directories by creating a new `.schema.json` file.

Basic Usage
===========

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

For detailed documentation, check out the [wiki](https://github.com/ethall/syphon/wiki).

Unit Testing
============

Install the `tox` and `pytest` packages via pip:
```
pip install tox pytest
```

Run quick tests (or all tests) against all available python environments:
```
tox [-- --slow]
```

Print all available test environments and test against only one:
```
tox --listenvs
...     # list of environments

tox -e ENV [-- --slow]
```

License
=======

Copyright (c) Keithley Instruments, LLC. All rights reserved.

Licensed under the [MIT](License) License.

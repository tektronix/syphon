# Contributing Guide

Syphon is a part-time effort from a small team, so contributions are welcome! This document shows you how to get the project, run all provided tests, and generate a production-ready build.


## Dependencies

To make sure that the following instructions work, install the following dependencies on your machine:

- Python 3.6
- Git


## Installation

To retrieve the Syphon source code, clone the git repository with:

````
$ git clone https://github.com/tektronix/syphon
````

This will clone the complete source to your local machine.

Syphon uses [**pipx**](https://pipxproject.github.io/pipx/) to create and maintain an isolated installation environment:

````
$ python3.6 -m pip install --user pipx
$ python3.6 -m pipx ensurepath
````

[**pipenv**](https://pipenv.kennethreitz.org/en/latest/) is used for its Pipfile support. To install it and all dependencies, navigate to the project directory and run:

````
$ pipx install pipenv
$ pipenv install --dev
````

This this will install everything required to package and test the project.

### Ignoring `.vscode/settings.json`

> 🚨 SECURITY WARNING 🚨

If you're using Visual Studio Code with the Python plugin, be sure to run
```
$ git update-index --assume-unchanged .vscode/settings.json
```
so you don't accidentally commit the `python.pythonPath` field and leak your personal directory information!


## Code Quality

### Formatting: `python ./scripts/format.py`

Performs automatic formatting on all source files.


### Linting: `python ./scripts/lint.py`

Performs linting on all source files.


## Testing

Syphon uses [**tox**](https://tox.readthedocs.io/en/latest/) for its environment management, [**pytest**](https://docs.pytest.org/en/latest/contents.html) for its testing framework, and [**pytest-cov**](https://pytest-cov.readthedocs.io/en/latest/) to calculate test coverage.


### Unit Testing: `pipenv run tox [-- --slow]`

Executes quick tests (or all tests) against all supported Python environments, including formatting and linting checks. Code coverage is automatically calculated after all tests are performed.

### Targeted Unit Testing

Testing can be performed against a specific environment with
```
$ pipenv run tox -e ENV [-- --slow]
```
where `ENV` is a supported environment, a list of which can be viewed by running
```
$ pipenv run tox --listenvs
```

Unit test files are located in [`syphon/tests`](/syphon/tests). To run a single test file, you should call `pytest` directly:
```
$ pipenv run pytest syphon/test/test_something.py
```


## Contributing/Submitting Changes

* Create a fork from the latest `canary` branch and name it what you intend to do.
    * Branch names should start with:
        * `topic/`
        * `feature/`
        * `bugfix/`
    * Use one branch per feature/bugfix.
    * Words in the branch name should be hyphen (`-`) delimited.
    * Example:
        ```
        $ git remote update && git fetch
        $ git checkout -b topic/speed-improvements origin/canary
        ```
* Make your changes.
    * Add or edit unit tests as appropriate.
    * Run `tox`.
        * Ensure no linting errors are present.
        * All unit tests must pass.
        * Coverage should be the same or better than when you started.
* Commit your changes.
    * Each commit should be as limited in scope as possible.
    * Ensure your commit messages are concise.
* Submit a pull request.
    * Make sure your PR is against the `canary` branch.

Your pull request will serve as a code review. All submissions, including those by project members, require review.


## Contributor License Agreement

Contributions to this project must be accompanied by a Contributor License Agreement. You (or your employer) retain the copyright to your contribution; this simply gives us permission to use and redistribute your contributions as part of the project.

You generally only need to submit a CLA once, so if you've already submitted one (even if it was for a different project), you probably don't need to do it again.



<!-- Modified by Tektronix. Original Content developed by the angular-translate team and Pascal Precht and their Contributing Guide available at https://github.com/angular-translate/angular-translate -->

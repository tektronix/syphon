# Releasing Syphon

This document records the rite of Software Release for the Syphon project. This practice is observed in two forms, Continuous and Manual, both recorded here for posterity.

The **Continuous Deployment** section documents the steps required to perform the ceremony automatically (via [Travis-CI](https://travis-ci.com/tektronix/syphon)) after a successful build on any Tag branch. It assumes that you'll be configuring continuous deployment from scratch following some unknown cataclysm. This method is recommended.

The **Manual Deployment** section documents how to perform a Software Release by hand. It is not a long-term alternative to Continuous Deployment, but simply a 


# Continuous Deployment


## Requirements

To properly configure continuous deployments, we need the following:

* A Linux distro (Ubuntu 14.04 LTS will be used in subsequent steps)
* Internet access


## Setup

In your Linux distro, install the following (if necessary):

* Ruby 2.0+

In Ubuntu, the available Ruby version from the Canoncial package index was capped at 1.9. Therefore the following was executed:

```
$ sudo apt-add-repository ppa:brightbox/ruby-ng
$ sudo apt update
```

Run a package search to find your latest Ruby version. At the time of writing, this was 2.5. The `ruby-switch` package and command is only necessary if Ruby is already installed.

```
$ sudo apt install ruby2.5 ruby-switch
$ sudo ruby-switch --set ruby2.5
$ sudo apt install ruby2.5-dev
```

### travis.rb

The next step is to install the official Travis-CI command-line utility. The exact command is documented [here](https://github.com/travis-ci/travis.rb#installation). At the time of this writing, the most recent version was `1.8.9`, so the following was executed:

```
$ sudo gem install travis -v 1.8.9 --no-rdoc --no-ri
```

Next you must login to your Travis-CI account:

```
$ travis login --pro
```

### PyPI Password

<span style="color:red"><b>Special characters in a PyPI password will cause problems.</b></span> Ensure the password of the target PyPI account does not contain symbols.

For more details see [travis-ci/dpl/issues/377](https://github.com/travis-ci/dpl/issues/377).

## Encrypting

Be sure to call

```
$ set +o history
```
to turn off command history before continuing.

Follow the Travis-CI [PyPI deployment](https://docs.travis-ci.com/user/deployment/pypi/) instructions (the opening section) to encrypt the password for the Tektronix PyPI account. You will need to add `--repo tektronix/syphon` to the `travis encrypt` command (see above link) if you're not running it from the root of the project directory.

Once complete, toggle command history back on with

```
$ set -o history
```


# Manual Deployment


## Requirements

The latest versions of the following Python packages:

* setuptools
* wheel
* twine


## Tag

In the master branch, create a new Tag:

```
$ git tag vM.m.p
```
where `M` is the major version, `m` is the minor version, and `p` is the patch version. These should follow [Semantic Versioning](https://semver.org/) rules.

Follow that up with

```
$ git push --tags
```
to update origin.


## Build

From the `master` branch in the root directory of the project, create a source archive and a built distribution:

```
$ python3 setup.py sdist bdist_wheel
```

Syphon utilizes [Python Versioneer](https://github.com/warner/python-versioneer) for automatic version management. Therefore, unless something was edited since the new tag was created, the created files should follow a `syphon-M.m.p` naming convention.


## Upload

Posting the built packages to the Package Index can be done with the following command run from the root directory of the project:

```
$ python3 -m twine upload dist/*
```

You will be prompted for your username and password.

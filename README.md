# CloudBlue Connect Command Line Interface

![pyversions](https://img.shields.io/pypi/pyversions/connect-cli.svg) [![PyPi Status](https://img.shields.io/pypi/v/connect-cli.svg)](https://pypi.org/project/connect-cli/) [![Build Status](https://travis-ci.org/cloudblue/connect-cli.svg?branch=master)](https://travis-ci.org/cloudblue/connect-cli) [![codecov](https://codecov.io/gh/cloudblue/connect-cli/branch/master/graph/badge.svg)](https://codecov.io/gh/cloudblue/connect-cli) [![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=connect-cli&metric=alert_status)](https://sonarcloud.io/dashboard?id=connect-cli)


## Introduction

The CloudBlue Connect Command Line Interface (CLI) is an extensible unified tool to perform various automation scenarios. With just one tool, you can control multiple Connect modules from the command line and automate them through scripts.

Since it is extensible, user can write your own plugins to extend its functionalities.


## Install

### Prerequisites

`connect-cli` depends on [Cairo](https://www.cairographics.org/), [Pango](https://pango.gnome.org/) and 
[GDK-PixBuf](https://developer.gnome.org/gdk-pixbuf/stable/).

Please refers to the platform-specific instructions on how to install these dependecies:

* [Linux](docs/linux_deps_install.md)
* [Mac OSX](docs/osx_deps_install.md)
* [Windows](docs/win_deps_install.md)


### Using PIP

To use `connect-cli` you need a system with python 3.6 or later installed.

```sh
    $ pip install --upgrade connect-cli
```    

### Binary distributions

A single executable binary distribution is available for windows, linux and mac os x.
You can it from the [Github Releases](https://github.com/cloudblue/connect-cli/releases) page.

To install under linux:

```
    $ curl -O -J https://github.com/cloudblue/connect-cli/releases/download/xx.yy/connect-cli_xx.yy_linux_amd64.tar.gz
    $ tar xvfz connect-cli_xx.yy_linux_amd64.tar.gz
    $ sudo cp dist/ccli /usr/local/bin/ccli
```

To install under Mac OS X:

```
    $ curl -O -J https://github.com/cloudblue/connect-cli/releases/download/xx.yy/connect-cli_xx.yy_osx_amd64.tar.gz
    $ tar xvfz connect-cli_xx.yy_osx_amd64.tar.gz
    $ sudo cp dist/ccli /usr/local/bin/ccli
```

> If your user is not a sudoer, you can copy the `ccli` executable from the dist directory to a directory of your choice
> that is listed in the `PATH` variable.


To install under Windows

Download the windows single executable zipfile from [Github Releases](https://github.com/cloudblue/connect-cli/releases/download/xx.yy/connect-cli_xx.yy_windows_amd64.zip), extract it and place it in a folder that is included in your `PATH` system variable.


## Usage

* [General](docs/core_usage.md)
* [Products](docs/products_usage.md)
* [Customers](docs/customers_usage.md)
* [Reports](docs/reports_usage.md)


## Run tests

`connect-cli` uses [poetry](https://python-poetry.org/) for dependencies management and packaging.

To run the `connect-cli` tests suite run:

```
$ pip install poetry
$ poetry install
$ poetry run pytest
```



## License

`connect-cli` is released under the [Apache License Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).

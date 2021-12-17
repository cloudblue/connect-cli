# CloudBlue Connect Command Line Interface

![pyversions](https://img.shields.io/pypi/pyversions/connect-cli.svg) [![PyPi Status](https://img.shields.io/pypi/v/connect-cli.svg)](https://pypi.org/project/connect-cli/) ![PyPI - Downloads](https://img.shields.io/pypi/dm/connect-cli) ![Docker Pulls](https://img.shields.io/docker/pulls/cloudblueconnect/connect-cli) ![GitHub Workflow Status](https://img.shields.io/github/workflow/status/cloudblue/connect-cli/Build%20Connect%20Command%20Line%20Client) [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=connect-cli&metric=coverage)](https://sonarcloud.io/summary/new_code?id=connect-cli) [![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=connect-cli&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=connect-cli)

## Introduction

The CloudBlue Connect Command Line Interface (CLI) is an extensible unified tool to perform various automation scenarios. With just one tool, you can control multiple Connect modules from the command line and automate them through scripts.

Since it is extensible, users can write their own plugins to extend its functionalities.


## Install

### Prerequisites

`connect-cli` depends on [Git](https://git-scm.com/), [Cairo](https://www.cairographics.org/),
[Pango](https://pango.gnome.org/) and [GDK-PixBuf](https://developer.gnome.org/gdk-pixbuf/stable/).

Please refers to the platform-specific instructions on how to install these dependecies:

* [Linux](docs/linux_deps_install.md)
* [Mac OS](docs/osx_deps_install.md)
* [Windows](docs/win_deps_install.md)


### Using PIP

To use `connect-cli` you need a system with python 3.8 or later installed.

```sh
    $ pip install --upgrade connect-cli
```

### Using Docker

To use the Docker image of `connect-cli`:

```sh
    $ docker run -it -v $HOME/.ccli:/home/connect/.ccli cloudblueconnect/connect-cli ccli
```

Please refer to the [`connect-cli` docker image documentation](https://hub.docker.com/r/cloudblueconnect/connect-cli) for more information.


### Using Homebrew on Mac OS

To install `connect-cli` with homebrew run:

```sh
    $ brew update
    $ brew tap cloudblue/connect
    $ brew install cloudblue/connect/connect-cli
```

### Using the installer on Windows

An installer package is available for Windows 10 or newer.
You can download its zip file from the [Github Releases](https://github.com/cloudblue/connect-cli/releases) page.



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

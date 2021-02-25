# CloudBlue Connect Command Line Interface

![pyversions](https://img.shields.io/pypi/pyversions/connect-cli.svg) [![PyPi Status](https://img.shields.io/pypi/v/connect-cli.svg)](https://pypi.org/project/connect-cli/) [![Build Status](https://travis-ci.org/cloudblue/connect-cli.svg?branch=master)](https://travis-ci.org/cloudblue/connect-cli) [![codecov](https://codecov.io/gh/cloudblue/connect-cli/branch/master/graph/badge.svg)](https://codecov.io/gh/cloudblue/connect-cli) [![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=connect-cli&metric=alert_status)](https://sonarcloud.io/dashboard?id=connect-cli)


## Introduction

The CloudBlue Connect Command Line Interface (CLI) is a unified tool to perform various automation scenarios. With just one tool, you can control multiple Connect modules from the command line and automate them through scripts.

`connect-cli` allow users to export/synchronize the items of a product to/from an Excel workbook.


## Install

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
    $ curl -O -J https://github.com/cloudblue/connect-cli/releases/download/21.12/connect-cli_21.12_linux_amd64.tar.gz
    $ tar xvfz connect-cli_21.3_linux_amd64.tar.gz
    $ sudo cp dist/ccli /usr/local/bin/ccli
```

To install under Mac OS X:

```
    $ curl -O -J https://github.com/cloudblue/connect-cli/releases/download/21.12/connect-cli_21.12_osx_amd64.tar.gz
    $ tar xvfz connect-cli_21.3_osx_amd64.tar.gz
    $ sudo cp dist/ccli /usr/local/bin/ccli
```

> If your user is not a sudoer, you can copy the `ccli` executable from the dist directory to a directory of your choice
> that is listed in the `PATH` variable.


To install under Windows

Download the windows single executable zipfile from [Github Releases](https://github.com/cloudblue/connect-cli/releases/download/21.12/connect-cli_21.12_windows_amd64.zip), extract it and place it in a folder that is included in your `path` system variable.


## Usage

### Add a new account

First of all you need to add an account the `connect-cli` with the CloudBlue Connect API *key*.

```
    $ ccli account add "ApiKey XXXXX:YYYYY"
```

### List configured accounts

To get a list of all configured account run:

```
    $ ccli account list
```


### Set the current active account

To set the current active account run:

```
    $ ccli account activate VA-000-000
```

### Remove an account

To remove an account run:

```
    $ ccli account remove VA-000-000
```

### List available products

To get a list of available products run:

```
    $ ccli product list
```

This command will output a list of all products (id and name) available within the current active account.
You can also filter the results by adding the ``--query`` flag followed by a RQL query.
For more information about RQL see the [Resource Query Language](https://connect.cloudblue.com/community/api/rql/)
article in the Connect community documentation portal.


### Export a product to Excel

To export a product to Excel run:

```
    $ ccli product export PRD-000-000-000
```

This command will generate a excel file named PRD-000-000-000.xlsx in the current working directory.


### Synchronize a product from Excel

To synchronize a product from Excel run:

```
    $ ccli product sync PRD-000-000-000
```


### Clone a product

To clone a product you can run this command:

```
    $ ccli product clone PRD-000-000-000
```

this command also accepts as additional parameters:

* -s: to specify the source account
* -d: to specify the destination account
* -n: to specify the name for the cloned one 


### Reports

Multiple reports are available to the Connect-cli tool, additionally you can create your owns and run them

to list available reports you can run:

```
    $ ccli report list
```

to execute a concrete report, you must get the id from the list before and execute:

```
    $ ccli report execute {ID}
```

for example:

```
    $ ccli report execute fulfillment_requests
```

### Getting help

To get help about the `connect-cli` commands type:

```
    $ ccli --help
```

## License

`connect-cli` is released under the [Apache License Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).

# Connect Product Synchronizer

![pyversions](https://img.shields.io/pypi/pyversions/product-sync.svg)  [![PyPi Status](https://img.shields.io/pypi/v/product-sync.svg)](https://pypi.org/project/product-sync/)  [![Build Status](https://travis-ci.org/cloudblue/product-sync.svg?branch=master)](https://travis-ci.org/cloudblue/product-sync)


## Introduction

CloudBlue Connect is a supply automation platform that manages your products and services, contracts, 
ordering and fulfillment, usage and subscriptions. 

It supports any product, from physical goods to cloud products, as well as any channel, including your 
direct and indirect sales channels and internal procurement. 

With its flexible APIs, it can connect to any commerce platform.

Vendors can leverage CloudBlue Connect to:

* Reduce the total cost of ownership for homegrown technology supporting their indirect channel
* Standardize integrations with partners
* Increase efficiencies and minimize redundancies by bridging their direct and indirect sales channels

Service providers can use CloudBlue Connect to:

* Define, manage and distribute any type of product (omni-product) through any channel (omni-channel)
* Transform perpetual licensed products into a subscription model
* Onboard new products into their portfolio quickly to build and deliver unique solutions to end customers

`product-sync` allow users to export/synchronize the items of a product to/from an Excel workbook.


## Install

### Using a virtualenv

To use `product-sync` you need any *nix system with python 3.6 or later installed.

The preferred way to install `product-sync` is using a [virtualenv](https://virtualenv.pypa.io/en/latest/):

```
    $ virtualenv psync
    $ source pysync/bin/activate
    $ pip install product-synchronizer
```    

### Binary distributions

A single executable binary distribution is available for both linux and mac osx (amd64).
You can it from the [Github Releases](https://github.com/cloudblue/product-sync/releases) page.

To install under linux:

```
    $ curl -O -J https://github.com/cloudblue/product-sync/releases/download/1.2/product-sync_1.2_linux_amd64.tar.gz
    $ tar xvfz product-sync_1.2_linux_amd64.tar.gz
    $ sudo cp dist/ccli /usr/local/bin/ccli
```

To install under Mac OSX:

```
    $ curl -O -J https://github.com/cloudblue/product-sync/releases/download/1.2/product-sync_1.2_osx_amd64.tar.gz
    $ tar xvfz product-sync_1.2_linux_amd64.tar.gz
    $ sudo cp dist/ccli /usr/local/bin/ccli
```

> If your user is not a sudoer, you can copy the `ccli` executable from the dist directory to a directory of your choice
> that is listed in the `PATH` variable.


## Usage

### Configure

First of all you need to configure the `product-sync` with the CloudBlue Connect API *endpoint* and *key*.

```
    $ ccli configure --url https://api.connect.cloudblue.com/public/v1 --key "ApiKey XXXXX:YYYYY"
```

### Dump products to Excel

To dump products to Excel run:

```
    $ ccli product dump PRD-000-000-000 PRD-000-000-001 PRD-000-000-002 --out my_products.xlsx
```


### Synchronize products 

To sync products from Excel run:

```
    $ ccli product sync --in my_products.xlsx
```


## License

`product-sync` is released under the [Apache License Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).

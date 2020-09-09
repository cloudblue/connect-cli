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


## Requirements

To use `product-sync` you need any *nix system with python 3.6 or later installed.

## Install

The preferred way to install `product-sync` is using a [virtualenv](https://virtualenv.pypa.io/en/latest/):

```
    $ virtualenv psync
    $ source pysync/bin/activate
    $ pip install product-synchronizer
```    

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



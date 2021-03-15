# Products management

The products management area offers useful commands to list, export, synchronize and clone a product definition.

To access the group of commands related to the management of products you must invoke the CLI with the `product` command:

```sh
$ ccli product

Usage: ccli product [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  clone   Create a clone of a product.
  export  Export a product to an excel file.
  list    List products.
  sync    Synchronize a product from an excel file.
```


## List products

To get a list of available products run:

```
    $ ccli product list
```

This command will output a list of all products (id and name) available within the current active account.
You can also filter the results by adding the ``--query`` flag followed by a RQL query.
For more information about RQL see the [Resource Query Language](https://connect.cloudblue.com/community/api/rql/)
article in the Connect community documentation portal.


## Export a product to Excel

To export a product to Excel run:

```
    $ ccli product export PRD-000-000-000
```

This command will generate a excel file named PRD-000-000-000.xlsx in the current working directory.


## Synchronize a product from Excel

To synchronize a product from Excel run:

```
    $ ccli product sync PRD-000-000-000
```


## Clone a product

To clone a product you can run this command:

```
    $ ccli product clone PRD-000-000-000
```

this command also accepts as additional parameters:

* -s: to specify the source account
* -d: to specify the destination account
* -n: to specify the name for the cloned one 
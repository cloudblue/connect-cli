# Customers management

The customers management area offers commands to export and synchronize customers
to/from an excel file.

To access the group of commands related to the management of customers you must invoke the CLI with the `customer` command:

```sh
$ ccli customer

Usage: ccli customer [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  export  Export customers to an excel file.
  sync    Synchronize customers from an excel file.
```


## Export customers

To export customers data to an excel file type:

```sh
$ ccli customer export
```

This command will create a folder named with the current active account ID and
will generate a customers.xlsx file within that folder.

## Syncrhonize customers

To synchronize customers from an excel file type:

```sh
$ ccli customer sync customers.xlsx
```

This command will output the total number of processed customers
and how many of them have been created, updated, deleted, skipped or generate an error.

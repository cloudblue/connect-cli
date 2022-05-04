# Translations management

The translations management area offers a command to export translations. A command to synchronize translations is in progress.

To access the group of commands related to the management of translations you must invoke the CLI with the `translation` command:

```sh
$ ccli translation

Usage: ccli translation [OPTIONS] COMMAND [ARGS]...

Options:
  -h, --help  Show this message and exit.

Commands:
  export  Export a translation and its attributes to an excel file.
```


## Export a translation to Excel

To export a translation and its attributes to Excel run:

```
    $ ccli translation export TRN-000-000-000
```

This command will generate a excel file named TRN-000-000-000.xlsx in the current working directory.

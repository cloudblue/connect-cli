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
  list    List translations.
```

## List translation options

To get the options for the translation list command run:

```sh
$ ccli translation list -h

Usage: ccli translation list [OPTIONS]

Options:
  -q, --query TEXT         RQL query expression.
  -p, --page-size INTEGER  Number of translations per page.
  -c, --always-continue    Do not prompt to continue.
  -h, --help               Show this message and exit.
```
You can also filter the results by adding the ``--query`` flag followed by a RQL query.
For more information about RQL see the [Resource Query Language](https://connect.cloudblue.com/community/api/rql/)
article in the Connect community documentation portal.

## List translation command
```sh
$ ccli translation list
```
This command will output a list of all translations (id, context id, context type, context name,locale name, auto, status, primary, owner) available within the current active account in a nice table format way:

```sh
┌──────────────────┬───────────────┬────────────┬────────────────────────┬───────┬────┬────────┬───────┬─────┐
│ID                │Context_ID     │Context_Type│      Context_Name      │ Locale│Auto│ Status │Primary│Owner│
├──────────────────┼───────────────┼────────────┼────────────────────────┼───────┼────┼────────┼───────┼─────┤
│TRN-0000-0000-0000│PRD-999-999-999│  product   │Product P00 for John Doe│English│off │inactive│   ✓   │  ✓  │
└──────────────────┴───────────────┴────────────┴────────────────────────┴───────┴────┴────────┴───────┴─────┘
```

## Export a translation to Excel

To export a translation and its attributes to Excel run:

```
    $ ccli translation export TRN-000-000-000
```

This command will generate a excel file named TRN-000-000-000.xlsx in the current working directory.

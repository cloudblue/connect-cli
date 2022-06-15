# Translations management

The translations management area offers a command to export translations. A command to synchronize translations is in progress.

To access the group of commands related to the management of translations you must invoke the CLI with the `translation` command:

```sh
$ ccli translation

Usage: ccli translation [OPTIONS] COMMAND [ARGS]...

Options:
  -h, --help  Show this message and exit.

Commands:
  activate   Active a translation.
  export     Export a translation and its attributes to an excel file.
  list       List translations.
  primarize  Primarize a translation.
  sync       Synchronize a translation from an excel file.
```


## List translations

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

Then, to list the translations, run:

```sh
$ ccli translation list
```
This command will output a list of all translations (id, context id, context type, context name,locale name, auto, status, primary, owner) available within the current active account in a nice table format way:

```sh
╭────────────────────┬─────────────────┬──────────────┬──────────────────────────┬─────────┬──────┬──────────┬─────────┬───────╮
│ ID                 │ Context_ID      │ Context_Type │       Context_Name       │  Locale │ Auto │  Status  │ Primary │ Owner │
├────────────────────┼─────────────────┼──────────────┼──────────────────────────┼─────────┼──────┼──────────┼─────────┼───────┤
│ TRN-0000-0000-0000 │ PRD-999-999-999 │   product    │ Product P00 for John Doe │ English │ off  │ inactive │    ✓    │   ✓   │
╰────────────────────┴─────────────────┴──────────────┴──────────────────────────┴─────────┴──────┴──────────┴─────────┴───────╯
```


## Export a translation to Excel

To export a translation and its attributes to Excel run:

```
    $ ccli translation export TRN-000-000-000
```

This command will generate a excel file named TRN-000-000-000.xlsx in the current working directory.


## Synchronize a translation from Excel

To synchronize a translation and its attributes from Excel run:

```
    $ ccli translation sync TRN-000-000-000
```

If you want to assign the translation to a different instance (for example, to copy a translation from a product to another product), set either the *Localization Context* field or the *Instance ID* field to the new value.

## Activate a translation

To see the options for the activate translation command run:

```sh
$ ccli translation activate -h

Usage: ccli translation activate [OPTIONS] TRANSLATION_ID

Options:
  -f, --force  Force activate.
  -h, --help   Show this message and exit.

```

Then, to activate a translation, run:

```sh
$ ccli translation activate TRN-000-000-000
```

<b>Please note that only one translation file may be active for a given locale at a time</b>. So you will receive a warning explaining this and will be ask if want to continue performing the action, otherwise the activate command will abort.
You can also use the flag `-f, --force` to force the translation activate and avoid warnings and questions.


## Primarize a translation

To see the options for the primarize translation command run:

```sh
$ ccli translation primarize -h

Usage: ccli translation primarize [OPTIONS] TRANSLATION_ID

Options:
  -f, --force  Force primarize.
  -h, --help   Show this message and exit.

```

Then, to primarize a translation, run:

```sh
$ ccli translation primarize TRN-000-000-000
```

<b>When primarize a translation you will loose all of its attributes values, they will be replaced with the original context attributes values. This action can't be undone.</b> So as the same as `activate command`, you will receive a warning.
You can also use the flag `-f, --force` to force the translation primarize.

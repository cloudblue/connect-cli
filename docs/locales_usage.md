# Locales management

The locale management area offers an useful command to list all locales available and supported by the CloudBlue Connect platform.

To access the group of commands related to the management of locales you must invoke the CLI with the `locale` command:

```sh
$ ccli locale

Usage: ccli locale [OPTIONS] COMMAND [ARGS]...

Options:
  -h, --help  Show this message and exit.

Commands:
  list  List locales.
```


## List locales options

To get the options for the locale list command run:

```sh
$ ccli locale list -h

Usage: ccli locale list [OPTIONS]

Options:
  -q, --query TEXT         RQL query expression.
  -p, --page-size INTEGER  Number of locales per page.
  -c, --always-continue    Do not prompt to continue.
  -h, --help               Show this message and exit.
```
You can also filter the results by adding the ``--query`` flag followed by a RQL query.
For more information about RQL see the [Resource Query Language](https://connect.cloudblue.com/community/api/rql/)
article in the Connect community documentation portal.

## List locales command
```sh
$ ccli locale list
```
This command will output a list of all locales (id, name, autotranslation) available and the `stats` of translations within the current active account in a nice table format way:

```sh
┌──┬───────┬───────────────┬────────────┐
│ID│Name   │Autotranslation│Translations│
├──┼───────┼───────────────┼────────────┤
│ES│Spanish│       ✓       │     2      │
└──┴───────┴───────────────┴────────────┘
```
You could also check if the locale of interest have support for `autotranslation`: ✓ (Yes) | ✖ (No)
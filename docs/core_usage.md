# CloudBlue Connect CLI core functionalities

## Accounts management

`connect-cli` need to configure at least one account to authenticate against the
Connect API.

Accounts will be stored in the `connect-cli` configuration file that by default
will be located in the .ccli folder inside the user home directory.

Multiple accounts can be configured but the active one will be used.

To access the group of commands related to the management of accounts you must invoke the CLI with the `account` command:

```sh
$ ccli account

Usage: ccli account [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  activate  Set the current active account.
  add       Add a new account.
  list      List configured accounts.
  remove    Remove a configured account.

```


## Add a new account

First of all you need to add an account the `connect-cli` with the CloudBlue Connect API *key*.

```
    $ ccli account add "ApiKey XXXXX:YYYYY"
```

## List configured accounts

To get a list of all configured account run:

```
    $ ccli account list
```


## Set the current active account

To set the current active account run:

```
    $ ccli account activate VA-000-000
```

## Remove an account

To remove an account run:

```
    $ ccli account remove VA-000-000
```

## Getting help

To get help about the `connect-cli` commands type:

```
    $ ccli --help
```
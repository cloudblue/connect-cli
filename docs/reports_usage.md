# Reports management

The reports management area offers commands that allow users to generate reports
and allow developers to create custom reports projects.

To access the group of commands related to the management of customers you must invoke the CLI with the `report` command:

```sh
$ ccli report

Usage: ccli report [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  execute  Execute a report.
  info     Get additional information for a given report.
  list     List available reports.
```

## Built-in reports

Multiple reports are available to the `connect-cli` tool, additionally you can create your owns and run them.

If the report is located to another folder you could use the flag `-d` to reference the project location.

### List built-in reports

To list available reports you can run:

```
    $ ccli report list
```

### Get information about a report

To get the information of an specific report run:

```
    $ ccli report info {ID}
```

### Execute a report

To execute a concrete report, you must get the id from the list before and execute:

```
    $ ccli report execute {ID}
```

For example:

```
    $ ccli report execute fulfillment_requests
```

If the report is located to another folder you could run:

```
    $ ccli report execute fulfillment_requests -d /my/other/folder
```

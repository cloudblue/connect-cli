# Streams management

The streams management area offers commands that allow users to clone and get listing of streams,
export or synchronize to/from Excel file.

To access the group of commands related to the management of streams you must invoke the CLI with the `commerce stream` command:

```sh
$ ccli commerce stream

Usage: ccli commerce [OPTIONS] COMMAND [ARGS]...

Options:
  -h, --help  Show this message and exit.

Commands:
  clone   Create a clone of a stream.
  export  Export commerce billing or pricing streams.
  list    List commerce billing and pricing streams.
  sync    Synchronize a stream from an excel file.
```

### Clone streams

To clone existing stream you can run:

```sh
$ccli commerce stream clone [OPTIONS] stream_id
```

```
Options:
    -d, --destination_account TEXT  Destination account ID
    -n, --new-stream-name TEXT      Cloned stream name
    -v, --validate                  Executes the validate action after the clone.
```

### List streams

To list available streams you can run:

```sh
$ ccli commerce stream list [OPTIONS]
```

```
Options:
  -q, --query TEXT  RQL query expression.
```

### Export streams

To export stream you can run:

```sh
$ ccli commerce stream export [OPTIONS] stream_id
```

```
Options:
  -o, --out FILE               Output Excel file name.
  -p, --output_path DIRECTORY  Directory where to store the export.
```

### Synchronize streams

To synchronize a stream from an Excel file you can run:

```sh
$ ccli commerce stream sync input_file
```

Structure of sync file can be taken from `tests/fixtures/commerce/stream_sync.xlsx` file.

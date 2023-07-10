# Project management

The project management area allow you to manage two project types, the extension and the report projects.

To access the group of commands related to the management of customers you must invoke the CLI with the `project` command:

```sh
$ ccli project

Usage: ccli project [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  extension  Manage extension projects.
  report     Manage report projects.
```

## Extension projects

The extension projects are managed using the `extension` subcommand. There are three actions that could be done, bootstrap a new project, bump the project runner to last version or validate a project.

```sh
$ ccli project extension

Usage: ccli project extension [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  bootstrap  Bootstrap new extension project.
  bump       Update runner version to the latest one.
  install    Install extension.
  update     Update extension.
  validate   Validate given extension project.
```

### Bootstrap new project

To create a new extension project you could run this command and follow the wizard:

```sh
$ ccli project extension bootstrap
```

### Bump runner to last version

To bump the runner version to the last one on an existing extenson project, you could run:

```sh
$ ccli project extension bump -p /my/project/folder
```

The docker-compose.yml will be updated with the last version.

### Deploy project

To install or update extension project from a specific repository:

```sh
$ ccli project extension deploy https://repository/url [--tag TAG]
```

This command will create a new extension and deploy one of its environment in cloud mode if it doesn't
exist or update an existing one. Specify tag to deploy certain repository version, otherwise latest version
will be used. All configurations are taken from _connect-deployment.yaml_ file inside root directory
of repository. Owner of extension will be current active user.

Structure of connect_deployment.yaml
```yaml
package_id: package.id
icon: path/to/icon.png              # absolute path from root directory
name: Extension name
env: development                    # one of [development, test, production]
type: multiaccount                  # one of [multiaccount, transformations]
description: Short description 
overview: path/to/overview          # absolute path from root directory
category: Category                  
website: https://www.example.com    
var:
  SOME_VAR:
    value: VALUE
    secure: false
  ENV_VAR:
    secure: true
```

The only mandatory attribute is `package_id`. If you haven't specified
`env` - default value is `production`. In case of missing extension `type` - it will be calculated automatically
based on `pyproject.toml` file inside repository. In case you specified `category` search for such 
will be executed and in case of match category will be set.

To use environment variable - add its name to `var` section and skip `value`.

### Validate project.

To validate if an extension project is correct, you could run:

```sh
$ ccli project extension validate -p /my/project/folder
```

If the result is in green it means that is correct.

## Report projects

The report projects are managed using the `report` subcommand. There are three actions that could be done, add a new report to a project, bootstrap a new project or validate a project.

```sh
$ ccli project report

Usage: ccli project report [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  add        Add new report to the given project.
  bootstrap  Bootstrap new report project.
  validate   Validate given report project.
```

### Add report

To add a new report in an existing project you could run this command and follow the wizard:

```sh
$ ccli project report add -p /my/project/folder
```

### Bootstrap new project

To create a new report project you could run this command and follow the wizard:

```sh
$ ccli project report bootstrap -o /output/folder
```

### Validate project

To create a new report project you could run this command:

```sh
$ ccli project report validate -p /my/project/folder
```

If the result is in green it means that is correct.

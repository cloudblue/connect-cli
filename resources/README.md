# CloudBlue Connect Command Line Interface

## What is CloudBlue Connect Command Line Interface

The CloudBlue Connect Command Line Interface (CLI) is an extensible unified tool to perform various automation scenarios. With just one tool, you can control multiple Connect modules from the command line and automate them through scripts.

Since it is extensible, users can write their own plugins to extend its functionalities.


## How to use this image

```
$ docker run -it -v $HOME/.ccli:/home/connect/.ccli cloudblueconnect/connect-cli ccli
```

## Version upgrade

```
$ docker pull cloudblueconnect/connect-cli
```

## Where to get help

[CloudBlue Connect community portal](https://connect.cloudblue.com/community/sdk/cli/), [Project Github repository](https://github.com/cloudblue/connect-cli)


## Where to file an issue

[https://github.com/cloudblue/connect-cli/issues](https://github.com/cloudblue/connect-cli/issues)

## License

`connect-cli` is released under the [Apache License Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).
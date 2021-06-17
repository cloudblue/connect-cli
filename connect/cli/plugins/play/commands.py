# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2021 Ingram Micro. All Rights Reserved.
import os
import sys

import click

from connect.cli.core.config import pass_config
from connect.cli.plugins.play.context import Context


@click.group(name='play', short_help='Play connect scripts.')
def grp_play():
    pass


class PlayOptions:
    context_file = 'context.json'


class PassArgumentDecorator:
    def __init__(self, arg):
        self.obj = arg

    def __call__(self, f):
        def wrapped(*args, **kwargs):
            f(self.obj, *args, **kwargs)

        return wrapped


pass_arg = PassArgumentDecorator


def setup_script_command(cls):
    @pass_config
    @pass_arg(cls)
    def cmd_play_custom(script_class, config, **kwargs):
        config.validate()

        Context.context_file_name = PlayOptions.context_file
        ctx = Context.create(**kwargs)

        if 'endpoint' not in ctx or not ctx.endpoint:
            ctx.endpoint = config.active.endpoint

        if 'distributor_account_token' not in ctx or not ctx.distributor_account_token:
            ctx.distributor_account_token = config.active.api_key

        ctx | script_class()
        ctx.save()

    for o in cls.options():
        cmd_play_custom = click.option(*o.args, **o.kwargs)(cmd_play_custom)

    grp_play.command(name=cls.command(), short_help=cls.help())(cmd_play_custom)


def load_one_script(scripts, filename):
    modname = filename[0:-3]

    try:
        mod = __import__(modname, globals={"__name__": __name__}, fromlist=['*'])

        if not hasattr(mod, '__all__'):
            print(f'Warning: {filename} has no __all__ defined', file=sys.stderr)
            return

        for cname in mod.__all__:
            cls = getattr(mod, cname)
            setup_script_command(cls)

    except Exception as e:
        print(f'Failed to import {scripts}/{filename}: {e}')


def load_scripts_actions():
    scripts = os.environ.get('CCLI_SCRIPTS', 'scripts')
    if scripts[0] != '/':
        scripts = os.path.join(os.getcwd(), scripts)

    if os.path.isdir(scripts):
        print(f'Reading scripts library from {scripts}')
        sys.path.append(scripts)

        for filename in sorted(os.listdir(scripts)):
            if not filename.endswith('.py') or filename[0] == '_':
                continue

            load_one_script(scripts, filename)


load_scripts_actions()


def get_group():
    return grp_play

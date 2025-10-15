# -*- coding: utf-8 -*-

# This file is part of the CloudBlue Connect connect-cli.
# Copyright (c) 2025 CloudBlue. All rights reserved.
import sys

from connect.cli.plugins.play.context import Context
from connect.cli.plugins.play.save import Save
from connect.cli.plugins.play.script import OptionWrapper, Script


class Script1(Script):
    """CLI help for Script1."""

    @classmethod
    def options(cls):
        return [
            OptionWrapper('--some_id', help='Script1 IDs'),
            OptionWrapper('--account_token', help='Script1 account token'),
        ]

    def do(self, context=None):
        super().do(context=context)
        print('--- Init Script 1 ---')


__all__ = ('Script1',)

if __name__ == '__main__':
    try:
        ctx = Context.create(sys.argv[1:])
        ctx | Script1 | Save
        print(ctx)
    except Exception as e:
        print(e)

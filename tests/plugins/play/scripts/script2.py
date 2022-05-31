
# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2021 Ingram Micro. All Rights Reserved.
import sys

from connect.cli.plugins.play.context import Context
from connect.cli.plugins.play.save import Save
from connect.cli.plugins.play.script import OptionWrapper, Script


class Script2(Script):
    """CLI help for Script2."""

    @classmethod
    def options(cls):
        return [
            OptionWrapper('--account_token', help='Script2 account token'),
        ]

    def do(self, context=None):
        super().do(context=context)
        print('--- Init Script 2 ---')


if __name__ == '__main__':
    try:
        ctx = Context.create(sys.argv[1:])
        ctx | Script2 | Save
        print(ctx)
    except Exception as e:
        print(e)

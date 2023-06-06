# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2021 Ingram Micro. All Rights Reserved.
from connect.client import ConnectClient

from connect.cli.plugins.play.context import Context
from connect.cli.plugins.play.script import OptionWrapper, Script


def test_script():
    ow = OptionWrapper(1, 2, 3, a=1, b=2, c=3)
    assert ow.args == (1, 2, 3)
    assert ow.kwargs == {'a': 1, 'b': 2, 'c': 3}

    class BasicInitScript(Script):
        """Some Help Message"""

    assert BasicInitScript.command() == 'basic-init-script'
    assert BasicInitScript.help() == 'Some Help Message'
    assert BasicInitScript.options() == []

    ctx = Context()
    ctx.endpoint = 'https://api.cnct.info/public/v1'
    ctx.distributor_account_token = 'ApiKey v1'
    ctx.vendor_account_token = 'ApiKey v2'

    s = BasicInitScript(context=ctx)
    assert type(s.dclient) == ConnectClient
    assert type(s.vclient) == ConnectClient

    s.do()
    s.do(context={'endpoint': 'https://api.cnct.tech/public/v1'})

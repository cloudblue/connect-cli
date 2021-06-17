# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2021 Ingram Micro. All Rights Reserved.
import re
from typing import List

from connect.cli.plugins.play.context import Context
from connect.client import ConnectClient


class OptionWrapper:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class Script:
    context: Context = None
    endpoint: str = None

    def __init__(self, context=None, **kwargs):
        self.context = context if context is not None else Context()
        self.context.update(kwargs)

    @classmethod
    def command(cls) -> str:
        return str(re.sub(r'^([A-Z])', lambda x: x.group(1).lower(),
                   re.sub(r'([a-z])([A-Z])', lambda x: f'{x.group(1)}-{x.group(2).lower()}', cls.__name__)))

    @classmethod
    def help(cls) -> str:
        return cls.__doc__

    @classmethod
    def options(cls) -> List[OptionWrapper]:
        return []

    def client(self, token) -> ConnectClient:
        return ConnectClient(token, endpoint=self.context.endpoint, use_specs=False)

    @property
    def dclient(self) -> ConnectClient:
        return self.client(self.context.distributor_account_token)

    @property
    def vclient(self) -> ConnectClient:
        return self.client(self.context.vendor_account_token)

    def do(self, context=None):
        if context:
            context.update(self.context)
            self.context = context

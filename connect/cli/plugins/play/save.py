# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2021 Ingram Micro. All Rights Reserved.
from connect.cli.plugins.play.context import Context
from connect.cli.plugins.play.script import Script


class Save(Script):
    def do(self, filename=Context.context_file_name, context=None):
        super().do(context=context)
        self.context.save(filename=filename)

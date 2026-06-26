# -*- coding: utf-8 -*-

# This file is part of the CloudBlue Connect connect-cli.
# Copyright (c) 2025 CloudBlue. All rights reserved.
from connect.cli.plugins.play.context import Context
from connect.cli.plugins.play.script import Script


class Save(Script):
    def do(self, filename=Context.context_file_name, context=None):
        super().do(context=context)
        self.context.save(filename=filename)

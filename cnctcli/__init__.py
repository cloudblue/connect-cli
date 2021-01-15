# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2020 Ingram Micro. All Rights Reserved.

import pkg_resources


try:
    __version__ = pkg_resources.require('connect-cli')[0].version
except BaseException:  # noqa: E722
    __version__ = '0.0.1'


def get_version():
    return __version__

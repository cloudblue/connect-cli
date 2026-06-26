# -*- coding: utf-8 -*-

# This file is part of the CloudBlue Connect connect-cli
# Copyright (c) 2025 CloudBlue. All rights reserved.
from importlib.metadata import version


try:
    __version__ = version('connect-cli')
except Exception:  # pragma: no cover
    __version__ = '0.0.0'


def get_version():
    return __version__

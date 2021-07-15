# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli
# Copyright (c) 2019-2021 Ingram Micro. All Rights Reserved.
import os
import re

from pkg_resources import DistributionNotFound, get_distribution


MODULE_REGEX = r'[0-9]+.[0-9]'

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
VERSION_FILE = os.path.join(BASE_DIR, os.path.join('.data', 'version.txt'))

try:
    if os.path.exists(VERSION_FILE):
        __version__ = re.search(MODULE_REGEX, open(VERSION_FILE, 'r').read()).group()
    else:
        __version__ = get_distribution('connect-cli').version
except DistributionNotFound:  # pragma: no cover
    __version__ = '0.0.0'


def get_version():
    return __version__

# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli
# Copyright (c) 2019-2021 Ingram Micro. All Rights Reserved.
from pkg_resources import DistributionNotFound, get_distribution


try:
    __version__ = get_distribution('connect-cli').version
except DistributionNotFound:  # pragma: no cover
    __version__ = '0.0.0'


def get_version():
    return __version__

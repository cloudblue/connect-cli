# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2022 Ingram Micro. All Rights Reserved.

from collections import namedtuple

ColumnSettings = namedtuple('ColumnSettings', ['header', 'width'])

ATTRIBUTES_COLS = {
    'A': ColumnSettings('Key', 70),
    'B': ColumnSettings('Action', 25),
    'C': ColumnSettings('Value', 100),
    'D': ColumnSettings('Comment', 30),
}

# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2020 Ingram Micro. All Rights Reserved.

ITEMS_COLS_HEADERS = {
    'A': 'ID',
    'B': 'MPN',
    'C': 'Action',
    'D': 'Name',
    'E': 'Description',
    'F': 'Type',
    'G': 'Precision',
    'H': 'Unit',
    'I': 'Billing Period',
    'J': 'Commitment',
    'K': 'Status',
    'L': 'Created',
    'M': 'Modified',
}

PRECISIONS = ('integer', 'decimal(1)', 'decimal(2)', 'decimal(4)', 'decimal(8)')
COMMITMENT = ('-', '1 year', '2 years', '3 years', '4 years', '5 years')
BILLING_PERIOD = (
    'onetime',
    'monthly',
    'yearly',
    '2 years',
    '3 years',
    '4 years',
    '5 years',
)

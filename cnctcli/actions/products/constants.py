# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2021 Ingram Micro. All Rights Reserved.

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

PARAMS_COLS_HEADERS = {
    'A': 'Verbose ID',
    'B': 'ID',
    'C': 'Action',
    'D': 'Title',
    'E': 'Description',
    'F': 'Phase',
    'G': 'Scope',
    'H': 'Type',
    'I': 'Required',
    'J': 'Unique',
    'K': 'Hidden',
    'L': 'JSON Properties',
    'M': 'Created',
    'N': 'Modified',
}

MEDIA_COLS_HEADERS = {
    'A': 'Position',
    'B': 'ID',
    'C': 'Action',
    'D': 'Type',
    'E': 'Image File',
    'F': 'Video URL Location',
}

CAPABILITIES_COLS_HEADERS = {
    'A': 'Capability',
    'B': 'Action',
    'C': 'Value',
}

STATIC_LINK_HEADERS = {
    'A': 'Type',
    'B': 'Title',
    'C': 'Action',
    'D': 'Url',
}

TEMPLATES_HEADERS = {
    'A': 'ID',
    'B': 'Title',
    'C': 'Action',
    'D': 'Scope',
    'E': 'Type',
    'F': 'Content',
    'G': 'Created',
    'H': 'Modified',
}

CONFIGURATION_HEADERS = {
    'A': 'ID',
    'B': 'Parameter',
    'C': 'Scope',
    'D': 'Action',
    'E': 'Item ID',
    'F': 'Item Name',
    'G': 'Marketplace ID',
    'H': 'Marketplace Name',
    'I': 'Value',
}

ACTIONS_HEADERS = {
    'A': 'Verbose ID',
    'B': 'ID',
    'C': 'Action',
    'D': 'Name',
    'E': 'Title',
    'F': 'Description',
    'G': 'Scope',
    'H': 'Created',
    'I': 'Modified',
}


PARAM_TYPES = [
    'email',
    'address',
    'checkbox',
    'choice',
    'domain',
    'subdomain',
    'url',
    'dropdown',
    'object',
    'password',
    'phone',
    'text',
]


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

CAPABILITIES = (
    'Pay-as-you-go support and schema',
    'Pay-as-you-go dynamic items support',
    'Pay-as-you-go future charges support',
    'Consumption reporting for Reservation Items',
    'Dynamic Validation of the Draft Requests',
    'Dynamic Validation of the Inquiring Form',
    'Reseller Authorization Level',
    'Tier Accounts Sync',
    'Administrative Hold',
)

# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2022 Ingram Micro. All Rights Reserved.

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

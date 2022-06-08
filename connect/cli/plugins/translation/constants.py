# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2022 Ingram Micro. All Rights Reserved.

from collections import namedtuple

TRANSLATION_TABLE_HEADER = """



| ID | Context_ID | Context_Type | Context_Name |Locale  | Auto | Status | Primary | Owner |
|:--------|:-----------|:-----------:|:-----------:|:-----------:|:-----------:|:-----------:|:-----------:|:-----------:|
"""

FieldSettings = namedtuple('FieldSettings', ['row_idx', 'title'])

GENERAL_SHEET_FIELDS = {
    'translation_id': FieldSettings(1, 'Translation'),
    'owner_id': FieldSettings(2, 'Translation Owner ID'),
    'owner_name': FieldSettings(3, 'Translation Owner Name'),
    'locale_id': FieldSettings(4, 'Locale'),
    'context_id': FieldSettings(5, 'Localization Context'),
    'context_instance_id': FieldSettings(6, 'Instance ID'),
    'context_name': FieldSettings(7, 'Instance Name'),
    'description': FieldSettings(8, 'Description'),
    'auto_enabled': FieldSettings(9, 'Auto-translation'),
}

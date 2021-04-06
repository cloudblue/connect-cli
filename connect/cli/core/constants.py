# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2021 Ingram Micro. All Rights Reserved.

DEFAULT_ENDPOINT = 'https://api.connect.cloudblue.com/public/v1'
DEFAULT_USER_AGENT = 'CloudBlue Connect CLI/'
DEFAULT_BAR_FORMAT = '{desc:<70.69}{percentage:3.0f}%|{bar:30}{r_bar}'

CAIRO_NOT_FOUND_ERROR = """Connect CLI depends on Cairo which is not present on the system.
If so, please follow the instructions to install it at https://github.com/cloudblue/connect-cli
and make sure your PATH environment variable includes also the Cairo shared libraries folder.
"""

PYPI_JSON_API_URL = 'https://pypi.org/pypi/connect-cli/json'

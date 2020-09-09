# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect product-sync.
# Copyright (c) 2019-2020 Ingram Micro. All Rights Reserved.

import json
import os

from click import make_pass_decorator


class Config(object):
    def __init__(self):
        self._config_path = None
        self._api_url = None
        self._api_key = None

    @property
    def api_url(self):
        return self._api_url

    @api_url.setter
    def api_url(self, value):
        self._api_url = value

    @property
    def api_key(self):
        return self._api_key

    @api_key.setter
    def api_key(self, value):
        self._api_key = value

    def load(self, config_dir):
        self._config_path = os.path.join(config_dir, 'config.json')
        if not os.path.isfile(self._config_path):
            return

        with open(self._config_path, 'r') as f:
            data = json.load(f)
            self.api_url = data['apiEndpoint']
            self.api_key = data.get('apiKey')

    def store(self):
        with open(self._config_path, 'w') as f:
            f.write(json.dumps({
                'apiEndpoint': self.api_url,
                'apiKey': self.api_key
            }))

    def is_valid(self):
        pass


pass_config = make_pass_decorator(Config, ensure=True)

# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2021 Ingram Micro. All Rights Reserved.

import json
import os
from dataclasses import dataclass

from click import ClickException, make_pass_decorator


from connect.cli.core.constants import DEFAULT_ENDPOINT


@dataclass
class Account:
    id: str
    name: str
    api_key: str
    endpoint: str

    def is_vendor(self):
        return self.id.startswith('VA-')

    def is_provider(self):
        return self.id.startswith('PA-')


class Config(object):
    def __init__(self):
        self._config_path = None
        self._active = None
        self._silent = True
        self._accounts = {}
        self._verbose = False

    def add_account(self, id, name, api_key, endpoint=DEFAULT_ENDPOINT):
        self._accounts[id] = Account(id, name, api_key, endpoint)
        if not self._active:
            self._active = self._accounts[id]

    @property
    def active(self):
        return self._active

    @property
    def accounts(self):
        return self._accounts

    @property
    def silent(self):
        return self._silent

    @silent.setter
    def silent(self, val):
        self._silent = val

    @property
    def verbose(self):
        return self._verbose

    @verbose.setter
    def verbose(self, val):
        self._verbose = val

    def activate(self, id):
        account = self._accounts.get(id)
        if account:
            self._active = account
            return
        raise ClickException(f'The account identified by {id} does not exist.')

    def remove_account(self, id):
        if id in self._accounts:
            account = self._accounts[id]
            del self._accounts[id]
            if self._active.id == id:
                if self._accounts:
                    self._active = list(self._accounts.values())[0]
                else:
                    self._active = None
            return account
        raise ClickException(f'The account identified by {id} does not exist.')

    def load(self, config_dir):
        self._config_path = os.path.join(config_dir, 'config.json')
        if not os.path.isfile(self._config_path):
            return

        with open(self._config_path, 'r') as f:
            data = json.load(f)
            active_account_id = data['active']
            for account_data in data['accounts']:
                account = Account(**account_data)
                self._accounts[account.id] = account
                if account.id == active_account_id:
                    self._active = account

    def store(self):
        with open(self._config_path, 'w') as f:
            accounts = [account.__dict__ for account in self._accounts.values()]
            f.write(
                json.dumps(
                    {
                        'active': self._active.id if self._active else '',
                        'accounts': accounts,
                    },
                    sort_keys=True,
                    indent=4,
                ),
            )

    def validate(self):
        if not (self._accounts and self._active):
            raise ClickException(
                'connect-cli is not properly configured.\n'
                'You must configure at least a Connect account. To do so please execute:\n\n'
                'ccli account add API_KEY\n\n',
            )


pass_config = make_pass_decorator(Config, ensure=True)

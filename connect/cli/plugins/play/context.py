# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2021 Ingram Micro. All Rights Reserved.
import inspect
import json
import sys


class Context(dict):
    context_file_name = None

    @classmethod
    def create_from_file(cls, filename=None):
        ctx = cls()
        try:
            ctx.load(filename)
        except FileNotFoundError:
            pass

        return ctx

    @classmethod
    def create(cls, args=None, filename=None, **kwargs):
        ctx = cls()
        try:
            ctx.load(filename)
        except FileNotFoundError:
            pass

        if args:
            ctx.parse_args(args)

        if kwargs:
            for k, v in kwargs.items():
                if v is not None:
                    ctx[k] = v

        return ctx

    def parse_args(self, args):
        for k, v in [a.split('=') for a in args]:
            self[k] = v

    def load(self, filename=None):
        if filename is None:
            filename = self.__class__.context_file_name
        if filename:
            with open(filename) as f:
                print(f'Loading context from {filename}', file=sys.stderr)
                self.clear()
                for k, v in json.load(f).items():
                    self[k] = v

    def save(self, filename=None):
        if filename is None:
            filename = self.__class__.context_file_name
        if filename:
            with open(filename, 'w') as f:
                print(f'Saving context into {filename}', file=sys.stderr)
                json.dump(self, f, indent=4)

    def __str__(self):
        return json.dumps(self, indent=4)

    def __getattr__(self, item):
        if item in self:
            return self[item]

        raise KeyError(item)

    def __setattr__(self, key, value):
        self[key] = value

    def __ior__(self, kv):
        key, value = kv
        if isinstance(value, dict):
            if key not in self:
                self[key] = {}
            self[key].update(value)
        else:
            if not isinstance(value, list):
                value = [value]

            if key not in self:
                self[key] = []

            self[key].extend(value)

        return self

    def __or__(self, step):
        if inspect.isclass(step):
            step = step()

        step.do(context=self)
        return self

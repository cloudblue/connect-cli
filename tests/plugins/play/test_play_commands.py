# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2021 Ingram Micro. All Rights Reserved.
import os
import sys


def unimport():
    for m in ('connect.cli.plugins.play.commands', 'connect.cli.ccli'):
        if m in sys.modules:
            del sys.modules[m]


def test_play_commands(fs, mocker):
    os.environ['CCLI_SCRIPTS'] = os.path.join(os.path.dirname(__file__), 'scripts')

    unimport()
    from connect.cli.ccli import main

    mocker.patch('connect.cli.plugins.play.commands.PlayOptions.context_file', None)
    mocker.patch('sys.argv', ['cmd', 'play', 'script1'])
    main()


def test_play_commands_rel(fs, mocker):

    os.environ['CCLI_SCRIPTS'] = 'tests/plugins/play/scripts'

    unimport()
    from connect.cli.ccli import main

    mocker.patch('connect.cli.plugins.play.commands.PlayOptions.context_file', None)
    mocker.patch('sys.argv', ['cmd', 'play', 'script1'])
    main()

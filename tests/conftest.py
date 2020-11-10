import json

import pytest

import requests
import yaml

from tests.data import CONFIG_DATA
from io import StringIO

from requests_mock import Mocker


@pytest.fixture()
def config_mocker(mocker):
    mocker.patch('os.path.isfile', return_value=True)
    return mocker.patch(
        'cnctcli.config.open',
        mocker.mock_open(read_data=json.dumps(CONFIG_DATA)),
    )

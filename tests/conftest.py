import json

import pytest

import requests
import yaml

from tests.data import CONFIG_DATA
from io import StringIO

from cnct.client.constants import CONNECT_SPECS_URL
from requests_mock import Mocker

def _load(url):
    res = requests.get(url, stream=True)
    if res.status_code == 200:
        result = StringIO()
        for chunk in res.iter_content(chunk_size=8192):
            result.write(str(chunk, encoding='utf-8'))
        result.seek(0)
        return yaml.safe_load(result)
    res.raise_for_status()


@pytest.fixture()
def config_mocker(mocker):
    mocker.patch('os.path.isfile', return_value=True)
    return mocker.patch(
        'cnctcli.config.open',
        mocker.mock_open(read_data=json.dumps(CONFIG_DATA)),
    )


@pytest.fixture(scope='session')
def connect_specs():
    mock = Mocker()
    mock.register_uri('GET', CONNECT_SPECS_URL, real_http=True)
    specs = _load(CONNECT_SPECS_URL)

    return specs


@pytest.fixture(scope='function')
def load_specs(connect_specs, mocker):
    return mocker.patch('cnct.specs.parser._load', return_value=connect_specs)

import json

import pytest

from tests.data import CONFIG_DATA


@pytest.fixture()
def config_mocker(mocker):
    mocker.patch('os.path.isfile', return_value=True)
    return mocker.patch(
        'cnctcli.config.open',
        mocker.mock_open(read_data=json.dumps(CONFIG_DATA)),
    )

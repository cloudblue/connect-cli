CONFIG_DATA = {
    'active': 'VA-000',
    'accounts': [
        {
            'id': 'VA-000',
            'name': 'Account 0',
            'api_key': 'ApiKey XXXX:YYYY',
            'endpoint': 'https://localhost/public/v1',
        },
        {
            'id': 'VA-001',
            'name': 'Account 1',
            'api_key': 'ApiKey ZZZZ:SSSS',
            'endpoint': 'https://localhost/public/v1',
        },
    ],
}

EXTENSION_CLASS_DECLARATION = 'class {extension_name}Extension(BaseExtension):'
EXTENSION_VARIABLES_DECLARATION = """@variables([
    {
        'name': 'VAR_NAME_1',
        'initial_value': 'VAR_VALUE_1',
        'secure': False,
    },
    {
        'name': 'VAR_NAME_N',
        'initial_value': 'VAR_VALUE_N',
        'secure': True,
    },
])
"""

EXTENSION_IMPORTS = """from connect.eaas.core.decorators import (
    event,{schedulable}{variables}
)
from connect.eaas.core.extension import Extension as BaseExtension
from connect.eaas.core.responses import ({background_response}{interactive_response}{scheduled_response}
)
"""

TEST_IMPORTS = """import pytest

from connect_ext.extension import {extension_name}Extension
"""


EXTENSION_BG_EVENT = """    @event(
        'sample_background_event',
        statuses=[
            'status1', 'status2',
        ],
    )
    {async_def}def handle_sample_background_event(self, request):
        self.logger.info(f"Obtained request with id {{request['id']}}")
        return BackgroundResponse.done()
"""

TEST_BG_EVENT = """{pytest_asyncio}{async_def}def test_handle_sample_background_event(
    {client_factory_prefix}client_factory,
    response_factory,
    logger,
):
    config = {{}}
    request = {{'id': 1}}
    responses = [
        response_factory(count=100),
        response_factory(value=[{{'id': 'item-1', 'value': 'value1'}}]),
    ]
    client = {await_keyword}{client_factory_prefix}client_factory(responses)
    ext = {extension_name}Extension(client, logger, config)
    result = {await_keyword}ext.handle_sample_background_event(request)
    assert result.status == 'success'"""

EXTENSION_INTERACTIVE_EVENT = """    @event(
        'sample_interactive_event',
        statuses=[
            'status1', 'status2',
        ],
    )
    {async_def}def handle_sample_interactive_event(self, request):
        self.logger.info(f"Obtained request with id {{request['id']}}")
        return InteractiveResponse.done(
            http_status=200,
            headers={{'X-Custom-Header': 'value'}},
            body=request,
        )
"""

EXTENSION_SCHEDULABLE_EVENT = """    @schedulable('Schedulable method', 'It can be used to test DevOps scheduler.')
    {async_def}def execute_scheduled_processing(self, schedule):
        self.logger.info(
            f"Received event for schedule  {{schedule['id']}}",
        )
        return ScheduledExecutionResponse.done()
"""


TEST_INTERACTIVE_EVENT = """{pytest_asyncio}{async_def}def test_handle_sample_interactive_event(
    {client_factory_prefix}client_factory,
    response_factory,
    logger,
):
    config = {{}}
    request = {{'id': 1}}
    responses = [
        response_factory(count=100),
        response_factory(value=[{{'id': 'item-1', 'value': 'value1'}}]),
    ]
    client = {await_keyword}{client_factory_prefix}client_factory(responses)
    ext = {extension_name}Extension(client, logger, config)
    result = {await_keyword}ext.handle_sample_interactive_event(request)
    assert result.status == 'success'
    assert result.body == request"""


TEST_SCHEDULABLE_EVENT = """{pytest_asyncio}{async_def}def test_execute_scheduled_processing(
    {client_factory_prefix}client_factory,
    response_factory,
    logger,
):
    config = {{}}
    request = {{'id': 1}}
    responses = [
        response_factory(count=100),
        response_factory(value=[{{'id': 'item-1', 'value': 'value1'}}]),
    ]
    client = {await_keyword}{client_factory_prefix}client_factory(responses)
    ext = {extension_name}Extension(client, logger, config)
    result = {await_keyword}ext.execute_scheduled_processing(request)
    assert result.status == 'success'"""

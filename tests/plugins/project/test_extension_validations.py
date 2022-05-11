import pytest
import toml
import yaml

from connect.cli.plugins.project.extension.validations import (
    get_code_context,
    validate_docker_compose_yml,
    validate_events,
    validate_extension_class,
    validate_pyproject_toml,
    validate_schedulables,
    validate_variables,
    ValidationItem,
    ValidationResult,
)
from connect.eaas.core.extension import Extension
from connect.eaas.core.responses import (
    CustomEventResponse,
    ProcessingResponse,
    ProductActionResponse,
    ValidationResponse,
)


def test_validate_pyproject_toml_file_not_found(mocker):
    result = validate_pyproject_toml(mocker.MagicMock(), 'fake_dir', None)

    assert isinstance(result, ValidationResult)
    assert result.must_exit is True
    assert len(result.items) == 1
    item = result.items[0]
    assert isinstance(item, ValidationItem)
    assert item.level == 'ERROR'
    assert 'the mandatory *pyproject.toml* project descriptor file is not present.' in item.message
    assert item.file == 'fake_dir/pyproject.toml'


def test_validate_pyproject_toml_invalid_toml(mocker):
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.os.path.isfile',
        return_value=True,
    )
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.toml.load',
        side_effect=toml.TomlDecodeError('error', 'error', 0),
    )

    result = validate_pyproject_toml(mocker.MagicMock(), 'fake_dir', None)

    assert isinstance(result, ValidationResult)
    assert result.must_exit is True
    assert len(result.items) == 1
    item = result.items[0]
    assert isinstance(item, ValidationItem)
    assert item.level == 'ERROR'
    assert 'The extension project descriptor file *pyproject.toml* is not valid.' in item.message
    assert item.file == 'fake_dir/pyproject.toml'


def test_validate_pyproject_toml_depends_on_runner(mocker):
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.os.path.isfile',
        return_value=True,
    )
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.toml.load',
        return_value={
            'tool': {
                'poetry': {
                    'dependencies': {
                        'connect-extension-runner': '23',
                    },
                    'plugins': {
                        'connect.eaas.ext': {
                            'extension': 'root_pkg.extension:MyExtension',
                        },
                    },
                },
            },
        },
    )
    mocker.patch('connect.cli.plugins.project.extension.validations.importlib.import_module')
    mocker.patch('connect.cli.plugins.project.extension.validations.inspect.getmembers', return_value=[])

    result = validate_pyproject_toml(mocker.MagicMock(), 'fake_dir', None)

    assert isinstance(result, ValidationResult)
    assert result.must_exit is False
    assert len(result.items) == 1
    item = result.items[0]
    assert isinstance(item, ValidationItem)
    assert item.level == 'WARNING'
    assert 'Extensions must depend on *connect-eaas-core* library not *connect-extension-runner*.' in item.message
    assert item.file == 'fake_dir/pyproject.toml'


def test_validate_pyproject_toml_missed_eaas_core_dependency(mocker):
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.os.path.isfile',
        return_value=True,
    )
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.toml.load',
        return_value={
            'tool': {
                'poetry': {
                    'dependencies': {},
                    'plugins': {
                        'connect.eaas.ext': {
                            'extension': 'root_pkg.extension:MyExtension',
                        },
                    },
                },
            },
        },
    )
    mocker.patch('connect.cli.plugins.project.extension.validations.importlib.import_module')
    mocker.patch('connect.cli.plugins.project.extension.validations.inspect.getmembers', return_value=[])

    result = validate_pyproject_toml(mocker.MagicMock(), 'fake_dir', None)

    assert isinstance(result, ValidationResult)
    assert result.must_exit is False
    assert len(result.items) == 1
    item = result.items[0]
    assert isinstance(item, ValidationItem)
    assert item.level == 'ERROR'
    assert 'No dependency on *connect-eaas-core* has been found.' in item.message
    assert item.file == 'fake_dir/pyproject.toml'


def test_validate_pyproject_toml_no_extension_declaration(mocker):
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.os.path.isfile',
        return_value=True,
    )
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.toml.load',
        return_value={
            'tool': {
                'poetry': {
                    'dependencies': {
                        'connect-eaas-core': '1.0.0',
                    },
                },
            },
        },
    )
    mocker.patch('connect.cli.plugins.project.extension.validations.importlib.import_module')
    mocker.patch('connect.cli.plugins.project.extension.validations.inspect.getmembers', return_value=[])

    result = validate_pyproject_toml(mocker.MagicMock(), 'fake_dir', None)

    assert isinstance(result, ValidationResult)
    assert result.must_exit is True
    assert len(result.items) == 1
    item = result.items[0]
    assert isinstance(item, ValidationItem)
    assert item.level == 'ERROR'
    assert 'No extension declaration has been found.' in item.message
    assert item.file == 'fake_dir/pyproject.toml'


def test_validate_pyproject_toml_invalid_extension_declaration(mocker):
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.os.path.isfile',
        return_value=True,
    )
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.toml.load',
        return_value={
            'tool': {
                'poetry': {
                    'dependencies': {
                        'connect-eaas-core': '1.0.0',
                    },
                    'plugins': {
                        'connect.eaas.ext': {
                            'other_key': 'root_pkg.extension:MyExtension',
                        },
                    },
                },
            },
        },
    )
    mocker.patch('connect.cli.plugins.project.extension.validations.importlib.import_module')
    mocker.patch('connect.cli.plugins.project.extension.validations.inspect.getmembers', return_value=[])

    result = validate_pyproject_toml(mocker.MagicMock(), 'fake_dir', None)

    assert isinstance(result, ValidationResult)
    assert result.must_exit is True
    assert len(result.items) == 1
    item = result.items[0]
    assert isinstance(item, ValidationItem)
    assert item.level == 'ERROR'
    assert 'Invalid extension declaration in' in item.message
    assert item.file == 'fake_dir/pyproject.toml'


def test_validate_pyproject_toml_import_error(mocker):
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.os.path.isfile',
        return_value=True,
    )
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.toml.load',
        return_value={
            'tool': {
                'poetry': {
                    'dependencies': {
                        'connect-eaas-core': '1.0.0',
                    },
                    'plugins': {
                        'connect.eaas.ext': {
                            'extension': 'root_pkg.extension:MyExtension',
                        },
                    },
                },
            },
        },
    )
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.importlib.import_module',
        side_effect=ImportError(),
    )

    result = validate_pyproject_toml(mocker.MagicMock(), 'fake_dir', None)

    assert isinstance(result, ValidationResult)
    assert result.must_exit is True
    assert len(result.items) == 1
    item = result.items[0]
    assert isinstance(item, ValidationItem)
    assert item.level == 'ERROR'
    assert 'The extension class *root_pkg.extension:MyExtension* cannot be loaded' in item.message
    assert item.file == 'fake_dir/pyproject.toml'


@pytest.mark.parametrize(
    ('deprecated', 'replacement'),
    (
        (CustomEventResponse, 'InteractiveResponse'),
        (ProcessingResponse, 'BackgroundResponse'),
        (ProductActionResponse, 'InteractiveResponse'),
        (ValidationResponse, 'InteractiveResponse'),
    ),
)
def test_validate_pyproject_toml_deprecated_responses(mocker, deprecated, replacement):
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.os.path.isfile',
        return_value=True,
    )
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.toml.load',
        return_value={
            'tool': {
                'poetry': {
                    'dependencies': {
                        'connect-eaas-core': '1.0.0',
                    },
                    'plugins': {
                        'connect.eaas.ext': {
                            'extension': 'root_pkg.extension:MyExtension',
                        },
                    },
                },
            },
        },
    )
    mocker.patch('connect.cli.plugins.project.extension.validations.importlib.import_module')
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.inspect.getmembers',
        return_value=[(deprecated.__name__, deprecated)],
    )
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.get_code_context',
        return_value={
            'file': 'file',
            'start_line': 0,
            'lineno': 5,
            'code': 'code',
        },
    )

    result = validate_pyproject_toml(mocker.MagicMock(), 'fake_dir', None)

    assert isinstance(result, ValidationResult)
    assert result.must_exit is False
    assert len(result.items) == 1
    item = result.items[0]
    assert isinstance(item, ValidationItem)
    assert item.level == 'WARNING'
    assert (
        f'The response class *{deprecated.__name__}* '
        f'has been deprecated in favor of *{replacement}*.'
    ) in item.message
    assert item.file == 'file'
    assert item.start_line == 0
    assert item.lineno == 5
    assert item.code == 'code'


def test_validate_extension_class_invalid_superclass(mocker):
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.inspect.getsourcefile',
        return_value='/dir/file.py',
    )
    context = {'extension_class': KeyError}
    result = validate_extension_class(mocker.MagicMock(), 'fake_dir', context)
    assert isinstance(result, ValidationResult)
    assert result.must_exit is True
    assert len(result.items) == 1
    item = result.items[0]
    assert isinstance(item, ValidationItem)
    assert item.level == 'ERROR'
    assert (
        'The extension class *KeyError* '
        'is not a subclass of *connect.eaas.core.extension.Extension*.'
    ) in item.message
    assert item.file == '/dir/file.py'


def test_validate_extension_class_descriptor_not_found(mocker):
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.inspect.getsourcefile',
        return_value='/dir/file.py',
    )

    mocker.patch.object(Extension, 'get_descriptor', side_effect=FileNotFoundError())

    class MyExt(Extension):
        pass

    context = {'extension_class': MyExt}
    result = validate_extension_class(mocker.MagicMock(), 'fake_dir', context)
    assert isinstance(result, ValidationResult)
    assert result.must_exit is True
    assert len(result.items) == 1
    item = result.items[0]
    assert isinstance(item, ValidationItem)
    assert item.level == 'ERROR'
    assert 'The extension descriptor *extension.json* cannot be loaded.' in item.message
    assert item.file == '/dir/extension.json'


@pytest.mark.parametrize(
    'descriptor',
    (
        {'capabilities': {}},
        {'variables': []},
        {'schedulables': []},
    ),
)
def test_validate_extension_class_descriptor_with_declarations(mocker, descriptor):
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.inspect.getsourcefile',
        return_value='/dir/file.py',
    )

    mocker.patch.object(Extension, 'get_descriptor', return_value=descriptor)

    class MyExt(Extension):
        pass

    context = {'extension_class': MyExt}
    result = validate_extension_class(mocker.MagicMock(), 'fake_dir', context)
    assert isinstance(result, ValidationResult)
    assert result.must_exit is False
    assert len(result.items) == 1
    item = result.items[0]
    assert isinstance(item, ValidationItem)
    assert item.level == 'WARNING'
    assert 'must be declared using' in item.message
    assert item.file == '/dir/extension.json'


def test_validate_events_invalid_event(mocker):
    extension_class = mocker.MagicMock()
    extension_class.get_events.return_value = [{
        'event_type': 'test_event',
        'method': 'event_handler',
    }]

    context = {'extension_class': extension_class}

    mocker.patch(
        'connect.cli.plugins.project.extension.validations.get_event_definitions',
        return_value=[],
    )

    mocker.patch(
        'connect.cli.plugins.project.extension.validations.get_code_context',
        return_value={
            'file': 'file',
            'start_line': 0,
            'lineno': 5,
            'code': 'code',
        },
    )

    result = validate_events(mocker.MagicMock(), 'fake_dir', context)

    assert isinstance(result, ValidationResult)
    assert result.must_exit is False
    assert len(result.items) == 1
    item = result.items[0]
    assert isinstance(item, ValidationItem)
    assert item.level == 'ERROR'
    assert 'The event type *test_event* is not valid.' in item.message
    assert item.file == 'file'
    assert item.start_line == 0
    assert item.lineno == 5
    assert item.code == 'code'


@pytest.mark.parametrize(
    ('object_statuses', 'event_statuses'),
    (
        (['status1', 'status2'], ['status3']),
        ([], ['status3']),
    ),
)
def test_validate_events_invalid_status(mocker, object_statuses, event_statuses):
    extension_class = mocker.MagicMock()
    extension_class.get_events.return_value = [{
        'event_type': 'test_event',
        'method': 'event_handler',
        'statuses': event_statuses,
    }]

    def event_handler(self, request):
        pass

    extension_class.event_handler = event_handler

    context = {'extension_class': extension_class}

    mocker.patch(
        'connect.cli.plugins.project.extension.validations.get_event_definitions',
        return_value=[
            {
                'type': 'test_event',
                'object_statuses': object_statuses,
            },
        ],
    )

    mocker.patch(
        'connect.cli.plugins.project.extension.validations.get_code_context',
        return_value={
            'file': 'file',
            'start_line': 0,
            'lineno': 5,
            'code': 'code',
        },
    )

    result = validate_events(mocker.MagicMock(), 'fake_dir', context)

    assert isinstance(result, ValidationResult)
    assert result.must_exit is False
    assert len(result.items) == 1
    item = result.items[0]
    assert isinstance(item, ValidationItem)
    assert item.level == 'ERROR'
    assert 'The status/es *status3* are invalid for the event *test_event*.' in item.message
    assert item.file == 'file'
    assert item.start_line == 0
    assert item.lineno == 5
    assert item.code == 'code'


def test_validate_events_invalid_signature(mocker):
    extension_class = mocker.MagicMock()
    extension_class.get_events.return_value = [{
        'event_type': 'test_event',
        'method': 'event_handler',
        'statuses': ['status'],
    }]

    def event_handler(self, request, other_arg):
        pass

    extension_class.event_handler = event_handler

    context = {'extension_class': extension_class}

    mocker.patch(
        'connect.cli.plugins.project.extension.validations.get_event_definitions',
        return_value=[
            {
                'type': 'test_event',
                'object_statuses': ['status'],
            },
        ],
    )

    mocker.patch(
        'connect.cli.plugins.project.extension.validations.get_code_context',
        return_value={
            'file': 'file',
            'start_line': 0,
            'lineno': 5,
            'code': 'code',
        },
    )

    result = validate_events(mocker.MagicMock(), 'fake_dir', context)

    assert isinstance(result, ValidationResult)
    assert result.must_exit is False
    assert len(result.items) == 1
    item = result.items[0]
    assert isinstance(item, ValidationItem)
    assert item.level == 'ERROR'
    assert 'The handler for the event *test_event* has an invalid signature' in item.message
    assert item.file == 'file'
    assert item.start_line == 0
    assert item.lineno == 5
    assert item.code == 'code'


def test_validate_schedulables_invalid_signature(mocker):
    extension_class = mocker.MagicMock()
    extension_class.get_schedulables.return_value = [{
        'method': 'event_handler',
    }]

    def event_handler(self, request, other_arg):
        pass

    extension_class.event_handler = event_handler

    context = {'extension_class': extension_class}

    mocker.patch(
        'connect.cli.plugins.project.extension.validations.get_code_context',
        return_value={
            'file': 'file',
            'start_line': 0,
            'lineno': 5,
            'code': 'code',
        },
    )

    result = validate_schedulables(mocker.MagicMock(), 'project_dir', context)

    assert isinstance(result, ValidationResult)
    assert result.must_exit is False
    assert len(result.items) == 1
    item = result.items[0]
    assert isinstance(item, ValidationItem)
    assert item.level == 'ERROR'
    assert 'The schedulable method *event_handler* has an invalid signature' in item.message
    assert item.file == 'file'
    assert item.start_line == 0
    assert item.lineno == 5
    assert item.code == 'code'


def test_validate_schedulables_no_schedulables(mocker):
    extension_class = mocker.MagicMock()
    extension_class.get_schedulables.return_value = []

    context = {'extension_class': extension_class}

    result = validate_schedulables(mocker.MagicMock(), 'project_dir', context)

    assert isinstance(result, ValidationResult)
    assert result.must_exit is False
    assert len(result.items) == 0


def test_validate_schedulables(mocker):
    extension_class = mocker.MagicMock()
    extension_class.get_schedulables.return_value = [{
        'method': 'event_handler',
    }]

    def event_handler(self, request):
        pass

    extension_class.event_handler = event_handler

    context = {'extension_class': extension_class}

    result = validate_schedulables(mocker.MagicMock(), 'project_dir', context)

    assert isinstance(result, ValidationResult)
    assert result.must_exit is False
    assert len(result.items) == 0


def test_validate_variables_no_name(mocker):
    extension_class = mocker.MagicMock()
    extension_class.get_variables.return_value = [{
        'initial_value': 'value',
    }]
    context = {'extension_class': extension_class}

    mocker.patch(
        'connect.cli.plugins.project.extension.validations.get_code_context',
        return_value={
            'file': 'file',
            'start_line': 0,
            'lineno': 5,
            'code': 'code',
        },
    )

    result = validate_variables(mocker.MagicMock(), 'project_dir', context)

    assert isinstance(result, ValidationResult)
    assert result.must_exit is False
    assert len(result.items) == 1
    item = result.items[0]
    assert isinstance(item, ValidationItem)
    assert item.level == 'ERROR'
    assert 'Invalid variable declaration: the *name* attribute is mandatory.' in item.message
    assert item.file == 'file'
    assert item.start_line == 0
    assert item.lineno == 5
    assert item.code == 'code'


def test_validate_variables_non_unique(mocker):
    extension_class = mocker.MagicMock()
    extension_class.get_variables.return_value = [
        {'name': 'VAR1'},
        {'name': 'VAR1'},
    ]
    context = {'extension_class': extension_class}

    mocker.patch(
        'connect.cli.plugins.project.extension.validations.get_code_context',
        return_value={
            'file': 'file',
            'start_line': 0,
            'lineno': 5,
            'code': 'code',
        },
    )

    result = validate_variables(mocker.MagicMock(), 'project_dir', context)

    assert isinstance(result, ValidationResult)
    assert result.must_exit is False
    assert len(result.items) == 1
    item = result.items[0]
    assert isinstance(item, ValidationItem)
    assert item.level == 'ERROR'
    assert (
        'Duplicate variable name: the variable with name *VAR1* '
        'has already been declared.'
    ) in item.message
    assert item.file == 'file'
    assert item.start_line == 0
    assert item.lineno == 5
    assert item.code == 'code'


def test_validate_variables_invalid_name(mocker):
    extension_class = mocker.MagicMock()
    extension_class.get_variables.return_value = [
        {'name': '1VAR'},
    ]
    context = {'extension_class': extension_class}

    mocker.patch(
        'connect.cli.plugins.project.extension.validations.get_code_context',
        return_value={
            'file': 'file',
            'start_line': 0,
            'lineno': 5,
            'code': 'code',
        },
    )

    result = validate_variables(mocker.MagicMock(), 'project_dir', context)

    assert isinstance(result, ValidationResult)
    assert result.must_exit is False
    assert len(result.items) == 1
    item = result.items[0]
    assert isinstance(item, ValidationItem)
    assert item.level == 'ERROR'
    assert 'Invalid variable name: the value *1VAR* does not match' in item.message
    assert item.file == 'file'
    assert item.start_line == 0
    assert item.lineno == 5
    assert item.code == 'code'


def test_validate_variables_invalid_initial_value(mocker):
    extension_class = mocker.MagicMock()
    extension_class.get_variables.return_value = [
        {
            'name': 'VAR1',
            'initial_value': mocker.MagicMock(),
        },
    ]
    context = {'extension_class': extension_class}

    mocker.patch(
        'connect.cli.plugins.project.extension.validations.get_code_context',
        return_value={
            'file': 'file',
            'start_line': 0,
            'lineno': 5,
            'code': 'code',
        },
    )

    result = validate_variables(mocker.MagicMock(), 'project_dir', context)

    assert isinstance(result, ValidationResult)
    assert result.must_exit is False
    assert len(result.items) == 1
    item = result.items[0]
    assert isinstance(item, ValidationItem)
    assert item.level == 'ERROR'
    assert 'Invalid *initial_value* attribute for variable *VAR1*:' in item.message
    assert item.file == 'file'
    assert item.start_line == 0
    assert item.lineno == 5
    assert item.code == 'code'


def test_validate_variables_invalid_secure(mocker):
    extension_class = mocker.MagicMock()
    extension_class.get_variables.return_value = [
        {
            'name': 'VAR1',
            'secure': mocker.MagicMock(),
        },
    ]
    context = {'extension_class': extension_class}

    mocker.patch(
        'connect.cli.plugins.project.extension.validations.get_code_context',
        return_value={
            'file': 'file',
            'start_line': 0,
            'lineno': 5,
            'code': 'code',
        },
    )

    result = validate_variables(mocker.MagicMock(), 'project_dir', context)

    assert isinstance(result, ValidationResult)
    assert result.must_exit is False
    assert len(result.items) == 1
    item = result.items[0]
    assert isinstance(item, ValidationItem)
    assert item.level == 'ERROR'
    assert 'Invalid *secure* attribute for variable *VAR1*:' in item.message
    assert item.file == 'file'
    assert item.start_line == 0
    assert item.lineno == 5
    assert item.code == 'code'


def test_validate_docker_compose_yml_not_found(mocker):
    result = validate_docker_compose_yml(mocker.MagicMock(), 'fake_dir', None)

    assert isinstance(result, ValidationResult)
    assert result.must_exit is False
    assert len(result.items) == 1
    item = result.items[0]
    assert isinstance(item, ValidationItem)
    assert item.level == 'WARNING'
    assert 'the file *docker-compose.yml* is not present.' in item.message
    assert item.file == 'fake_dir/docker-compose.yml'


def test_validate_docker_compose_yml_invalid_yml(mocker):
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.os.path.isfile',
        return_value=True,
    )
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.open',
    )
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.yaml.safe_load',
        side_effect=yaml.YAMLError(),
    )

    result = validate_docker_compose_yml(mocker.MagicMock(), 'fake_dir', None)

    assert isinstance(result, ValidationResult)
    assert result.must_exit is False
    assert len(result.items) == 1
    item = result.items[0]
    assert isinstance(item, ValidationItem)
    assert item.level == 'ERROR'
    assert 'The file *docker-compose.yml* is not valid.' in item.message
    assert item.file == 'fake_dir/docker-compose.yml'


def test_validate_docker_compose_yml_invalid_image(mocker):
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.os.path.isfile',
        return_value=True,
    )
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.open',
    )
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.get_pypi_runner_version',
        return_value='1.0',
    )
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.yaml.safe_load',
        return_value={
            'services': {
                'dev': {
                    'image': 'invalid:image',
                },
            },
        },
    )

    result = validate_docker_compose_yml(mocker.MagicMock(), 'fake_dir', None)

    assert isinstance(result, ValidationResult)
    assert result.must_exit is False
    assert len(result.items) == 1
    item = result.items[0]
    assert isinstance(item, ValidationItem)
    assert item.level == 'ERROR'
    assert (
        'Invalid image for service *dev*: expected '
        '*cloudblueconnect/connect-extension-runner:1.0* got *invalid:image*.'
    ) in item.message
    assert item.file == 'fake_dir/docker-compose.yml'


def test_validate_docker_compose_yml(mocker):
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.os.path.isfile',
        return_value=True,
    )
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.open',
    )
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.get_pypi_runner_version',
        return_value='1.0',
    )
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.yaml.safe_load',
        return_value={
            'services': {
                'dev': {
                    'image': 'cloudblueconnect/connect-extension-runner:1.0',
                },
            },
        },
    )

    result = validate_docker_compose_yml(mocker.MagicMock(), 'fake_dir', None)

    assert isinstance(result, ValidationResult)
    assert result.must_exit is False
    assert len(result.items) == 0


def test_get_code_context_module(mocker, faker):
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.inspect.getsourcefile',
        return_value='path/file.py',
    )

    code_lines = [f'{line}\n' for line in faker.paragraphs(nb=10)]

    code = ''.join(code_lines)

    mocker.patch(
        'connect.cli.plugins.project.extension.validations.inspect.getsourcelines',
        return_value=(
            code_lines,
            1,
        ),
    )
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.inspect.ismodule',
        return_value=True,
    )

    result = get_code_context(mocker.MagicMock(), 'country store build before')

    assert result['file'] == 'path/file.py'
    assert result['start_line'] == 1
    assert result['lineno'] == 7
    assert result['code'] == ''.join(code.splitlines(keepends=True)[0:7 + 3])


def test_get_code_context_function(mocker, faker):
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.inspect.getsourcefile',
        return_value='path/file.py',
    )

    code_lines = [f'{line}\n' for line in faker.paragraphs(nb=10)]

    code = ''.join(code_lines)

    mocker.patch(
        'connect.cli.plugins.project.extension.validations.inspect.getsourcelines',
        return_value=(
            code_lines,
            1,
        ),
    )
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.inspect.ismodule',
        return_value=False,
    )

    result = get_code_context(mocker.MagicMock(), 'country store build before')

    assert result['file'] == 'path/file.py'
    assert result['start_line'] == 1
    assert result['lineno'] == 7
    assert result['code'] == ''.join(code.splitlines(keepends=True))

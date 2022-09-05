import pytest
import toml
import yaml

from connect.cli.plugins.project.extension.validations import (
    validate_anvil_extension,
    validate_docker_compose_yml,
    validate_events,
    validate_extension_class,
    validate_pyproject_toml,
    validate_schedulables,
    validate_variables,
    validate_webapp_extension,
    ValidationItem,
    ValidationResult,
)
from connect.eaas.core.extension import EventsExtension, Extension
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
    assert (
        'The mandatory *pyproject.toml* project descriptor file is not present in the folder fake_dir.'
    ) in item.message
    assert item.file == 'fake_dir/pyproject.toml'


def test_validate_pyproject_toml_invalid_toml(mocker):
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.os.path.isfile',
        return_value=True,
    )
    mocker.patch(
        'connect.cli.plugins.project.validators.toml.load',
        side_effect=toml.TomlDecodeError('error', 'error', 0),
    )

    result = validate_pyproject_toml(mocker.MagicMock(), 'fake_dir', None)

    assert isinstance(result, ValidationResult)
    assert result.must_exit is True
    assert len(result.items) == 1
    item = result.items[0]
    assert isinstance(item, ValidationItem)
    assert item.level == 'ERROR'
    assert 'The project descriptor file *pyproject.toml* is not a valid toml file.' in item.message
    assert item.file == 'fake_dir/pyproject.toml'


def test_validate_pyproject_toml_depends_on_runner(mocker):
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.os.path.isfile',
        return_value=True,
    )
    mocker.patch(
        'connect.cli.plugins.project.validators.toml.load',
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
        'connect.cli.plugins.project.validators.toml.load',
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
        'connect.cli.plugins.project.validators.toml.load',
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
        'connect.cli.plugins.project.validators.toml.load',
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
        'connect.cli.plugins.project.validators.toml.load',
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
        'connect.cli.plugins.project.validators.toml.load',
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
    context = {'extension_classes': {'webapp': KeyError}}
    result = validate_extension_class(mocker.MagicMock(), 'fake_dir', context)
    assert isinstance(result, ValidationResult)
    assert result.must_exit is True
    assert len(result.items) == 1
    item = result.items[0]
    assert isinstance(item, ValidationItem)
    assert item.level == 'ERROR'
    assert (
        'The extension class *KeyError* '
        'is not a subclass of *connect.eaas.core.extension.WebAppExtension*.'
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

    context = {'extension_classes': {'extension': MyExt}}
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

    mocker.patch.object(EventsExtension, 'get_descriptor', return_value=descriptor)

    class MyExt(EventsExtension):
        pass

    context = {'extension_classes': {'extension': MyExt}}
    result = validate_extension_class(mocker.MagicMock(), 'fake_dir', context)
    assert isinstance(result, ValidationResult)
    assert result.must_exit is False
    assert len(result.items) == 1
    item = result.items[0]
    assert isinstance(item, ValidationItem)
    assert item.level == 'WARNING'
    assert 'must be declared using' in item.message
    assert item.file == '/dir/extension.json'


def test_validate_events_no_such_extension(mocker):
    extension_class = mocker.MagicMock()
    context = {'extension_classes': {'webapp': extension_class}}

    result = validate_events(mocker.MagicMock(), 'fake_dir', context)

    assert isinstance(result, ValidationResult)
    assert result.must_exit is False
    assert len(result.items) == 0


def test_validate_events_invalid_event(mocker):
    extension_class = mocker.MagicMock()
    extension_class.get_events.return_value = [{
        'event_type': 'test_event',
        'method': 'event_handler',
    }]

    context = {'extension_classes': {'extension': extension_class}}

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

    context = {'extension_classes': {'extension': extension_class}}

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

    context = {'extension_classes': {'extension': extension_class}}

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


def test_validate_schedulables_no_such_extension(mocker):
    extension_class = mocker.MagicMock()
    context = {'extension_classes': {'webapp': extension_class}}

    result = validate_schedulables(mocker.MagicMock(), 'fake_dir', context)

    assert isinstance(result, ValidationResult)
    assert result.must_exit is False
    assert len(result.items) == 0


def test_validate_schedulables_invalid_signature(mocker):
    extension_class = mocker.MagicMock()
    extension_class.get_schedulables.return_value = [{
        'method': 'event_handler',
    }]

    def event_handler(self, request, other_arg):
        pass

    extension_class.event_handler = event_handler

    context = {'extension_classes': {'extension': extension_class}}

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

    context = {'extension_classes': {'extension': extension_class}}

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

    context = {'extension_classes': {'extension': extension_class}}

    result = validate_schedulables(mocker.MagicMock(), 'project_dir', context)

    assert isinstance(result, ValidationResult)
    assert result.must_exit is False
    assert len(result.items) == 0


def test_validate_variables_no_name(mocker):
    extension_class = mocker.MagicMock()
    extension_class.get_variables.return_value = [{
        'initial_value': 'value',
    }]
    context = {'extension_classes': {'extension': extension_class}}

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
    context = {'extension_classes': {'extension': extension_class}}

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
    context = {'extension_classes': {'extension': extension_class}}

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
    context = {'extension_classes': {'extension': extension_class}}

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
    context = {'extension_classes': {'extension': extension_class}}

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


def test_validate_webapp_extension_no_such_extension(mocker):
    extension_class = mocker.MagicMock()
    context = {'extension_classes': {'events': extension_class}}

    result = validate_webapp_extension(mocker.MagicMock(), 'fake_dir', context)

    assert isinstance(result, ValidationResult)
    assert result.must_exit is False
    assert len(result.items) == 0


def test_validate_webapp_extension_no_class_wrapper(mocker):
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.inspect.getsource',
        return_value='class E2EWebAppExtension(WebAppExtension):....',
    )
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.inspect.getsourcefile',
        return_value='/dir/file.py',
    )

    context = {'extension_classes': {'webapp': mocker.MagicMock()}}
    result = validate_webapp_extension(mocker.MagicMock(), 'fake_dir', context)
    assert isinstance(result, ValidationResult)
    assert result.must_exit is True
    assert len(result.items) == 1
    item = result.items[0]
    assert isinstance(item, ValidationItem)
    assert item.level == 'ERROR'
    assert 'The Web app extension class must be wrapped in *@web_app(router)*.' in item.message


def test_validate_webapp_extension_no_router_methods(mocker):
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.inspect.getsource',
        side_effect=[
            '@web_app(router)\nclass E2EWebAppExtension(WebAppExtension):...',
            'def retrieve_settings(self):...',
        ],
    )
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.inspect.getsourcefile',
        return_value='/dir/file.py',
    )

    def f():
        pass

    mocker.patch(
        'connect.cli.plugins.project.extension.validations.inspect.getmembers',
        return_value=[('some_func', f)],
    )

    context = {'extension_classes': {'webapp': mocker.MagicMock()}}
    result = validate_webapp_extension(mocker.MagicMock(), 'fake_dir', context)
    assert isinstance(result, ValidationResult)
    assert result.must_exit is True
    assert len(result.items) == 1
    item = result.items[0]
    assert isinstance(item, ValidationItem)
    assert item.level == 'ERROR'
    assert 'The Web app extension class must contain at least one router' in item.message
    assert 'function wrapped in *@router.your_method("/your_path")*.' in item.message


def test_validate_webapp_extension_missing_static_files(mocker):
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.inspect.getsource',
        side_effect=[
            '@web_app(router)...\nclass E2EWebAppExtension(WebAppExtension):...',
            '@router.get("/settings")\ndef retrieve_settings(self):...',
        ],
    )
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.inspect.getsourcefile',
        return_value='/dir/file.py',
    )

    def f():
        pass

    mocker.patch(
        'connect.cli.plugins.project.extension.validations.inspect.getmembers',
        return_value=[('some_func', f)],
    )

    mocker.patch(
        'connect.cli.plugins.project.extension.validations.os.path.exists',
        return_value=False,
    )

    context = {
        'extension_classes': {'webapp': mocker.MagicMock()},
        'descriptor': {
            'name': 'My Awesome Project',
            'description': 'Project description',
            'version': '0.1.0',
            'readme_url': 'https://example.com/README.md',
            'changelog_url': 'https://example.com/CHANGELOG.md',
            'ui': {
                'settings': {
                    'label': 'My Settings',
                    'url': 'static/settings.html',
                },
                'customer': {
                    'label': 'My Customer Portal UI',
                    'url': 'static/customer.html',
                },
            },
        },
    }
    result = validate_webapp_extension(mocker.MagicMock(), 'fake_dir', context)
    assert isinstance(result, ValidationResult)
    assert result.must_exit is True
    assert len(result.items) == 1
    item = result.items[0]
    assert isinstance(item, ValidationItem)
    assert item.level == 'ERROR'
    assert 'The extension descriptor contains missing static files' in item.message
    assert 'static/customer.html, static/settings.html.' in item.message


def test_validate_webapp_extension_wrong_ui_setting(mocker):
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.inspect.getsource',
        side_effect=[
            '@web_app(router)...\nclass E2EWebAppExtension(WebAppExtension):...',
            '@router.get("/settings")\ndef retrieve_settings(self):...',
        ],
    )
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.inspect.getsourcefile',
        return_value='/dir/file.py',
    )

    def f():
        pass

    mocker.patch(
        'connect.cli.plugins.project.extension.validations.inspect.getmembers',
        return_value=[('some_func', f)],
    )

    context = {
        'extension_classes': {'webapp': mocker.MagicMock()},
        'descriptor': {
            'name': 'My Awesome Project',
            'description': 'Project description',
            'version': '0.1.0',
            'readme_url': 'https://example.com/README.md',
            'changelog_url': 'https://example.com/CHANGELOG.md',
            'ui': {
                'settings': {
                    'label': 'My Settings',
                    'path': 'static/settings.html',
                },
            },
        },
    }
    result = validate_webapp_extension(mocker.MagicMock(), 'fake_dir', context)
    assert isinstance(result, ValidationResult)
    assert result.must_exit is True
    assert len(result.items) == 1
    item = result.items[0]
    assert isinstance(item, ValidationItem)
    assert item.level == 'ERROR'
    assert 'The extension descriptor contains incorrect ui item' in item.message
    assert '*My Settings*, url is not presented.' in item.message


def test_validate_webapp_extension(mocker):
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.inspect.getsource',
        side_effect=[
            '@web_app(router)...\nclass E2EWebAppExtension(WebAppExtension):...',
            '@router.get("/settings")\ndef retrieve_settings(self):...',
        ],
    )
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.inspect.getsourcefile',
        return_value='/dir/file.py',
    )

    def f():
        pass

    mocker.patch(
        'connect.cli.plugins.project.extension.validations.inspect.getmembers',
        return_value=[('some_func', f)],
    )

    mocker.patch(
        'connect.cli.plugins.project.extension.validations.os.path.exists',
        return_value=True,
    )

    context = {
        'extension_classes': {'webapp': mocker.MagicMock()},
        'descriptor': {
            'name': 'My Awesome Project',
            'description': 'Project description',
            'version': '0.1.0',
            'readme_url': 'https://example.com/README.md',
            'changelog_url': 'https://example.com/CHANGELOG.md',
            'ui': {
                'settings': {
                    'label': 'My Settings',
                    'url': 'static/settings.html',
                },
                'customer': {
                    'label': 'My Customer Portal UI',
                    'url': 'static/customer.html',
                },
                'modules': {
                    'label': 'My Main Page',
                    'url': '/static/index.html',
                    'children': [
                        {
                            'label': 'Page 1',
                            'url': '/static/page1.html',
                        },
                        {
                            'label': 'Page 2',
                            'url': '/static/page2.html',
                        },
                    ],
                },
            },
        },
    }
    result = validate_webapp_extension(mocker.MagicMock(), 'fake_dir', context)
    assert isinstance(result, ValidationResult)
    assert result.must_exit is False
    assert len(result.items) == 0


def test_validate_anvil_extension_no_such_extension(mocker):
    context = {
        'extension_classes': {'webapp': mocker.MagicMock()},
    }
    result = validate_anvil_extension(mocker.MagicMock(), 'fake_dir', context)
    assert isinstance(result, ValidationResult)
    assert result.must_exit is False
    assert len(result.items) == 0


def test_validate_anvil_extension(mocker):
    anvil_extension_class = mocker.MagicMock()
    anvil_extension_class.get_anvil_key_variable.return_value = 'ANVIL_API_KEY'
    context = {'extension_classes': {'anvil': anvil_extension_class}}

    result = validate_anvil_extension(mocker.MagicMock(), 'fake_dir', context)

    assert isinstance(result, ValidationResult)
    assert result.must_exit is False
    assert len(result.items) == 0


def test_validate_anvil_extension_invalid_anvil_api_key(mocker):
    anvil_extension_class = mocker.MagicMock()
    anvil_extension_class.get_anvil_key_variable.return_value = '1ANVIL1'
    context = {'extension_classes': {'anvil': anvil_extension_class}}

    result = validate_anvil_extension(mocker.MagicMock(), 'fake_dir', context)

    assert isinstance(result, ValidationResult)
    assert result.must_exit is False
    assert len(result.items) == 1
    item = result.items[0]
    assert isinstance(item, ValidationItem)
    assert item.level == 'ERROR'
    assert 'Invalid Anvil key variable name: the value *1ANVIL1* does not match' in item.message

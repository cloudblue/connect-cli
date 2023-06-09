from functools import partial
from urllib.parse import urlparse

from interrogatio.validators import RequiredValidator

from connect.cli.plugins.project.extension.utils import (
    check_event_type_applicable,
    check_eventsapp_feature_not_selected,
    check_extension_not_multi_account,
    check_webapp_feature_not_selected,
    get_application_types,
    get_available_event_types,
    get_background_events,
    get_default_application_types,
    get_extension_types,
    get_interactive_events,
)
from connect.cli.plugins.project.extension.validators import AppTypesValidator, UISupportValidator
from connect.cli.plugins.project.utils import slugify
from connect.cli.plugins.project.validators import PythonIdentifierValidator


EXTENSION_BOOTSTRAP_WIZARD_INTRO = (
    'Welcome to the Connect Extension Project Bootstrap utility.\n'
    'Using this utility multiple data will be collected in order to create a project\n'
    'skeleton for your Connect Extension. This skeleton will contain all needed things\n'
    'to start writing your code.\n\n'
    'For more information please visit https://connect.cloudblue.com/community/modules/devops\n'
    'Have a nice trip!\n'
)


def get_summary(data):  # pragma: no cover
    def value(variable_name, formatted=False):
        if not data.get(variable_name):
            return ''

        data_value = data[variable_name]['formatted_value' if formatted else 'value']

        return data_value or '-'

    common = f"""<b><blue>Project</blue></b>
    <b>Project Name:</b> {value('project_name')} - <b>Package Name:</b> {value('package_name')}
    <b>Description:</b> {value('description')}
    <b>Author:</b> {value('author')}
    <b>Version:</b> {value('version')} - <b>License:</b> {value('license')}
    <b>Use Github Actions:</b> {value('use_github_actions', formatted=True)} - """

    common += f"""<b>Use Asyncio:</b> {value('use_asyncio', formatted=True)}
<b><blue>Config</blue></b>
    <b>API Key:</b> {value('api_key')}
    <b>Environment ID:</b> {value('environment_id')}
    <b>Server Address:</b> {value('server_address')}
"""

    extension = f"""<b><blue>Extension</blue></b>
    <b>Type:</b> {value('extension_type', formatted=True)}
"""
    if value('extension_type') in ('multiaccount', 'transformations'):
        extension += f"""    <b>Audience:</b> {value('extension_audience', formatted=True)}
"""
        extension += f"""    <b>Features:</b> {value('application_types', formatted=True)}
"""

    event_answers = f"""    <b>Events:</b> {value('event_types', formatted=True)}
"""

    if 'webapp' in value('application_types'):
        extension += f"""    <b>UI support:</b> {value('webapp_supports_ui', formatted=True)}
"""

    examples = f"""<b><blue>Examples</blue></b>
    <b>Variables:</b> {value('include_variables_example', formatted=True)}"""

    return common + extension + event_answers + examples


def get_questions(config, definitions):
    project = [
        {
            'name': 'project_name',
            'label': 'Project: name',
            'type': 'input',
            'description': 'Enter a friendly name for your Extension:',
            'default': 'My Awesome Project',
            'validators': (RequiredValidator(message='Please, provide a project name.'),),
        },
        {
            'name': 'project_slug',
            'label': 'Project: root',
            'type': 'input',
            'description': 'Choose a name for the root folder of your Extension module.',
            'default': lambda ctx: slugify(ctx['project_name']),
            'validators': [RequiredValidator(message='Please, provide a project root folder.')],
        },
        {
            'name': 'description',
            'label': 'Project: description',
            'type': 'input',
            'description': 'Briefly describe your Extension:',
            'default': 'Project description',
            'validators': (RequiredValidator(message='Please, provide a description.'),),
        },
        {
            'name': 'version',
            'label': 'Project: version',
            'type': 'input',
            'description': 'Introduce a version identifier for your Extension:',
            'default': '0.1.0',
            'validators': (RequiredValidator(message='Please, provide a version.'),),
        },
        {
            'name': 'author',
            'label': 'Project: author',
            'type': 'input',
            'description': 'Enter the name of the Extension author:',
            'default': 'Globex Corporation',
            'validators': (RequiredValidator(message='Please, provide an author name.'),),
        },
        {
            'name': 'license',
            'label': 'Project: license',
            'type': 'selectone',
            'description': 'Choose an Open Source license for your Extension:',
            'values': [
                ('Apache Software License 2.0', 'Apache Software License 2.0'),
                ('MIT', 'MIT'),
                ('BSD', 'BSD'),
            ],
            'formatting_template': '${label}',
        },
        {
            'name': 'package_name',
            'label': 'Project: package',
            'type': 'input',
            'description': (
                'Choose a name for the root python package of your extension module.'
                ' This must be a valid python\nidentifier:'
            ),
            'default': 'connect_ext',
            'validators': (
                RequiredValidator(message='Please, provide a package name.'),
                PythonIdentifierValidator(),
            ),
        },
        {
            'name': 'use_asyncio',
            'label': 'Project: asyncio',
            'type': 'selectone',
            'description': 'Do you want to develop your Extension using the Python asyncio library ?',
            'values': [
                ('n', 'No'),
                ('y', 'Yes'),
            ],
            'formatting_template': '${label}',
        },
        {
            'name': 'use_github_actions',
            'label': 'Project: CI',
            'type': 'selectone',
            'description': (
                'If you plan to host the Extension code on GitHub, are you also planning\n'
                'to use GitHub actions as your continuous integration system ?'
            ),
            'values': [
                ('n', 'No'),
                ('y', 'Yes'),
            ],
            'formatting_template': '${label}',
        },
    ]

    environment = [
        {
            'name': 'server_address',
            'label': 'Config: API hostname',
            'type': 'input',
            'description': 'Connect API hostname: ',
            'default': urlparse(config.active.endpoint).netloc,
            'validators': (RequiredValidator(message='Please, provide the API hostname.'),),
        },
        {
            'name': 'api_key',
            'label': 'Config: API key',
            'type': 'input',
            'description': (
                'Enter the API key that will be used to authenticate API calls to Connect:\n'
                'The API key can be created within the integration module of Connect.\n'
                'It defaults to the current active CLI account.'
            ),
            'default': config.active.api_key,
            'validators': (RequiredValidator(message='Please, provide an API Key.'),),
        },
        {
            'name': 'environment_id',
            'label': 'Config: environment ID',
            'type': 'input',
            'description': (
                'Enter the DevOps environment identifier to which your Extension will connect:\n'
                'It can be found in the DevOps module of Connect within the Local Access widget.\nSee: '
                'https://connect.cloudblue.com/community/modules/devops/user-interface/#Environment_ID_Specification'
            ),
            'validators': (RequiredValidator(message='Please, provide a DevOps environment ID.'),),
        },
    ]

    extension_type = [
        {
            'name': 'extension_type',
            'label': 'Extension: Extension type',
            'type': 'selectone',
            'description': 'Type of extension: ',
            'values': get_extension_types(config),
            'formatting_template': '${label}',
        },
        {
            'name': 'extension_audience',
            'label': 'Extension: Audience',
            'type': 'selectmany',
            'description': 'Which type of actors this extension targets: ',
            'values': [
                ('vendor', 'Vendors'),
                ('distributor', 'Distributors'),
                ('reseller', 'Resellers'),
            ],
            'formatting_template': '${label}',
            'disabled': check_extension_not_multi_account,
            'validators': (RequiredValidator(message='Please, select at least one option.'),),
        },
        {
            'name': 'application_types',
            'label': 'Extension: Features',
            'type': 'selectmany',
            'description': 'Which features do you want to support in your extension: ',
            'values': get_application_types,
            'default': get_default_application_types,
            'formatting_template': '${label}',
            'validators': (
                RequiredValidator(message='Please, select at least one option.'),
                AppTypesValidator(),
            ),
        },
        {
            'name': 'event_types',
            'label': 'Extension: Events type',
            'type': 'selectmany',
            'description': 'Which types of event do you want to support in your extension: ',
            'values': partial(get_available_event_types, definitions),
            'formatting_template': '${label}',
            'disabled': check_eventsapp_feature_not_selected,
            'validators': (RequiredValidator(message='Please, select at least one option.'),),
        },
        {
            'name': 'webapp_supports_ui',
            'label': 'Extension: WebApp',
            'type': 'selectone',
            'description': 'Does your web application plug into the Connect UI ? ',
            'values': [
                ('n', 'No'),
                ('y', 'Yes'),
            ],
            'default': 'y',
            'formatting_template': '${label}',
            'disabled': check_webapp_feature_not_selected,
            'validators': (UISupportValidator(),),
        },
    ]

    event_questions = [
        {
            'name': 'background',
            'label': 'Extension: Background events',
            'type': 'selectmany',
            'description': (
                'What types of background events do you want your Extension to process?'
            ),
            'values': partial(get_background_events, definitions),
            'formatting_template': '${label}',
            'disabled': partial(check_event_type_applicable, 'background'),
            'validators': (RequiredValidator(message='Please, select at least one option.'),),
        },
        {
            'name': 'interactive',
            'label': 'Extension: Interactive events',
            'type': 'selectmany',
            'description': (
                'What types of interactive events do you want your Extension to process?'
            ),
            'values': partial(get_interactive_events, definitions),
            'disabled': partial(check_event_type_applicable, 'interactive'),
            'formatting_template': '${label}',
            'validators': (RequiredValidator(message='Please, select at least one option.'),),
        },
    ]

    examples = [
        {
            'name': 'include_variables_example',
            'label': 'Examples: variables',
            'type': 'selectone',
            'description': 'Do you want to include an example of environment variables ? ',
            'values': [
                ('n', 'No'),
                ('y', 'Yes'),
            ],
            'formatting_template': '${label}',
        },
    ]

    return project + environment + extension_type + event_questions + examples

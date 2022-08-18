from urllib.parse import urlparse

from interrogatio.validators import RequiredValidator

from connect.cli.plugins.project.extension.utils import (
    check_extension_not_events_application,
    check_extension_not_hub,
    check_extension_not_multi_account,
    check_extension_not_products,
    get_extension_types,
)
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


def get_summary(config, definitions):
    common = """<b><blue>Project</blue></b>
    <b>Project Name:</b> ${project_name} - <b>Package Name:</b> ${package_name}
    <b>Description:</b> ${description}
    <b>Author:</b> ${author}
    <b>Version:</b> ${version} - <b>License:</b> ${license}
    <b>Use Github Actions:</b> ${use_github_actions} - <b>Use Asyncio:</b> ${use_asyncio}
<b><blue>Config</blue></b>
    <b>API Key:</b> ${api_key}
    <b>Environment ID:</b> ${environment_id}
    <b>Server Address:</b> ${server_address}
"""

    event_answers = '\n'.join(
        (
            f'<b><blue>{extension_type_name} {category} events:</blue></b>\n'
            '    ${' + f'{extension_type}_{category}_' + 'events}'
        )
        for extension_type, extension_type_name in get_extension_types(config)
        for category in ['background', 'interactive']
    ) + '\n'

    examples = """<b><blue>Examples</blue></b>
    <b>Schedulables:</b> ${include_schedules_example} - <b>Variables:</b> ${include_variables_example}
"""
    return common + event_answers + examples


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
            'validators': (RequiredValidator(message='Please, provide a project root folder.'),),
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
            'name': 'author',
            'label': 'Project: author',
            'type': 'input',
            'description': 'Enter the name of the Extension author:',
            'default': 'Globex Corporation',
            'validators': (RequiredValidator(message='Please, provide an author name.'),),
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
                'It can be found in the DevOps module of Connect within the Local Access widget.\n'
                'See: https://connect.cloudblue.com/community/modules/devops/user-interface/#Service_Details'
            ),
            'validators': (RequiredValidator(message='Please, provide a DevOps environment ID.'),),
        },
        {
            'name': 'server_address',
            'label': 'Config: API hostname',
            'type': 'input',
            'description': 'Connect API hostname: ',
            'default': urlparse(config.active.endpoint).netloc,
            'validators': (RequiredValidator(message='Please, provide the API hostname.'),),
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
            'name': 'application_types',
            'label': 'Extension: Application type',
            'type': 'selectmany',
            'description': 'Type of application: ',
            'values': [
                ('webapp', 'Web app'),
                ('anvil', 'Anvil app'),
                ('events', 'Events app'),
            ],
            'formatting_template': '${label}',
            'disabled': check_extension_not_multi_account,
        },
    ]

    if config.active.is_provider():
        event_questions = [
            {
                'name': f'hub_{category}_events',
                'label': f'Hub integration: {category} events',
                'type': 'selectmany',
                'description': (
                    f'What types of {category}'
                    'events do you want your Extension to process ?'
                ),
                'values': [
                    (event['type'], f'{event["group"]}: {event["name"]}')
                    for event in definitions['hub'][category]
                ],
                'formatting_template': '${label}',
                'disabled': check_extension_not_hub,
            }
            for category in [
                'background', 'interactive',
            ] if len(definitions['hub'][category]) > 0
        ]
    else:
        event_questions = [
            {
                'name': f'products_{category}_events',
                'label': f'Fulfillment Automation: {category} events',
                'type': 'selectmany',
                'description': (
                    f'What types of {category}'
                    'events do you want your Extension to process ?'
                ),
                'values': [
                    (event['type'], f'{event["group"]}: {event["name"]}')
                    for event in definitions['products'][category]
                ],
                'formatting_template': '${label}',
                'disabled': check_extension_not_products,
            }
            for category in [
                'background', 'interactive',
            ] if len(definitions['products'][category]) > 0
        ]

    event_questions.extend([
        {
            'name': f'multiaccount_{category}_events',
            'label': f'Multi-Account installation: {category} events',
            'type': 'selectmany',
            'description': (
                f'What types of {category}'
                'events do you want your Extension to process ?'
            ),
            'values': [
                (event['type'], f'{event["group"]}: {event["name"]}')
                for event in definitions['multiaccount'][category]
            ],
            'formatting_template': '${label}',
            'disabled': check_extension_not_events_application,
        }
        for category in [
            'background', 'interactive',
        ] if len(definitions['multiaccount'][category]) > 0
    ])

    examples = [
        {
            'name': 'include_schedules_example',
            'label': 'Examples: schedulables',
            'type': 'selectone',
            'description': 'Do you want to include an example of schedulable method ? ',
            'values': [
                ('n', 'No'),
                ('y', 'Yes'),
            ],
            'formatting_template': '${label}',
        },
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

from urllib.parse import urlparse

from interrogatio.validators import RequiredValidator

from connect.cli.plugins.project.cookiehelpers import slugify
from connect.cli.plugins.project.validators import PythonIdentifierValidator


EXTENSION_BOOTSTRAP_WIZARD_INTRO = (
    'Welcome to the Connect Extension Project Bootstrap utility.\n'
    'Using this utility multiple data will be collected in order to create a project\n'
    'skeleton for your Connect Extension. This skeleton will contain all needed things\n'
    'to start writing your code.\n\n'
    'For more information please visit https://connect.cloudblue.com/community/modules/devops\n'
    'Have a nice trip!\n'
)


def get_summary(config):
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
<b><blue>Subscriptions processing</blue></b>
    <b>Asset requests types:</b> ${asset_processing}
    <b>Tier configuration requests types:</b> ${asset_processing}
<b><blue>Listing processing</blue></b>
    <b>Listing requests types:</b> ${listing_request}
"""

    vendor_specific = """<b><blue>Products</blue></b>
    <b>Custom events:</b> ${product_capabilities_2of2} - <b>Actions:</b> ${product_capabilities_1of2}
<b><blue>Tier accounts</blue></b>
    <b>Update requests:</b> ${product_capabilities_2of2}
<b><blue>Validation</blue></b>
    <b>Asset requests type:</b> ${asset_validation}
    <b>Tier configuration requests type:</b> ${tierconfig_validation}
<b><blue>Usage</blue></b>
    <b>Usage files:</b> ${usage_file_process}
"""

    provider_specific = """<b><blue>Products</blue></b>
    <b>Custom events:</b> ${product_capabilities_2of2}
<b><blue>Usage</blue></b>
    <b>Usage chunk files:</b> ${usage_chunk_file_process}
"""

    examples = """<b><blue>Examples</blue></b>
    <b>Schedulables:</b> ${include_schedules_example} - <b>Variables:</b> ${include_variables_example}
"""

    return (
        common
        + (vendor_specific if config.active.is_vendor() else provider_specific)
        + examples
    )


def get_questions(config):
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

    common = [
        {
            'name': 'asset_processing',
            'label': 'Subscriptions: assets',
            'type': 'selectmany',
            'description': 'What types of asset requests do you want your Extension to process ?',
            'values': [
                ('subscription_process_capabilities_1of6', 'Purchase'),
                ('subscription_process_capabilities_2of6', 'Change'),
                ('subscription_process_capabilities_3of6', 'Suspend'),
                ('subscription_process_capabilities_4of6', 'Resume'),
                ('subscription_process_capabilities_5of6', 'Cancel'),
                ('subscription_process_capabilities_6of6', 'Adjustment'),
            ],
            'formatting_template': '${label}',
        },
        {
            'name': 'tierconfig',
            'label': 'Subscriptions: tier config',
            'type': 'selectmany',
            'description': 'What types of tier configuration requests do you want your Extension to process ?',
            'values': [
                ('tier_config_process_capabilities_1of3', 'Setup'),
                ('tier_config_process_capabilities_2of3', 'Change'),
                ('tier_config_process_capabilities_3of3', 'Adjustment'),
            ],
            'formatting_template': '${label}',
        },
        {
            'name': 'listing_request',
            'label': 'Listings',
            'type': 'selectmany',
            'description': 'What types of listing requests do you want your Extension to process ?',
            'values': [
                ('listing_request_process_new', 'New/Update'),
                ('listing_request_process_remove', 'Remove'),
            ],
            'formatting_template': '${label}',
        },
        {
            'name': 'product_capabilities_2of2',
            'label': 'Products: custom events',
            'type': 'selectone',
            'description': (
                'Will your extension support custom events ? Custom events are useful in the use\n'
                'case that an external system needs to interact with your extension running on the\n'
                'cloud.'
            ),
            'values': [
                ('n', 'No'),
                ('y', 'Yes'),
            ],
            'formatting_template': '${label}',
        },
    ]

    vendor_specific = [
        {
            'name': 'product_capabilities_1of2',
            'label': 'Products: actions',
            'type': 'selectone',
            'description': 'Will your extension support product actions ?',
            'values': [
                ('n', 'No'),
                ('y', 'Yes'),
            ],
            'formatting_template': '${label}',
        },
        {
            'name': 'tier_account_update_request',
            'label': 'Tiers: accounts',
            'type': 'selectone',
            'description': 'Do you want to process Tier Account Requests ?',
            'values': [
                ('n', 'No'),
                ('y', 'Yes'),
            ],
            'formatting_template': '${label}',
        },
        {
            'name': 'asset_validation',
            'label': 'Validation: assets',
            'type': 'selectmany',
            'description': 'What types of asset requests do you want your Extension to validate ?',
            'values': [
                ('subscription_validation_capabilities_1of2', 'Purchase'),
                ('subscription_validation_capabilities_2of2', 'Change'),
            ],
            'formatting_template': '${label}',
        },
        {
            'name': 'tierconfig_validation',
            'label': 'Validation: tier config',
            'type': 'selectmany',
            'description': 'What types of tier configuration requests do you want your Extension to validate ?',
            'values': [
                ('tier_config_validation_capabilities_1of2', 'Setup'),
                ('tier_config_validation_capabilities_2of2', 'Change'),
            ],
            'formatting_template': '${label}',
        },
        {
            'name': 'usage_file_process',
            'label': 'Usage: files',
            'type': 'selectone',
            'description': 'Do you want to process Usage Files ?',
            'values': [
                ('n', 'No'),
                ('y', 'Yes'),
            ],
            'formatting_template': '${label}',
        },
    ]

    provider_specific = [
        {
            'name': 'usage_chunk_file_process',
            'label': 'Usage: chunks',
            'type': 'selectone',
            'description': 'Do you want to process Usage Chunk Files ?',
            'values': [
                ('n', 'No'),
                ('y', 'Yes'),
            ],
            'formatting_template': '${label}',
        },
    ]

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

    return (
        project + environment + common
        + (vendor_specific if config.active.is_vendor() else provider_specific)
        + examples
    )

import json
import os
import shutil
from pathlib import Path
from urllib.parse import urlparse

import openpyxl
from click.exceptions import ClickException
from cookiecutter.config import DEFAULT_CONFIG
from cookiecutter.utils import rmtree
from interrogatio import dialogus
from interrogatio.themes import for_dialog
from interrogatio.validators.builtins import RequiredValidator
from prompt_toolkit.shortcuts import button_dialog

STATUSES = [
    'draft',
    'tiers_setup',
    'pending',
    'inquiring',
    'approved',
    'failed',
]

REQUESTS_SCHEDULED_ACTION_STATUSES = [
    'scheduled',
    'revoking',
    'revoked',
]

TIER_ACCOUNT_UPDATE_STATUSES = [
    'pending',
    'accepted',
    'ignored',
]

LISTING_REQUEST_STATUSES = [
    'draft',
    'reviewing',
    'deploying',
    'canceled',
    'completed',
]

USAGE_FILE_STATUSES = [
    'draft',
    'uploading',
    'uploaded',
    'invalid',
    'processing',
    'processed',
    'ready',
    'rejected',
    'pending',
    'accepted',
    'closed',
]

CHUNK_FILE_STATUSES = [
    'draft',
    'ready',
    'closed',
    'failed',
]


def purge_cookiecutters_dir():
    # Avoid asking rewrite clone boilerplate project
    cookie_dir = DEFAULT_CONFIG['cookiecutters_dir']
    if os.path.isdir(cookie_dir):
        rmtree(cookie_dir)


def _run_hook_from_repo_dir(
    repo_dir, hook_name, project_dir, context, delete_project_on_failure,
):
    '''Fake method for monkey patching purposes'''
    pass


def eaas_introduction(config, idx, total):
    message = (
        'Welcome to the Connect Extension Project Bootstrap utility.\n'
        'Using this utility multiple data will be collected in order to create a project\n'
        'skeleton for your Connect Extension. This skeleton will contain all needed things\n'
        'to start writing your code.\n\n'
        'Have a nice trip!\n'
    )
    return _show_cancel_next_dialog(msg=message, idx=idx, total=total)


def eaas_summary(answers, idx, total, config):
    summary_list = _prepare_summary(answers, config)
    message = f'The provided values for the project are:\n\n{summary_list}'
    _show_cancel_next_dialog(msg=message, idx=idx, total=total)
    return answers


def _summary_general_questions(answers):
    general_data = {
        'Project Name': answers['project_name'],
        'Description': answers['description'],
        'Package Name': answers['package_name'],
        'Author': answers['author'],
        'Version': answers['version'],
        'License': answers['license'],
        'Use Github Actions': 'Yes' if answers['use_github_actions'] == 'y' else 'No',
        'Use Asyncio': 'Yes' if answers['use_asyncio'] == 'y' else 'No',
        'API Key': answers['api_key'],
        'Environment ID': answers['environment_id'],
        'Server Address': answers['server_address'],
    }
    return general_data


def _summary_asset_questions(answers):
    asset_data = {
        'Process Asset Purchase requests': 'Yes' if answers.get(
            'subscription_process_capabilities_1of6', '',
        ) == 'y' else 'No',
        'Process Asset Change requests': 'Yes' if answers.get(
            'subscription_process_capabilities_2of6', '',
        ) == 'y' else 'No',
        'Process Asset Suspend requests': 'Yes' if answers.get(
            'subscription_process_capabilities_3of6', '',
        ) == 'y' else 'No',
        'Process Asset Resume requests': 'Yes' if answers.get(
            'subscription_process_capabilities_4of6', '',
        ) == 'y' else 'No',
        'Process Asset Cancel requests': 'Yes' if answers.get(
            'subscription_process_capabilities_5of6', '',
        ) == 'y' else 'No',
        'Process Asset Adjustment requests': 'Yes' if answers.get(
            'subscription_process_capabilities_6of6', '',
        ) == 'y' else 'No',
    }
    return asset_data


def _summary_asset_validation_questions(answers):
    asset_data = {
        'Validate Asset Purchase requests': 'Yes' if answers.get(
            'subscription_validation_capabilities_1of2', '',
        ) == 'y' else 'No',
        'Validate Asset Change requests': 'Yes' if answers.get(
            'subscription_validation_capabilities_2of2', '',
        ) == 'y' else 'No',
    }
    return asset_data


def _summary_product_actions_questions(answers):
    product_data = {
        'Execute Product Actions': 'Yes' if answers.get(
            'product_capabilities_1of2', '',
        ) == 'y' else 'No',
    }
    return product_data


def _summary_product_custom_events_questions(answers):
    product_data = {
        'Process Product Custom Events': 'Yes' if answers.get(
            'product_capabilities_2of2', '',
        ) == 'y' else 'No',
    }
    return product_data


def _summary_tier_config_validation(answers):
    tier_data = {
        'Validate Tier Config Setup requests': 'Yes' if answers.get(
            'tier_config_validation_capabilities_1of2', '',
        ) == 'y' else 'No',
        'Validate Tier Config Change requests': 'Yes' if answers.get(
            'tier_config_validation_capabilities_2of2', '',
        ) == 'y' else 'No',
    }
    return tier_data


def _summary_tier_account_questions(answers):
    tier_data = {
        'Process Tier Accounts Update requests': 'Yes' if answers.get(
            'tier_account_update_request', '',
        ) == 'y' else 'No',
    }
    return tier_data


def _summary_tier_questions(answers):
    tier_data = {
        'Process Tier Config Setup requests': 'Yes' if answers.get(
            'tier_config_process_capabilities_1of3', '',
        ) == 'y' else 'No',
        'Process Tier Config Change requests': 'Yes' if answers.get(
            'tier_config_process_capabilities_2of3', '',
        ) == 'y' else 'No',
        'Process Tier Config Adjustment requests': 'Yes' if answers.get(
            'tier_config_process_capabilities_3of3', '',
        ) == 'y' else 'No',
    }
    return tier_data


def _summary_usage_files(answers):
    usage_data = {
        'Process Usage Files': 'Yes' if answers.get(
            'usage_file_process', '',
        ) == 'y' else 'No',
    }

    return usage_data


def _summary_usage_chunk_files(answers):
    usage_data = {
        'Process Usage Chunk Files': 'Yes' if answers.get(
            'usage_chunk_file_process', '',
        ) == 'y' else 'No',
    }

    return usage_data


def _summary_listing_requests(answers):
    listing_req_data = {
        'Process New Listing Requests': 'Yes' if answers.get(
            'listing_request_process_new', '',
        ) == 'y' else 'No',
        'Process Listing Removal Requests': 'Yes' if answers.get(
            'listing_request_process_remove', '',
        ) == 'y' else 'No',
    }

    return listing_req_data


def _summary_examples(answers):
    examples_data = {
        'Include Schedulables example into extension project': 'Yes' if answers.get(
            'include_schedules_example', '',
        ) == 'y' else 'No',
        'Include Environment variables example into extension project': 'Yes' if answers.get(
            'include_variables_example', '',
        ) == 'y' else 'No',
    }

    return examples_data


def _prepare_summary(answers, config):
    result = {}
    result.update(_summary_general_questions(answers))
    result.update(_summary_asset_questions(answers))
    result.update(_summary_product_custom_events_questions(answers))
    if config.active.is_vendor():
        result.update(_summary_asset_validation_questions(answers))
        result.update(_summary_product_actions_questions(answers))
        result.update(_summary_usage_files(answers))
        result.update(_summary_tier_config_validation(answers))
    if config.active.is_provider():
        result.update(_summary_usage_chunk_files(answers))
    result.update(_summary_tier_questions(answers))
    result.update(_summary_tier_account_questions(answers))
    result.update(_summary_listing_requests(answers))
    result.update(_summary_examples(answers))
    return '\n'.join(f'{item[0]}: {item[1]}' for item in result.items())


def general_extension_questions(config, idx, total):
    questions = [
        {
            'name': 'project_name',
            'type': 'input',
            'message': 'Extension project name: ',
            'default': 'My Awesome Project',
            'validators': (RequiredValidator(message='Please, provide a project name.'),),
        },
        {
            'name': 'description',
            'type': 'input',
            'message': 'Extension project description: ',
            'default': 'Project description',
            'validators': (RequiredValidator(message='Please, provide a description.'),),
        },
        {
            'name': 'package_name',
            'type': 'input',
            'message': 'Extension project package name: ',
            'default': 'connect_ext',
            'validators': (RequiredValidator(message='Please, provide a package name.'),),
        },
        {
            'name': 'author',
            'type': 'input',
            'message': 'Extension project author: ',
            'default': 'Globex Corporation',
            'validators': (RequiredValidator(message='Please, provide an author name.'),),
        },
        {
            'name': 'version',
            'type': 'input',
            'message': 'Extension project version: ',
            'default': '0.1.0',
            'validators': (RequiredValidator(message='Please, provide a version.'),),
        },
        {
            'name': 'license',
            'type': 'selectone',
            'description': 'Extension project license: ',
            'values': [
                ('Apache Software License 2.0', 'Apache Software License 2.0'),
                ('MIT', 'MIT'),
                ('BSD', 'BSD'),
            ],
        },
        {
            'name': 'use_github_actions',
            'type': 'selectone',
            'description': 'Do you want to use Github actions? ',
            'values': [
                ('n', 'No'),
                ('y', 'Yes'),
            ],
        },
        {
            'name': 'use_asyncio',
            'type': 'selectone',
            'description': 'Do you want to use asynchronous libraries? ',
            'values': [
                ('n', 'No'),
                ('y', 'Yes'),
            ],
        },
    ]
    answers = _show_dialog(questions, idx, total)
    return answers


def credentials_questions(config, idx, total):
    config.validate()
    active_api_key = config.active.api_key or 'ApiKey XXXXXXX:xxxxxxxxxxxxxxxxxxxxxxxxxxx'
    active_server = urlparse(config.active.endpoint).netloc or 'api.connect.cloudblue.com'
    questions = [
        {
            'name': 'api_key',
            'type': 'input',
            'message': 'API Key from Connect integration module: ',
            'default': active_api_key,
            'validators': (RequiredValidator(message='Please, provide an API Key.'),),
        },
        {
            'name': 'environment_id',
            'type': 'input',
            'message': 'Environment ID from DevOps module: ',
            'default': 'a1a1a1a1-b2b2-c3c3-d4d4-e5e5e5e5e5e5',
            'validators': (RequiredValidator(message='Please, provide a valid environment id.'),),
        },
        {
            'name': 'server_address',
            'type': 'input',
            'message': 'Connect API hostname: ',
            'default': active_server,
            'validators': (RequiredValidator(message='Please, provide a server address.'),),
        },
    ]
    answers = _show_dialog(questions, idx, total)
    return answers


def asset_process_capabilities(config, idx, total):
    questions = [
        {
            'name': 'asset_processing',
            'type': 'selectmany',
            'description': 'Asset processing capabilities',
            'values': [
                ('subscription_process_capabilities_1of6', 'Purchase Request'),
                ('subscription_process_capabilities_2of6', 'Change Request'),
                ('subscription_process_capabilities_3of6', 'Suspend Request'),
                ('subscription_process_capabilities_4of6', 'Resume Request'),
                ('subscription_process_capabilities_5of6', 'Cancel Request'),
                ('subscription_process_capabilities_6of6', 'Adjustment Request'),
            ],
        },
    ]
    answers = _show_dialog(questions, idx, total)
    return _gen_cookie_capabilities(answers['asset_processing'])


def asset_validation_capabilities(config, idx, total):
    questions = [
        {
            'name': 'asset_validation',
            'type': 'selectmany',
            'description': 'Asset validation capabilities',
            'values': [
                ('subscription_validation_capabilities_1of2', 'Purchase Request'),
                ('subscription_validation_capabilities_2of2', 'Change Request'),
            ],
        },
    ]
    answers = _show_dialog(questions, idx, total)
    return _gen_cookie_capabilities(answers['asset_validation'])


def tier_config_validation_capabilities(config, idx, total):
    questions = [
        {
            'name': 'tierconfig_validation',
            'type': 'selectmany',
            'description': 'Tier configuration validation capabilities',
            'values': [
                ('tier_config_validation_capabilities_1of2', 'Setup Request Validation'),
                ('tier_config_validation_capabilities_2of2', 'Change Request Validation'),
            ],
        },
    ]
    answers = _show_dialog(questions, idx, total)
    return _gen_cookie_capabilities(answers['tierconfig_validation'])


def tier_config_processing_capabilities(config, idx, total):
    questions = [
        {
            'name': 'tierconfig',
            'type': 'selectmany',
            'description': 'Tier configuration capabilities',
            'values': [
                ('tier_config_process_capabilities_1of3', 'Setup Request Processing'),
                ('tier_config_process_capabilities_2of3', 'Change Request Processing'),
                ('tier_config_process_capabilities_3of3', 'Adjustment Request Processing'),
                ('tier_config_validation_capabilities_1of2', 'Setup Request Validation'),
                ('tier_config_validation_capabilities_1of2', 'Change Request Validation'),
            ],
        },
    ]
    answers = _show_dialog(questions, idx, total)
    return _gen_cookie_capabilities(answers['tierconfig'])


def product_custom_events_capability(config, idx, total):
    questions = [
        {
            'name': 'product_capabilities_2of2',
            'type': 'selectone',
            'description': (
                'Will your extension support custom events? Custom events are useful in the use '
                'case that an external system needs to interact with your extension running on the '
                'cloud.'
            ),
            'values': [
                ('n', 'No'),
                ('y', 'Yes'),
            ],
        },
    ]
    return _show_dialog(questions, idx, total)


def product_actions_capability(config, idx, total):
    questions = [
        {
            'name': 'product_capabilities_1of2',
            'type': 'selectone',
            'description': 'Will your extension support product actions?',
            'values': [
                ('n', 'No'),
                ('y', 'Yes'),
            ],
        },
    ]
    return _show_dialog(questions, idx, total)


def tier_account_capabilities(config, idx, total):
    questions = [
        {
            'name': 'tier_account_update_request',
            'type': 'selectone',
            'description': 'Do you want to process Tier Account Requests?',
            'values': [
                ('n', 'No'),
                ('y', 'Yes'),
            ],
        },
    ]
    return _show_dialog(questions, idx, total)


def usage_files_capabilities(config, idx, total):
    questions = [
        {
            'name': 'usage_file_process',
            'type': 'selectone',
            'description': 'Do you want to process Usage Files?',
            'values': [
                ('n', 'No'),
                ('y', 'Yes'),
            ],
        },
    ]
    return _show_dialog(questions, idx, total)


def usage_chunk_files_capabilities(config, idx, total):
    questions = [
        {
            'name': 'usage_chunk_file_process',
            'type': 'selectone',
            'description': 'Do you want to process Usage Chunk Files?',
            'values': [
                ('n', 'No'),
                ('y', 'Yes'),
            ],
        },
    ]
    return _show_dialog(questions, idx, total)


def listing_request_capabilities(config, idx, total):
    questions = [
        {
            'name': 'listing_request',
            'type': 'selectmany',
            'description': 'Listing Requests',
            'values': [
                ('listing_request_process_new', 'Process New Listing Requests'),
                ('listing_request_process_remove', 'Process Listing Requests Removals'),
            ],
        },
    ]
    answers = _show_dialog(questions, idx, total)
    return _gen_cookie_capabilities(answers['listing_request'])


def include_schedulables_example(config, idx, total):
    questions = [
        {
            'name': 'include_schedules_example',
            'type': 'selectone',
            'description': 'Do you want to include an example of schedulable method? ',
            'values': [
                ('n', 'No'),
                ('y', 'Yes'),
            ],
        },
    ]
    return _show_dialog(questions, idx, total)


def include_variables_example(config, idx, total):
    questions = [
        {
            'name': 'include_variables_example',
            'type': 'selectone',
            'description': 'Do you want to include an example of environment variables? ',
            'values': [
                ('n', 'No'),
                ('y', 'Yes'),
            ],
        },
    ]
    return _show_dialog(questions, idx, total)


def _show_dialog(questions, idx, total):
    confirm = 'Create' if idx == total else 'Next'
    answers = dialogus(
        questions,
        title=f'Extension Project Configuration ({idx}/{total})',
        confirm=confirm,
    )
    if not answers:
        raise ClickException('Aborted by user input')
    return answers


def _show_cancel_next_dialog(msg, idx, total):
    confirm = 'Create' if idx == total else 'Next'
    clicked_next = button_dialog(
        title=f'Extension Project Configuration ({idx}/{total})',
        text=msg,
        buttons=[('Cancel', False), (confirm, True)],
        style=for_dialog(),
    ).run()
    if not clicked_next:
        raise ClickException('Aborted by user input')
    return []


def _gen_cookie_capabilities(answers):
    cookicutter_answers = {}
    if answers:
        for capability in answers:
            cookicutter_answers[capability] = 'y'

    return cookicutter_answers


def pre_gen_cookiecutter_extension_hook(answers: dict):
    pr_slug = _slugify(answers['project_name'])
    if hasattr(pr_slug, 'isidentifier') and not pr_slug.isidentifier():
        raise ClickException(f'{pr_slug} project slug is not a valid Python identifier.')

    pk_slug = _slugify(answers['package_name'])
    if hasattr(pk_slug, 'isidentifier') and not pk_slug.isidentifier():
        raise ClickException(f'{pk_slug} package slug is not a valid Python identifier.')


def post_gen_cookiecutter_extension_hook(answers: dict, project_dir: str, config):
    if answers['use_github_actions'].lower() == 'n':
        _remove_github_actions(project_dir)

    pr_slug = _slugify(answers['project_name'])
    pk_slug = _slugify(answers['package_name'])
    descriptor = json.load(open(f'{pr_slug}/{pk_slug}/extension.json'))

    # general
    _json_subscription_process_capabilities(descriptor, answers)
    _json_tierconfig_processing_capabilities(descriptor, answers)
    _json_tieraccount_capabilities(descriptor, answers)
    _json_listing_request_capabilities(descriptor, answers)
    _json_product_custom_events(descriptor, answers)

    if config.active.is_vendor():
        _json_product_actions(descriptor, answers)
        _json_subscription_validation_capabilities(descriptor, answers)
        _json_usage_files_capabilities(descriptor, answers)
        _json_tier_config_validation_capabilities(descriptor, answers)

    if config.active.is_provider():
        _json_usage_chunk_files_capabilities(descriptor, answers)

    _join_schedulable_example(descriptor, answers)
    _join_variables_example(descriptor, answers)

    json.dump(descriptor, open(f'{pr_slug}/{pk_slug}/extension.json', 'w'), indent=2)
    print('Done! Your extension project is ready to go!')


def _slugify(name):
    return name.lower().strip().replace(' ', '_').replace('-', '_').replace('.', '_').replace(',', '')


def _remove_github_actions(project_dir: str):
    shutil.rmtree(f'{project_dir}/.github')


def _json_tieraccount_capabilities(descriptor: dict, answers: dict):
    if (
        'tier_account_update_request' in answers.keys()
        and answers['tier_account_update_request'].lower() == 'y'
    ):
        descriptor['capabilities'][
            'tier_account_update_request_processing'] = TIER_ACCOUNT_UPDATE_STATUSES


def _json_usage_files_capabilities(descriptor: dict, answers: dict):
    if (
        'usage_file_process' in answers.keys()
        and answers['usage_file_process'].lower() == 'y'
    ):
        descriptor['capabilities'][
            'usage_file_request_processing'] = USAGE_FILE_STATUSES


def _json_usage_chunk_files_capabilities(descriptor: dict, answers: dict):
    if (
        'usage_chunk_file_process' in answers.keys()
        and answers['usage_chunk_file_process'].lower() == 'y'
    ):
        descriptor['capabilities'][
            'part_usage_file_request_processing'] = CHUNK_FILE_STATUSES


def _join_schedulable_example(descriptor: dict, answers: dict):
    if (
        'include_schedules_example' in answers.keys()
        and answers['include_schedules_example'].lower() == 'y'
    ):
        descriptor['schedulables'] = [{
            'name': 'Schedulable method mock',
            'description': 'It can be used to test DevOps scheduler.',
            'method': 'execute_scheduled_processing',
        }]


def _join_variables_example(descriptor: dict, answers: dict):
    if (
        'include_variables_example' in answers.keys()
        and answers['include_variables_example'].lower() == 'y'
    ):
        descriptor['variables'] = [
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
        ]


def _json_listing_request_capabilities(descriptor: dict, answers: dict):
    if (
        'listing_request_process_new' in answers.keys()
        and answers['listing_request_process_new'].lower() == 'y'
    ):
        descriptor['capabilities'][
            'listing_new_request_processing'] = LISTING_REQUEST_STATUSES
    if (
        'listing_request_process_remove' in answers.keys()
        and answers['listing_request_process_remove'].lower() == 'y'
    ):
        descriptor['capabilities'][
            'listing_remove_request_processing'] = LISTING_REQUEST_STATUSES


def _json_subscription_process_capabilities(descriptor: dict, answers: dict):
    if (
        'subscription_process_capabilities_1of6' in answers.keys()
        and answers['subscription_process_capabilities_1of6'].lower() == 'y'
    ):
        descriptor['capabilities'][
            'asset_purchase_request_processing'
        ] = STATUSES + REQUESTS_SCHEDULED_ACTION_STATUSES
    if (
        'subscription_process_capabilities_2of6' in answers.keys()
        and answers['subscription_process_capabilities_2of6'].lower() == 'y'
    ):
        descriptor['capabilities'][
            'asset_change_request_processing'
        ] = STATUSES + REQUESTS_SCHEDULED_ACTION_STATUSES
    if (
        'subscription_process_capabilities_3of6' in answers.keys()
        and answers['subscription_process_capabilities_3of6'].lower() == 'y'
    ):
        descriptor['capabilities'][
            'asset_suspend_request_processing'
        ] = STATUSES + REQUESTS_SCHEDULED_ACTION_STATUSES
    if (
        'subscription_process_capabilities_4of6' in answers.keys()
        and answers['subscription_process_capabilities_4of6'].lower() == 'y'
    ):
        descriptor['capabilities'][
            'asset_resume_request_processing'
        ] = STATUSES + REQUESTS_SCHEDULED_ACTION_STATUSES
    if (
        'subscription_process_capabilities_5of6' in answers.keys()
        and answers['subscription_process_capabilities_5of6'].lower() == 'y'
    ):
        descriptor['capabilities'][
            'asset_cancel_request_processing'
        ] = STATUSES + REQUESTS_SCHEDULED_ACTION_STATUSES
    if (
        'subscription_process_capabilities_6of6' in answers.keys()
        and answers['subscription_process_capabilities_6of6'].lower() == 'y'
    ):
        descriptor['capabilities']['asset_adjustment_request_processing'] = STATUSES


def _json_subscription_validation_capabilities(descriptor: dict, answers: dict):
    if (
        'subscription_validation_capabilities_1of2' in answers.keys()
        and answers['subscription_validation_capabilities_1of2'].lower() == 'y'
    ):
        descriptor['capabilities']['asset_purchase_request_validation'] = STATUSES
    if (
        'subscription_validation_capabilities_2of2' in answers.keys()
        and answers['subscription_validation_capabilities_2of2'].lower() == 'y'
    ):
        descriptor['capabilities']['asset_change_request_validation'] = STATUSES


def _json_tier_config_validation_capabilities(descriptor: dict, answers: dict):
    # Validation
    if (
            'tier_config_validation_capabilities_1of2' in answers.keys()
            and answers['tier_config_validation_capabilities_1of2'].lower() == 'y'
    ):
        descriptor['capabilities']['tier_config_setup_request_validation'] = STATUSES
    if (
            'tier_config_validation_capabilities_2of2' in answers.keys()
            and answers['tier_config_validation_capabilities_2of2'].lower() == 'y'
    ):
        descriptor['capabilities']['tier_config_change_request_validation'] = STATUSES


def _json_tierconfig_processing_capabilities(descriptor: dict, answers: dict):
    # Processing
    if (
        'tier_config_process_capabilities_1of3' in answers.keys()
        and answers['tier_config_process_capabilities_1of3'].lower() == 'y'
    ):
        descriptor['capabilities']['tier_config_setup_request_processing'] = STATUSES
    if (
        'tier_config_process_capabilities_2of3' in answers.keys()
        and answers['tier_config_process_capabilities_2of3'].lower() == 'y'
    ):
        descriptor['capabilities']['tier_config_change_request_processing'] = STATUSES
    if (
        'tier_config_process_capabilities_3of3' in answers.keys()
        and answers['tier_config_process_capabilities_3of3'].lower() == 'y'
    ):
        descriptor['capabilities']['tier_config_adjustment_request_processing'] = STATUSES


def _json_product_custom_events(descriptor: dict, answers: dict):
    if (
        'product_capabilities_2of2' in answers.keys()
        and answers['product_capabilities_2of2'].lower() == 'y'
    ):
        descriptor['capabilities']['product_custom_event_processing'] = []


def _json_product_actions(descriptor: dict, answers: dict):
    if (
        'product_capabilities_1of2' in answers.keys()
        and answers['product_capabilities_1of2'].lower() == 'y'
    ):
        descriptor['capabilities']['product_action_execution'] = []


def pre_gen_cookiecutter_report_hook(answers: dict):
    project_slug = _slugify(answers['project_name'])
    if hasattr(project_slug, 'isidentifier') and not project_slug.isidentifier():
        raise ClickException(f'{project_slug} project slug is not a valid Python identifier.')

    package_slug = _slugify(answers['package_name'])
    if hasattr(package_slug, 'isidentifier') and not package_slug.isidentifier():
        raise ClickException(f'{package_slug} project slug is not a valid Python identifier.')

    initial_report_slug = _slugify(answers['initial_report_name'])
    if hasattr(initial_report_slug, 'isidentifier') and not initial_report_slug.isidentifier():
        raise ClickException(f'{initial_report_slug} report slug is not a valid Python identifier.')


def post_gen_cookiecutter_report_hook(answers: dict, project_dir: str):
    if answers['use_github_actions'] == 'n':
        _remove_github_actions(project_dir)

    _create_renderer_templates(answers)

    print('Done! Your report project is ready to go!')


def _create_renderer_templates(answers: dict):
    project_slug = _slugify(answers['project_name'])
    package_slug = _slugify(answers['package_name'])
    initial_report_slug = _slugify(answers['initial_report_name'])

    # XLSX
    xlsx_template_dir = f'{project_slug}/{package_slug}/{initial_report_slug}/templates/xlsx'
    os.makedirs(xlsx_template_dir)
    wb = openpyxl.Workbook()
    wb.save(f'{xlsx_template_dir}/template.xlsx')

    # PDF
    pdf_template_dir = f'{project_slug}/{package_slug}/{initial_report_slug}/templates/pdf'
    os.makedirs(pdf_template_dir)
    Path(f'{pdf_template_dir}/template.css').touch()
    Path(f'{pdf_template_dir}/template.html.j2').touch()

    # JINJA2
    jinja2_template_dir = f'{project_slug}/{package_slug}/{initial_report_slug}/templates/xml'
    os.makedirs(jinja2_template_dir)
    open(f'{jinja2_template_dir}/template.xml.j2', 'w').write(
        'Please rename this file with a proper extension file.\n',
    )


def general_report_questions():
    questions = [
        {
            'name': 'project_name',
            'type': 'input',
            'message': 'Reports project name: ',
            'default': 'My Awesome Project',
            'validators': (RequiredValidator(message='Please, provide a project name.'),),
        },
        {
            'name': 'description',
            'type': 'input',
            'message': 'Reports project description: ',
            'default': 'Project description',
            'validators': (RequiredValidator(message='Please, provide a description.'),),
        },
        {
            'name': 'package_name',
            'type': 'input',
            'message': 'Reports project package name: ',
            'default': 'reports',
            'validators': (RequiredValidator(message='Please, provide a package name.'),),
        },
        {
            'name': 'initial_report_name',
            'type': 'input',
            'message': 'Initial report name: ',
            'default': 'My Awesome Report',
            'validators': (RequiredValidator(message='Please, provide a report name.'),),
        },
        {
            'name': 'initial_report_description',
            'type': 'input',
            'message': 'Initial report description: ',
            'default': 'This report provides all data I need',
            'validators': (RequiredValidator(message='Please, provide a description.'),),
        },
        {
            'name': 'initial_report_renderer',
            'type': 'selectone',
            'description': 'Initial report renderer: ',
            'values': [
                ('xlsx', 'xlsx'),
                ('csv', 'csv'),
                ('pdf', 'pdf'),
                ('json', 'json'),
                ('jinja2', 'jinja2'),
            ],
        },
        {
            'name': 'author',
            'type': 'input',
            'message': 'Reports project author: ',
            'default': 'Globex Corporation',
            'validators': (RequiredValidator(message='Please, provide an author name.'),),
        },
        {
            'name': 'version',
            'type': 'input',
            'message': 'Reports project version: ',
            'default': '0.1.0',
            'validators': (RequiredValidator(message='Please, provide a version.'),),
        },
        {
            'name': 'license',
            'type': 'selectone',
            'description': 'Reports project license: ',
            'values': [
                ('Apache Software License 2.0', 'Apache Software License 2.0'),
                ('MIT', 'MIT'),
                ('BSD', 'BSD'),
            ],
        },
        {
            'name': 'use_github_actions',
            'type': 'selectone',
            'description': 'Do you want to use Github actions? ',
            'values': [
                ('n', 'No'),
                ('y', 'Yes'),
            ],
        },
    ]
    answers = dialogus(
        questions,
        title='Reports Project Configuration',
        confirm='Create',
    )
    if not answers:
        raise ClickException('Aborted by user input')

    return answers


def add_report_questions():
    questions = [
        {
            'name': 'initial_report_name',
            'type': 'input',
            'message': 'Report name: ',
            'default': 'My Awesome Report',
            'validators': (RequiredValidator(message='Please, provide a report name.'),),
        },
        {
            'name': 'initial_report_description',
            'type': 'input',
            'message': 'Report description: ',
            'default': 'This report provides all data I need',
            'validators': (RequiredValidator(message='Please, provide a description.'),),
        },
        {
            'name': 'initial_report_renderer',
            'type': 'selectone',
            'description': 'Report renderer: ',
            'values': [
                ('xlsx', 'xlsx'),
                ('csv', 'csv'),
                ('pdf', 'pdf'),
                ('json', 'json'),
                ('jinja2', 'jinja2'),
            ],
        },
        {
            'name': 'author',
            'type': 'input',
            'message': 'Reports project author: ',
            'default': 'Globex Corporation',
            'validators': (RequiredValidator(message='Please, provide an author name.'),),
        },
    ]
    answers = dialogus(
        questions,
        title='Report Configuration',
        confirm='Create',
    )
    if not answers:
        raise ClickException('Aborted by user input')

    return answers

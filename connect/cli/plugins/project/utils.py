import json
import os
import shutil
from urllib.parse import urlparse

from click.exceptions import ClickException
from cookiecutter.config import DEFAULT_CONFIG
from cookiecutter.utils import rmtree
from interrogatio import dialogus
from interrogatio.validators.builtins import RequiredValidator

STATUSES = [
    'draft',
    'tiers_setup',
    'pending',
    'inquiring',
    'approved',
    'failed',
]


def purge_cookiecutters_dir():
    # Avoid asking rewrite clone boilerplate project
    cookie_dir = DEFAULT_CONFIG['cookiecutters_dir']
    if os.path.isdir(cookie_dir):
        rmtree(cookie_dir)


def general_questions(config, idx, total):
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


def tier_config_capabilities(config, idx, total):
    questions = [
        {
            'name': 'tierconfig',
            'type': 'selectmany',
            'description': 'Tier configuration capabilities',
            'values': [
                ('tier_config_process_capabilities_1of2', 'Setup Request Processing'),
                ('tier_config_process_capabilities_2of2', 'Change Request Processing'),
                ('tier_config_validation_capabilities_1of2', 'Setup Request Validation'),
                ('tier_config_validation_capabilities_1of2', 'Change Request Validation'),
            ],
        },
    ]
    answers = _show_dialog(questions, idx, total)
    return _gen_cookie_capabilities(answers['tierconfig'])


def product_capabilities(config, idx, total):
    questions = [
        {
            'name': 'product',
            'type': 'selectmany',
            'description': 'Product capabilities',
            'values': [
                ('product_capabilities_1of2', 'Product Action Execution'),
                ('product_capabilities_2of2', 'Product Custom Event'),
            ],
        },
    ]
    answers = _show_dialog(questions, idx, total)
    return _gen_cookie_capabilities(answers['product'])


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


def _gen_cookie_capabilities(answers):
    cookicutter_answers = {}
    if answers:
        for capability in answers:
            cookicutter_answers[capability] = 'y'

    return cookicutter_answers


def pre_gen_cookiecutter_hook(answers: dict):
    pr_slug = _slugify(answers['project_name'])
    if hasattr(pr_slug, 'isidentifier') and not pr_slug.isidentifier():
        raise ClickException(f'{pr_slug} project slug is not a valid Python identifier.')

    pk_slug = _slugify(answers['package_name'])
    if hasattr(pk_slug, 'isidentifier') and not pk_slug.isidentifier():
        raise ClickException(f'{pk_slug} package slug is not a valid Python identifier.')


def post_gen_cookiecutter_hook(answers: dict):
    if answers['license'] == 'Other, not Open-source':
        _remove_license()
    if answers['use_github_actions'].lower() == 'n':
        _remove_github_actions()

    pr_slug = _slugify(answers['project_name'])
    pk_slug = _slugify(answers['package_name'])
    descriptor = json.load(open(f'{pr_slug}/{pk_slug}/extension.json'))

    _json_subscription_process_capabilities(descriptor, answers)
    _json_subscription_validation_capabilities(descriptor, answers)
    _json_tierconfig_capabilities(descriptor, answers)
    _json_product_capabilities(descriptor, answers)

    json.dump(descriptor, open(f'{pr_slug}/{pk_slug}/extension.json', 'w'), indent=2)
    print('Done! Your extension project is ready to go!')


def _slugify(name):
    return name.lower().strip().replace(' ', '_').replace('-', '_').replace('.', '_').replace(',', '')


def _remove_license():
    os.remove('LICENSE')


def _remove_github_actions():
    shutil.rmtree('.github')


def _json_subscription_process_capabilities(descriptor: dict, answers: dict):
    if (
        'subscription_process_capabilities_1of6' in answers.keys()
        and answers['subscription_process_capabilities_1of6'].lower() == 'y'
    ):
        descriptor['capabilities']['asset_purchase_request_processing'] = STATUSES
    if (
        'subscription_process_capabilities_2of6' in answers.keys()
        and answers['subscription_process_capabilities_2of6'].lower() == 'y'
    ):
        descriptor['capabilities']['asset_change_request_processing'] = STATUSES
    if (
        'subscription_process_capabilities_3of6' in answers.keys()
        and answers['subscription_process_capabilities_3of6'].lower() == 'y'
    ):
        descriptor['capabilities']['asset_suspend_request_processing'] = STATUSES
    if (
        'subscription_process_capabilities_4of6' in answers.keys()
        and answers['subscription_process_capabilities_4of6'].lower() == 'y'
    ):
        descriptor['capabilities']['asset_resume_request_processing'] = STATUSES
    if (
        'subscription_process_capabilities_5of6' in answers.keys()
        and answers['subscription_process_capabilities_5of6'].lower() == 'y'
    ):
        descriptor['capabilities']['asset_cancel_request_processing'] = STATUSES
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


def _json_tierconfig_capabilities(descriptor: dict, answers: dict):
    # Processing
    if (
        'tier_config_process_capabilities_1of2' in answers.keys()
        and answers['tier_config_process_capabilities_1of2'].lower() == 'y'
    ):
        descriptor['capabilities']['tier_config_setup_request_processing'] = STATUSES
    if (
        'tier_config_process_capabilities_2of2' in answers.keys()
        and answers['tier_config_process_capabilities_2of2'].lower() == 'y'
    ):
        descriptor['capabilities']['tier_config_change_request_processing'] = STATUSES

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


def _json_product_capabilities(descriptor: dict, answers: dict):
    if (
        'product_capabilities_1of2' in answers.keys()
        and answers['product_capabilities_1of2'].lower() == 'y'
    ):
        descriptor['capabilities']['product_action_execution'] = []
    if (
        'product_capabilities_2of2' in answers.keys()
        and answers['product_capabilities_2of2'].lower() == 'y'
    ):
        descriptor['capabilities']['product_custom_event_processing'] = []


def _run_hook_from_repo_dir(
    repo_dir, hook_name, project_dir, context, delete_project_on_failure,
):
    '''Fake method for monkey patching purposes'''
    pass

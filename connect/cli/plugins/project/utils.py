import os

from click.exceptions import ClickException
from cookiecutter.config import DEFAULT_CONFIG
from cookiecutter.utils import rmtree
from interrogatio import dialogus
from interrogatio.validators.builtins import RequiredValidator


def _purge_cookiecutters_dir():
    # Avoid asking rewrite clone boilerplate project
    cookie_dir = DEFAULT_CONFIG['cookiecutters_dir']
    if os.path.isdir(cookie_dir):
        rmtree(cookie_dir)


def _general_questions(idx, total):
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


def _asset_process_capabilities(idx, total):
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


def _asset_validation_capabilities(idx, total):
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


def _tier_config_capabilities(idx, total):
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


def _product_capabilities(idx, total):
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
    answers = dialogus(
        questions,
        title=f'Extension Project Configuration ({idx}/{total})',
        confirm='Next',
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

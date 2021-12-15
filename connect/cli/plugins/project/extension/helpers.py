import inspect
import json
import os

import click
import pkg_resources
import requests
import toml
import yaml
from click.exceptions import ClickException
from cmr import render
from cookiecutter.exceptions import OutputDirExistsException, RepositoryCloneFailed
from cookiecutter.main import cookiecutter
from interrogatio.core.dialog import dialogus

from connect.cli.plugins.project.extension.constants import (
    CAPABILITY_ALLOWED_STATUSES,
    CAPABILITY_METHOD_MAP,
    CHUNK_FILE_STATUSES,
    LISTING_REQUEST_STATUSES,
    PROJECT_EXTENSION_BOILERPLATE_TAG,
    PROJECT_EXTENSION_BOILERPLATE_URL,
    PYPI_EXTENSION_RUNNER_URL,
    REQUESTS_SCHEDULED_ACTION_STATUSES,
    TIER_ACCOUNT_UPDATE_STATUSES,
    USAGE_FILE_STATUSES,
)
from connect.cli.plugins.project.git import get_highest_version, GitException
from connect.cli.plugins.project.cookiehelpers import purge_cookiecutters_dir
from connect.cli.plugins.project.extension.wizard import (
    EXTENSION_BOOTSTRAP_WIZARD_INTRO,
    get_questions,
    get_summary,
)


def bootstrap_extension_project(config, data_dir: str):
    click.secho('Bootstraping extension project...\n', fg='blue')

    purge_cookiecutters_dir()

    answers = dialogus(
        get_questions(config),
        'Extension project bootstrap',
        intro=EXTENSION_BOOTSTRAP_WIZARD_INTRO,
        summary=get_summary(config),
        finish_text='Create',
        previous_text='Back',
    )

    if not answers:
        raise ClickException('Aborted by user input')

    cookiecutter_ctx = {}

    for input_field in (
        'asset_processing', 'asset_validation',
        'tierconfig_validation', 'tierconfig',
        'listing_request',
    ):
        if input_field in answers:
            cookiecutter_ctx.update(
                {v: 'y' for v in answers[input_field]},
            )

    cookiecutter_ctx.update(answers)

    try:
        checkout_tag, _ = PROJECT_EXTENSION_BOILERPLATE_TAG or get_highest_version(PROJECT_EXTENSION_BOILERPLATE_URL)

        project_dir = cookiecutter(
            PROJECT_EXTENSION_BOILERPLATE_URL,
            checkout=checkout_tag,
            no_input=True,
            extra_context=cookiecutter_ctx,
            output_dir=data_dir,
        )
        click.secho(f'\nExtension Project location: {project_dir}\n', fg='blue')
        click.echo(render(open(f'{project_dir}/HOWTO.md', 'r').read()))
    except GitException as error:
        raise ClickException(f'\nAn error occured on tags retrieval: {error}')
    except RepositoryCloneFailed as error:
        raise ClickException(f'\nAn error occured while cloning the project: {error}')
    except OutputDirExistsException as error:
        project_path = str(error).split('"')[1]
        raise ClickException(
            f'\nThe directory "{project_path}" already exists, '
            '\nif you would like to use that name, please delete '
            'the directory or use another location.',
        )


def validate_extension_project(project_dir: str):
    click.secho(f'Validating project {project_dir}...\n', fg='blue')
    extension_dict = _project_descriptor_validations(project_dir)
    _entrypoint_validations(project_dir, extension_dict)

    _runner_version_validation(project_dir)

    click.secho(f'Extension Project {project_dir} has been successfully validated.', fg='green')


def _runner_version_validation(project_dir):
    latest_version = _get_pypi_runner_version()
    docker_compose_file = os.path.join(project_dir, 'docker-compose.yml')
    if not os.path.isfile(docker_compose_file):
        raise ClickException(
            f'Mandatory `docker-compose.yml` file on directory `{project_dir}` is missing.\n'
            'Please, consider recovering it.',
        )
    try:
        with open(docker_compose_file, 'r') as fp:
            data = yaml.load(fp, Loader=yaml.FullLoader)
    except yaml.YAMLError as error:
        raise ClickException(
            '`docker_compose.yml` file is not properly formatted. Please review it.\n'
            f'Error: {error}',
        )
    older_image_list = []
    for service in data['services']:
        if 'image' in data['services'][service]:
            runner_image = data['services'][service]['image']
            runner_version = runner_image.split(':')[-1]
            if runner_version != latest_version:
                older_image_list.append(runner_image)
    if older_image_list:
        image_string_list = ', '.join(older_image_list)
        raise ClickException(
            'The extension runner used currently on `docker-compose.yml` file is not the latest one. '
            'Please, consider updating it.\n'
            f'Latest extension-runner version: {latest_version}\n'
            f'Images not updated: {image_string_list}',
        )


def _project_descriptor_validations(project_dir):
    descriptor_file = os.path.join(project_dir, 'pyproject.toml')
    if not os.path.isfile(descriptor_file):
        raise ClickException(
            f'The directory `{project_dir}` does not look like an extension project directory, '
            'the mandatory `pyproject.toml` project descriptor file is not present.',
        )
    try:
        data = toml.load(descriptor_file)
    except toml.TomlDecodeError:
        raise ClickException(
            'The extension project descriptor file `pyproject.toml` is not valid.',
        )

    extension_dict = data['tool']['poetry']['plugins']['connect.eaas.ext']
    if not isinstance(extension_dict, dict):
        raise ClickException(
            'The extension definition on [tool.poetry.plugins."connect.eaas.ext"] `pyproject.toml` section '
            'is not well configured. It should be as following: "extension" = "your_package.extension:YourExtension"',
        )
    if 'extension' not in extension_dict.keys():
        raise ClickException(
            'The extension definition on [tool.poetry.plugins."connect.eaas.ext"] `pyproject.toml` section '
            'does not have "extension" defined. Reminder: "extension" = "your_package.extension:YourExtension"',
        )
    return extension_dict


def _check_variables(variables):
    names = list(map(lambda x: x['name'], variables))
    unique_names = list(set(map(lambda x: x['name'], variables)))
    if names != unique_names:
        raise ClickException(
            'There are duplicated values in "name" property in multiple entries in '
            '"variables" list in your extension.json. Please correct it, all variables '
            'names must be unique.',
        )


def _check_schedulables(schedulables, extension_class):
    invalid_no_keys = list(filter(
        lambda x: set({'method', 'name', 'description'}) != set(x.keys()),
        schedulables,
    ))
    if invalid_no_keys:
        raise ClickException(
            f'There are schedulable definitions with missing keys: {invalid_no_keys}. '
            'All definitions must have "method", "name" and "description" properties set '
            'and not empty.',
        )

    for schedulable in schedulables:
        empty_values = list(filter(lambda x: not x, list(schedulable.values())))
        if empty_values:
            raise ClickException(
                f'Schedulable definition {schedulable} contains empty values. All '
                'values must be filled in.',
            )

    methods = list(map(lambda x: x['method'], schedulables))
    unique_methods = list(set(map(lambda x: x['method'], schedulables)))
    if methods != unique_methods:
        raise ClickException(
            'There are duplicated values in "method" property in multiple entries in '
            '"schedulables" list in your extension.json. Please correct it, all schedulable '
            'methods must be unique.',
        )

    for method_name in unique_methods:
        if not hasattr(extension_class, method_name):
            raise ClickException(
                f'The schedulable method {method_name} is not defined in the extension class',
            )


def _entrypoint_validations(project_dir, extension_dict):
    package_name = extension_dict['extension'].rsplit('.', 1)[0]
    descriptor_file = os.path.join(f'{project_dir}/{package_name}', 'extension.json')
    if sum(1 for _ in pkg_resources.iter_entry_points('connect.eaas.ext', 'extension')) > 1:
        raise ClickException('\nOnly one extension can be loaded at a time!!!')

    ext_class = next(pkg_resources.iter_entry_points('connect.eaas.ext', 'extension'), None)
    if not ext_class:
        raise ClickException('\nThe extension could not be loaded, Did you execute `poetry install`?')

    CustomExtension = ext_class.load()
    if not inspect.isclass(CustomExtension):
        raise ClickException(f'\nThe extension class {CustomExtension} does not seem a class, please check it')

    all_methods = CustomExtension.__dict__
    methods = [method for method in all_methods.keys() if method in CAPABILITY_METHOD_MAP.values()]

    try:
        ext_descriptor = json.load(open(descriptor_file, 'r'))
    except json.JSONDecodeError:
        raise ClickException(
            '\nThe extension descriptor file `extension.json` could not be loaded.',
        )

    if 'schedulables' in ext_descriptor.keys() and len(ext_descriptor['schedulables']):
        _check_schedulables(ext_descriptor['schedulables'], CustomExtension)

    if 'variables' in ext_descriptor.keys() and len(ext_descriptor['variables']):
        _check_variables(ext_descriptor['variables'])

    capabilities = ext_descriptor['capabilities']

    errors = _have_capabilities_proper_stats(capabilities)
    if errors:
        raise ClickException(f'Capability errors: {errors}')

    errors = _have_methods_proper_capabilities(methods, capabilities)
    if errors:
        raise ClickException(f'Capability-Method errors: {errors}')

    _have_methods_proper_type(CustomExtension, capabilities)


def _have_methods_proper_type(cls, capabilities):
    guess_async = [
        inspect.iscoroutinefunction(getattr(cls, CAPABILITY_METHOD_MAP.get(name)))
        for name in capabilities.keys()
    ]
    if all(guess_async):
        return
    if not any(guess_async):
        return

    raise ClickException('An Extension class can only have sync or async methods not a mix of both.')


def _have_capabilities_proper_stats(capabilities):
    errors = []
    for capability, stats in capabilities.items():
        if capability == 'product_action_execution' or capability == 'product_custom_event_processing':
            if isinstance(stats, list) and len(stats) != 0:
                errors.append(f'Capability `{capability}` must not have status.')
            continue
        if not stats:
            errors.append(f'Capability `{capability}` must have at least one allowed status.')
        for stat in stats:
            errors = _check_statuses(capability, stat, errors)

    return errors


def _check_statuses(capability, stat, errors):
    capabilities_statuses_map = {
        'asset_purchase_request_processing': (
            CAPABILITY_ALLOWED_STATUSES + REQUESTS_SCHEDULED_ACTION_STATUSES),
        'asset_change_request_processing': (
            CAPABILITY_ALLOWED_STATUSES + REQUESTS_SCHEDULED_ACTION_STATUSES),
        'asset_suspend_request_processing': (
            CAPABILITY_ALLOWED_STATUSES + REQUESTS_SCHEDULED_ACTION_STATUSES),
        'asset_resume_request_processing': (
            CAPABILITY_ALLOWED_STATUSES + REQUESTS_SCHEDULED_ACTION_STATUSES),
        'asset_cancel_request_processing': (
            CAPABILITY_ALLOWED_STATUSES + REQUESTS_SCHEDULED_ACTION_STATUSES),
        'listing_new_request_processing': LISTING_REQUEST_STATUSES,
        'listing_remove_request_processing': LISTING_REQUEST_STATUSES,
        'tier_account_update_request_processing': TIER_ACCOUNT_UPDATE_STATUSES,
        'part_usage_file_request_processing': CHUNK_FILE_STATUSES,
        'usage_file_request_processing': USAGE_FILE_STATUSES,
    }

    if capability in capabilities_statuses_map.keys():
        if stat not in capabilities_statuses_map[capability]:
            errors.append(f'Status `{stat}` on capability `{capability}` is not allowed.')
    else:
        if stat not in CAPABILITY_ALLOWED_STATUSES:
            errors.append(f'Status `{stat}` on capability `{capability}` is not allowed.')

    return errors


def _have_methods_proper_capabilities(methods, capabilities):
    errors = []
    for capability in capabilities.keys():
        if CAPABILITY_METHOD_MAP.get(capability) not in methods:
            errors.append(
                f'Capability ´{capability}´ does not have '
                f'corresponding ´{CAPABILITY_METHOD_MAP.get(capability)}´ method',
            )
    return errors


def bump_runner_extension_project(project_dir: str):
    click.secho(f'Bumping runner version on project {project_dir}...\n', fg='blue')

    latest_version = _get_pypi_runner_version()
    docker_compose_file = os.path.join(project_dir, 'docker-compose.yml')
    if not os.path.isfile(docker_compose_file):
        raise ClickException(f'Mandatory `docker-compose.yml` file on directory `{project_dir}` is missing.')
    try:
        with open(docker_compose_file, 'r') as file_reader:
            data = yaml.load(file_reader, Loader=yaml.FullLoader)
            for service in data['services']:
                if 'image' in data['services'][service]:
                    runner_image = data['services'][service]['image']
                    runner_version = runner_image.split(':')[-1]
                    updated_image = runner_image.replace(runner_version, latest_version)
                    data['services'][service]['image'] = updated_image
        with open(docker_compose_file, 'w') as file_writer:
            yaml.dump(data, file_writer, sort_keys=False)
    except yaml.YAMLError as error:
        raise ClickException(
            '`docker_compose.yml` file is not properly formatted. Please review it.\n'
            f'Error: {error}',
        )

    click.secho(f'Runner version has been successfully updated to {latest_version}', fg='green')


def _get_pypi_runner_version():
    res = requests.get(PYPI_EXTENSION_RUNNER_URL)
    if res.status_code != 200:
        raise ClickException(
            f'We can not retrieve the current connect-extension-runner version from {PYPI_EXTENSION_RUNNER_URL}.\n'
            'Please check manually if the version on `docker-compose.yml` file is the same than the lastest on PYPI.',
        )
    content = res.json()
    if not isinstance(content, dict):
        raise ClickException(
            f'The content retrieved from {PYPI_EXTENSION_RUNNER_URL} is not valid.\n'
            'Please check it later or consider doing manually.',
        )
    return content['info']['version']

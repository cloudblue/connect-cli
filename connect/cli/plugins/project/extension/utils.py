import os
import subprocess
from pathlib import Path

import requests
from click import ClickException

from connect.cli import get_version
from connect.cli.core.utils import sort_and_filter_tags
from connect.cli.plugins.project.extension.constants import PRE_COMMIT_HOOK, PYPI_EXTENSION_RUNNER_URL
from connect.client import ClientError


def get_event_definitions(config):
    try:
        return list(config.active.client('devops').event_definitions.all())
    except ClientError as err:
        raise ClickException(f"Error getting event definitions: {str(err)}")


def get_pypi_runner_version():
    res = requests.get(PYPI_EXTENSION_RUNNER_URL)
    if res.status_code != 200:
        raise ClickException(
            f'We can not retrieve the current connect-extension-runner version from {PYPI_EXTENSION_RUNNER_URL}.',
        )
    content = res.json()
    tags = sort_and_filter_tags(content['releases'], get_version().split('.', 1)[0])
    if tags:
        return tags.popitem()[0]
    return content['info']['version']


def get_extension_types(config):
    if config.active.is_provider():
        extension_types = [('hub', 'Hub integration')]
    else:
        extension_types = [('products', 'Fulfillment Automation')]

    extension_types.append(('multiaccount', 'Multi-Account installation'))
    return extension_types


def get_background_events(definitions, context):
    return [
        (event['type'], f'{event["group"]}: {event["name"]}')
        for event in definitions[context['extension_type']]['background']
    ]


def get_interactive_events(definitions, context):
    return [
        (event['type'], f'{event["group"]}: {event["name"]}')
        for event in definitions[context['extension_type']]['interactive']
    ]


def check_extension_not_multi_account(context):
    return context.get('extension_type') != 'multiaccount'


def check_extension_events_applicable(context):
    if context.get('extension_type') != 'multiaccount':
        return False

    return 'events' not in context.get('application_types', [])


def check_extension_interactive_events_applicable(definitions, context):
    if context.get('extension_type') == 'multiaccount':
        if not definitions[context['extension_type']].get('interactive'):
            return True

    return False


def check_webapp_feature_not_selected(context):
    return 'webapp' not in context.get('application_types', [])


def check_eventsapp_feature_not_selected(context):
    return 'events' not in context.get('application_types', [])


def initialize_git_repository(tmp_dir, context):
    project_dir = os.path.join(tmp_dir, context['project_slug'])
    hooks_dir = os.path.join(project_dir, '.git', 'hooks')
    subprocess.run(
        ['git', 'init', project_dir],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for sample in Path(hooks_dir).glob('*.sample'):
        sample.unlink()

    if context.get('webapp_supports_ui') == 'y':
        pre_commit_file = Path(os.path.join(hooks_dir, 'pre-commit'))
        with open(pre_commit_file, 'w') as f:
            f.write(
                PRE_COMMIT_HOOK.format(
                    project_slug=context['project_slug'],
                    package_name=context['package_name'],
                ),
            )

        pre_commit_file.chmod(0o755)

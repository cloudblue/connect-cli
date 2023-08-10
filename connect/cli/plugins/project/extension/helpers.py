import collections
import json
import os

import yaml
from click.exceptions import ClickException
from connect.eaas.core.deployment.extension import deploy_extension
from connect.eaas.core.validation.validators import get_validators
from interrogatio.core.dialog import dialogus

from connect.cli import get_version
from connect.cli.core.terminal import console
from connect.cli.plugins.project.extension.utils import (
    get_event_definitions,
    get_pypi_runner_version,
    get_pypi_runner_version_by_connect_version,
    initialize_git_repository,
)
from connect.cli.plugins.project.extension.wizard import (
    EXTENSION_BOOTSTRAP_WIZARD_INTRO,
    get_questions,
    get_summary,
)
from connect.cli.plugins.project.renderer import BoilerplateRenderer
from connect.cli.plugins.project.utils import show_validation_result_table
from connect.cli.plugins.project.validators import ProjectDirValidator


def bootstrap_extension_project(  # noqa: CCR001
    config,
    output_dir,
    overwrite,
    save_answers,
    load_answers,
):
    console.secho('Bootstraping extension project...\n', fg='blue')

    if save_answers and os.path.exists(save_answers):
        raise ClickException(f'Answers cannot be saved, because {save_answers} already exists.')

    statuses_by_event = collections.defaultdict(lambda: collections.defaultdict())

    definitions = get_event_definitions(config)
    grouped_definitions = collections.defaultdict(lambda: collections.defaultdict(list))

    for elem in definitions:
        statuses_by_event[elem['extension_type']][elem['type']] = elem['object_statuses']
        grouped_definitions[elem['extension_type']][elem['category']].append(elem)

    questions = get_questions(config, grouped_definitions)

    if load_answers:
        try:
            with open(load_answers) as fp:
                loaded_answers = json.load(fp)

            for question in questions:
                if question['name'] in loaded_answers:
                    question['default'] = loaded_answers[question['name']]
        except Exception as e:
            raise ClickException(f'Can not load or parse answers from {load_answers}: {e}')

    if not overwrite:
        for q in questions:
            if q['name'] == 'project_slug':
                q['validators'].append(ProjectDirValidator(output_dir))
                break

    answers = dialogus(
        questions,
        'Extension project bootstrap',
        intro=EXTENSION_BOOTSTRAP_WIZARD_INTRO,
        summary=get_summary,
        fast_forward=load_answers is not None,
        finish_text='Create',
        previous_text='Back',
    )

    if not answers:
        raise ClickException('Aborted by user input')

    ctx = {
        'statuses_by_event': statuses_by_event[answers['extension_type']],
        'interactive': [],
        'current_major_version': get_version().split('.')[0],
        'runner_version': get_pypi_runner_version(),
    }

    for var, answer in answers.items():
        ctx.update({var: answer})

    project_dir = os.path.join(output_dir, ctx['project_slug'])
    if not overwrite and os.path.exists(project_dir):
        raise ClickException(f'The destination directory {project_dir} already exists.')

    if save_answers:
        with open(save_answers, 'w') as fp:
            json.dump(answers, fp, indent=2)
        console.echo()
        console.secho(f'Answers saved to {save_answers}', fg='green')
        console.echo()

    exclude = []

    if answers['use_github_actions'] == 'n':
        exclude.extend(['.github', '.github/**/*'])

    application_types = answers.get('application_types', [])

    if answers.get('webapp_supports_ui') != 'y':
        exclude.extend(
            [
                os.path.join('${package_name}', 'static', '.gitkeep'),
                'ui',
                'ui/**/*',
                'package.json.j2',
                'webpack.config.js.j2',
                '__mocks__',
                '__mocks__/*',
                '.eslintrc.yaml.j2',
                'babel.config.json.j2',
                'jest.config.js.j2',
            ],
        )

    elif 'tfnapp' not in application_types:
        exclude.extend(
            [
                'ui/pages/transformations',
                'ui/pages/transformations/*',
                'ui/src/pages/transformations',
                'ui/src/pages/transformations/*',
                'ui/styles/manual.css.j2',
            ],
        )
    else:
        exclude.extend(
            [
                'ui/pages/index.html.j2',
                'ui/pages/settings.html.j2',
                'ui/src/pages/index.js.j2',
                'ui/src/pages/settings.js.j2',
                'ui/tests/pages.spec.js.j2',
                'ui/tests/utils.spec.js.j2',
            ],
        )

    for app_type in ['anvil', 'events', 'webapp', 'tfnapp']:
        if app_type not in application_types:
            exclude.append(
                os.path.join(
                    '${package_name}',
                    f'{app_type}.py.j2',
                ),
            )
            exclude.append(
                os.path.join(
                    'tests',
                    f'test_{app_type}.py.j2',
                ),
            )
    if 'webapp' not in application_types:
        exclude.append('${package_name}/schemas.py.j2')

    renderer = BoilerplateRenderer(
        context=ctx,
        template_folder=os.path.join(
            os.path.dirname(__file__),
            'templates',
            'bootstrap',
        ),
        output_dir=output_dir,
        overwrite=overwrite,
        exclude=exclude,
        post_render=initialize_git_repository,
    )
    renderer.render()
    console.markdown(open(f'{project_dir}/HOWTO.md', 'r').read())


def validate_extension_project(config, project_dir):  # noqa: CCR001
    console.secho(f'Validating project {project_dir}...\n', fg='blue')

    event_definitions = {
        definition['type']: definition
        for definition in config.active.client('devops').event_definitions.all()
    }

    context = {
        'runner_version': get_pypi_runner_version(),
        'project_dir': project_dir,
        'event_definitions': event_definitions,
    }

    validation_items = []

    for validator in get_validators():
        result = validator(context)
        validation_items.extend(result.items)
        if result.must_exit:
            break
        if result.context:
            context.update(result.context)

    if validation_items:
        console.markdown('# Extension validation results')
        show_validation_result_table(validation_items)
        console.secho(
            f'Warning/errors have been found while validating the Extension Project {project_dir}.',
            fg='yellow',
        )
    else:
        console.secho(
            f'Extension Project {project_dir} has been successfully validated.',
            fg='green',
        )


def _update_docker_file_runner_from(dockerfile: str, latest_version: str):
    to_be_replaced = False
    last_runner = f'cloudblueconnect/connect-extension-runner:{latest_version}'
    lines = []
    with open(dockerfile, 'r') as f:
        for line in f.readlines():
            content = line.split()
            if (
                content
                and content[0] == 'FROM'
                and content[1].startswith(
                    'cloudblueconnect/connect-extension-runner:',
                )
                and content[1].strip() != last_runner
            ):
                lines.append(line.replace(content[1], last_runner))
                to_be_replaced = True
            else:
                lines.append(line)
    if to_be_replaced:
        with open(dockerfile, 'w') as f:
            f.writelines(lines)
    return to_be_replaced


def bump_runner_extension_project(project_dir: str):  # noqa: CCR001
    console.secho(f'Bumping runner version on project {project_dir}...\n', fg='blue')

    updated_files = set()
    latest_version = get_pypi_runner_version_by_connect_version()
    latest_runner_version = f'cloudblueconnect/connect-extension-runner:{latest_version}'
    docker_compose_file = os.path.join(project_dir, 'docker-compose.yml')
    if not os.path.isfile(docker_compose_file):
        raise ClickException(
            f'Mandatory `docker-compose.yml` file on directory `{project_dir}` is missing.',
        )
    try:
        with open(docker_compose_file, 'r') as file_reader:
            data = yaml.load(file_reader, Loader=yaml.FullLoader)
            for service in data['services']:
                if (
                    'image' in data['services'][service]
                    and data['services'][service]['image'].startswith(
                        'cloudblueconnect/connect-extension-runner:',
                    )
                    and data['services'][service]['image'] != latest_runner_version
                ):
                    runner_image = data['services'][service]['image']
                    runner_version = runner_image.split(':')[-1]
                    updated_image = runner_image.replace(runner_version, latest_version)
                    data['services'][service]['image'] = updated_image
                    updated_files.add(docker_compose_file)
                elif 'build' in data['services'][service]:
                    dockerfile = data['services'][service]['build'].get('dockerfile', 'Dockerfile')
                    dockerfile_path = os.path.join(project_dir, dockerfile)
                    if not os.path.isfile(dockerfile_path):
                        raise ClickException(
                            f'The expected dockerfile `{dockerfile_path}` specified in '
                            f'{docker_compose_file} is missing.',
                        )
                    if dockerfile_path not in updated_files and _update_docker_file_runner_from(
                        dockerfile_path,
                        latest_version,
                    ):
                        updated_files.add(dockerfile_path)
        with open(docker_compose_file, 'w') as file_writer:
            yaml.dump(data, file_writer, sort_keys=False)
    except yaml.YAMLError as error:
        raise ClickException(
            '`docker_compose.yml` file is not properly formatted. Please review it.\n'
            f'Error: {error}',
        )

    if updated_files:
        console.secho(
            f'Runner version has been successfully updated to {latest_version}. The following '
            f'files have been updated:\n{",".join(updated_files)}',
            fg='green',
        )
    else:
        console.secho(f'Nothing to update to {latest_version}', fg='yellow')


def deploy_extension_project(config, repo_url, tag):
    deploy_extension(
        repo=repo_url,
        client=config.active.client,
        log=console.secho,
        tag=tag,
    )

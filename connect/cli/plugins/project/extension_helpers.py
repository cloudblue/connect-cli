import click
from click.exceptions import ClickException
from cookiecutter.exceptions import OutputDirExistsException
from cookiecutter.main import cookiecutter

from connect.cli.plugins.project.constants import PROJECT_EXTENSION_BOILERPLATE_URL
from connect.cli.plugins.project import utils


def bootstrap_extension_project(data_dir: str):
    click.secho('Bootstraping extension project...\n', fg='blue')

    utils._purge_cookiecutters_dir()

    index = 1
    answers = {}
    function_list = [
        '_general_questions',
        '_asset_process_capabilities',
        '_asset_validation_capabilities',
        '_tier_config_capabilities',
        '_product_capabilities',
    ]
    for question_function in function_list:
        partial = getattr(utils, question_function)(index, len(function_list))
        index += 1
        answers.update(partial)

    try:
        project_dir = cookiecutter(
            PROJECT_EXTENSION_BOILERPLATE_URL,
            no_input=True,
            extra_context=answers,
            output_dir=data_dir,
        )
        click.secho(f'\nExtension Project location: {project_dir}', fg='blue')
    except OutputDirExistsException as error:
        project_path = str(error).split('"')[1]
        raise ClickException(
            f'\nThe directory "{project_path}" already exists, '
            '\nif you would like to use that name, please delete '
            'the directory or use another location.',
        )

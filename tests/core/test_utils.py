import re
import os.path

import pytest
from click import ClickException

from connect.cli.core import utils
from connect.cli.core.constants import PYPI_JSON_API_URL


def test_continue_or_quit_c(mocker):
    mocker.patch('connect.cli.core.utils.click.echo')
    mocker.patch('connect.cli.core.utils.click.getchar', return_value='c')
    assert utils.continue_or_quit() is True


def test_continue_or_quit_q(mocker):
    mocker.patch('connect.cli.core.utils.click.echo')
    mocker.patch('connect.cli.core.utils.click.getchar', return_value='q')
    assert utils.continue_or_quit() is False


def test_continue_or_quit_invalid_plus_q(mocker):
    mocker.patch('connect.cli.core.utils.click.echo')
    mocker.patch('connect.cli.core.utils.click.getchar', side_effect=['z', 'q'])
    assert utils.continue_or_quit() is False


def test_check_for_updates_ok(mocker, capsys, mocked_responses):
    mocker.patch('connect.cli.core.utils.get_version', return_value='1.0.0')
    mocked_responses.add('GET', PYPI_JSON_API_URL, json={'info': {'version': '2.0.0'}})

    utils.check_for_updates()

    captured = capsys.readouterr()

    assert 'You are running CloudBlue Connect CLI version 1.0.0. ' in captured.out
    assert 'A newer version is available: 2.0.0' in captured.out


def test_check_for_updates_is_latest(mocker, capsys, mocked_responses):
    mocker.patch('connect.cli.core.utils.get_version', return_value='2.0.0')
    mocked_responses.add('GET', PYPI_JSON_API_URL, json={'info': {'version': '2.0.0'}})

    utils.check_for_updates()

    captured = capsys.readouterr()

    assert 'You are running CloudBlue Connect CLI version 1.0.0. ' not in captured.out
    assert 'A newer version is available: 2.0.0' not in captured.out


def test_validate_output_options(fs):
    fs.makedirs('custom/path')

    output_file = utils.validate_output_options(
        output_path=os.path.join(fs.root_path, 'custom/path'),
        output_file='custom_filename.xlsx',
        default_dir_name='XX-000-000',
        default_file_name='data.xlsx',
    )

    assert output_file.endswith('custom/path/XX-000-000/custom_filename.xlsx')


def test_validate_output_options_output_path_does_not_exist(fs):
    with pytest.raises(ClickException) as e:
        utils.validate_output_options(
            output_path=os.path.join(fs.root_path, 'custom/inexistent/path'),
            output_file=None,
            default_dir_name='XX-000-000',
        )

    assert 'Output Path does not exist' in str(e)


def test_validate_output_options_output_path_is_file(fs):
    fs.makedirs('custom/path')
    fs.create('custom/path/XX-000-000')

    with pytest.raises(ClickException) as e:
        utils.validate_output_options(
            output_path=os.path.join(fs.root_path, 'custom/path'),
            output_file=None,
            default_dir_name='XX-000-000',
        )

    assert (
        "Exists a file with name 'XX-000-000' but a directory is "
        "expected, please rename it" in str(e)
    )


def test_validate_output_options_no_options(fs, mocker):
    fs.makedir('workdir')
    mocker.patch('os.getcwd', return_value=os.path.join(fs.root_path, 'workdir'))

    output_file = utils.validate_output_options(
        output_path=None,
        output_file=None,
        default_dir_name='XX-000-000',
        default_file_name='data',
    )

    assert output_file.endswith('workdir/XX-000-000/data.xlsx')


def test_validate_output_options_no_options_no_default_file_name(fs, mocker):
    fs.makedir('workdir')
    mocker.patch('os.getcwd', return_value=os.path.join(fs.root_path, 'workdir'))

    output_file = utils.validate_output_options(
        output_path=None,
        output_file=None,
        default_dir_name='XX-000-000',
    )

    assert output_file.endswith('workdir/XX-000-000/XX-000-000.xlsx')


def test_validate_output_options_no_output_path(fs, mocker):
    fs.makedir('workdir')
    mocker.patch('os.getcwd', return_value=os.path.join(fs.root_path, 'workdir'))

    output_file = utils.validate_output_options(
        output_path=None,
        output_file='custom_filename.xlsx',
        default_dir_name='XX-000-000',
        default_file_name='data',
    )

    assert output_file.endswith('workdir/XX-000-000/custom_filename.xlsx')


def test_validate_output_options_no_output_file(fs):
    fs.makedirs('custom/path')

    output_file = utils.validate_output_options(
        output_path=os.path.join(fs.root_path, 'custom/path'),
        output_file=None,
        default_dir_name='XX-000-000',
        default_file_name='data',
    )

    assert output_file.endswith('custom/path/XX-000-000/data.xlsx')


def test_field_to_check_mark():
    assert '✓' == utils.field_to_check_mark(True)
    assert '' == utils.field_to_check_mark(False)


def test_field_to_check_mark_with_false_value():
    assert '-' == utils.field_to_check_mark(False, false_value='-')


def test_row_format_resource():
    fields = (
        'ZH-HANS',
        'Simplified Chinese',
        '✓',
        '-',
    )
    separators = len(fields) + 1
    assert '| ZH-HANS | Simplified Chinese | ✓ | - |\n' == utils.row_format_resource(*fields)
    assert separators == len(re.findall(r'\|', utils.row_format_resource(*fields)))


def test_formater_not_echo_with_page_size_greater_than_paging(capsys, mocked_resource_list_table):

    utils.table_formater_resource(
        resource_str_list=mocked_resource_list_table,
        count_of_resources=97,
        paging=1,
        page_size=10,
    )
    captured = capsys.readouterr()
    assert '' == captured.out


def test_formater_with_page_size_less_than_paging_and_modulo_equal_zero(capsys, mocked_resource_list_table):
    utils.table_formater_resource(
        resource_str_list=mocked_resource_list_table,
        count_of_resources=97,
        paging=2,
        page_size=1,
    )
    captured = capsys.readouterr()
    assert '╭─────────╮\n│   ID    │\n├─────────┤\n│ ZH-HANS │\n╰─────────╯\n\n' == captured.out


def test_table_formater_page_size_equeal_paging(capsys, mocked_resource_list_table):

    utils.table_formater_resource(
        resource_str_list=mocked_resource_list_table[:2],
        count_of_resources=97,
        paging=1,
        page_size=1,
    )

    captured = capsys.readouterr()
    assert '╭─────────╮\n│   ID    │\n├─────────┤\n│ ZH-HANS │\n╰─────────╯\n\n' == captured.out

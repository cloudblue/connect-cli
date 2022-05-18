import subprocess

import pytest

from connect.cli.plugins.project import git


def test_list_tags(mocker):
    mock_subprocess_run = mocker.patch('connect.cli.plugins.project.git.subprocess.run')
    mock_subprocess_called_process_error = mocker.patch(
        'connect.cli.plugins.project.git.subprocess.CompletedProcess',
    )
    mock_subprocess_called_process_error.stdout = b"""commit1	refs/tags/21.1
                  commit2	refs/tags/21.10
                  commit3	refs/tags/21.11
                  commit4	refs/tags/21.9"""
    mock_subprocess_run.return_value = mock_subprocess_called_process_error

    tags = git._list_tags('dummy.repo')
    assert tags == {'21.1': 'commit1', '21.10': 'commit2', '21.11': 'commit3', '21.9': 'commit4'}


def test_list_tags_error(mocker):
    mock_subprocess_run = mocker.patch('connect.cli.plugins.project.git.subprocess.run')
    mock_subprocess_called_process = mocker.patch(
        'connect.cli.plugins.project.git.subprocess.CompletedProcess',
    )
    mock_subprocess_called_process.check_returncode.side_effect = subprocess.CalledProcessError(1, [])
    mock_subprocess_run.return_value = mock_subprocess_called_process

    with pytest.raises(git.GitException):
        git._list_tags('dummy.repo')


@pytest.mark.parametrize(
    ('tags', 'cli_version', 'expected'),
    (
        (
            b"""commit1	 refs/tags/v21.1
                commit2	 refs/tags/v21.10
                commit3	 refs/tags/v21.11
                commit4	 refs/tags/v21.9""",
            '21.4',
            ('v21.11', 'commit3'),
        ),
        (
            b"""commit1	 refs/tags/21.1
                commit2	 refs/tags/21.10
                commit3	 refs/tags/21.11
                commit4	 refs/tags/21.9""",
            '21.7',
            ('21.11', 'commit3'),
        ),
        (
            b"""commit4	 refs/tags/22.0
                commit1	 refs/tags/21.3
                commit2	 refs/tags/21.2
                commit3	 refs/tags/21.1""",
            '22.1',
            ('22.0', 'commit4'),
        ),
        (
            b"""commit4	 refs/tags/22.0
                commit1	 refs/tags/21.3
                commit2	 refs/tags/21.2
                commit3	 refs/tags/21.1""",
            '21.1',
            ('21.3', 'commit1'),
        ),
        (
            b"""commit4	 refs/tags/22.0
                commit1	 refs/tags/21.3
                commit2	 refs/tags/21.2""",
            '22.4',
            ('22.0', 'commit4'),
        ),
        (
            b"""commit4	 refs/tags/01.0
                commit1	 refs/tags/0.0""",
            '22.1',
            (None, None),
        ),
        (b"", '21.1', (None, None)),
    ),
)
def test_get_highest_version(mocker, tags, cli_version, expected):
    mock_subprocess_run = mocker.patch('connect.cli.plugins.project.git.subprocess.run')
    mock_subprocess_called_process_error = mocker.patch(
        'connect.cli.plugins.project.git.subprocess.CalledProcessError',
    )
    mock_subprocess_called_process_error.stdout = tags
    mock_subprocess_run.return_value = mock_subprocess_called_process_error
    mocker.patch('connect.cli.plugins.project.git.get_version', return_value=cli_version)
    assert expected == git.get_highest_version('dummy.repo')

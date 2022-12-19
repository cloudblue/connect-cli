import stat

from connect.cli.plugins.project.utils import force_delete, purge_dir


def test_force_delete(mocker):
    mocked_os_chmod = mocker.patch('connect.cli.plugins.project.utils.os.chmod')
    mocked_f = mocker.MagicMock()
    force_delete(mocked_f, 'somepath', None)
    mocked_os_chmod.assert_called_with('somepath', stat.S_IWRITE)
    assert mocked_f.call_count == 1


def test_purge_dir(mocker):
    mocked_os_isdir = mocker.patch('connect.cli.plugins.project.utils.os.path.isdir', return_value=True)
    mocked_shutil_rmtree = mocker.patch('connect.cli.plugins.project.utils.shutil.rmtree')
    mocked_force_delete = mocker.patch('connect.cli.plugins.project.utils.force_delete')
    purge_dir('somepath')
    mocked_os_isdir.assert_called_with('somepath')
    mocked_shutil_rmtree.assert_called_with('somepath', onerror=mocked_force_delete)

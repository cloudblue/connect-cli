import os

import pytest
from click import Abort
from rich import box
from rich.panel import Panel
from rich.progress import Progress
from rich.status import Status as _Status

from connect.cli.core.terminal import Console, Status, get_style


def test_get_style(mocker):
    mocked_style_inst = mocker.MagicMock()
    mocked_style = mocker.patch(
        'connect.cli.core.terminal.Style',
        return_value=mocked_style_inst,
    )

    style = get_style(
        fg='fg',
        bg='bg',
        bold='bold',
        dim='dim',
        underline='underline',
        overline='overline',
        italic='italic',
        blink='blink',
        reverse='reverse',
        strikethrough='strikethrough',
    )

    assert style == mocked_style_inst
    mocked_style.assert_called_once_with(
        color='fg',
        bgcolor='bg',
        bold='bold',
        dim='dim',
        underline='underline',
        overline='overline',
        italic='italic',
        blink='blink',
        reverse='reverse',
        strike='strikethrough',
    )


def test_status_update(mocker):
    mocked_update = mocker.patch.object(_Status, 'update')
    style = mocker.MagicMock()
    mocker.patch(
        'connect.cli.core.terminal.get_style',
        return_value=style,
    )

    status = Status('')

    status.update(
        'status_text',
        fg='blue',
        spinner='spinner',
        spinner_style='spinner_style',
        speed=3,
    )

    assert mocked_update.mock_calls[0].args[0].plain == 'status_text'
    assert mocked_update.mock_calls[0].args[0].style == style
    assert mocked_update.mock_calls[0].kwargs['spinner'] == 'spinner'
    assert mocked_update.mock_calls[0].kwargs['spinner_style'] == 'spinner_style'
    assert mocked_update.mock_calls[0].kwargs['speed'] == 3


def test_console_silent(mocker):
    mocked_file = mocker.MagicMock()
    mocked_open = mocker.patch(
        'connect.cli.core.terminal.open',
        return_value=mocked_file,
    )

    c = Console()
    assert c.silent is False
    assert c._file is None

    c.silent = True
    assert c.silent is True
    assert c._file == mocked_file
    mocked_open.assert_called_once_with(os.devnull, 'w')


def test_console_skip_confirm():
    c = Console()
    assert c.skip_confirm is False

    c.skip_confirm = True
    assert c.skip_confirm is True


def test_console_verbose():
    c = Console()
    assert c.verbose is False

    c.verbose = True
    assert c.verbose is True


def test_console_page_size():
    c = Console()
    assert c.page_size == 25

    c.page_size = 50
    assert c.page_size == 50


@pytest.mark.parametrize('confirm_return', (True, False))
def test_console_confirm(mocker, confirm_return):
    prompt = mocker.MagicMock(return_value=confirm_return)
    mocked_confirm = mocker.patch(
        'connect.cli.core.terminal.Confirm',
        return_value=prompt,
    )
    c = Console()

    assert c.confirm('message') is confirm_return
    mocked_confirm.assert_called_once_with('message', console=c)
    prompt.assert_called_once_with(default=False)


def test_console_confirm_skip_confirm(mocker):
    c = Console()
    c.skip_confirm = True

    assert c.confirm('message') is True


def test_console_confirm_abort(mocker):
    prompt = mocker.MagicMock(return_value=False)
    mocker.patch(
        'connect.cli.core.terminal.Confirm',
        return_value=prompt,
    )
    c = Console()

    with pytest.raises(Abort):
        c.confirm('message', abort=True)


def test_echo(mocker):
    mocked_print = mocker.patch.object(Console, 'print')

    c = Console()
    c.echo('message')
    mocked_print.assert_called_once_with('message')


def test_secho(mocker):
    mocked_print = mocker.patch.object(Console, 'print')
    style = mocker.MagicMock()
    mocker.patch(
        'connect.cli.core.terminal.get_style',
        return_value=style,
    )
    c = Console()
    c.secho('message', fg='blue')
    mocked_print.assert_called_once_with('message', style=style)


def test_markdown(mocker):
    mocked_print = mocker.patch.object(Console, 'print')
    mocked_render = mocker.patch(
        'connect.cli.core.terminal.render',
        return_value='rendered markdown',
    )
    c = Console()
    c.markdown('# my markdown')
    mocked_print.assert_called_once_with('rendered markdown', soft_wrap=True)
    mocked_render.assert_called_once_with('# my markdown')


def test_header(mocker):
    mocked_print = mocker.patch.object(Console, 'print')
    style = mocker.MagicMock()
    mocker.patch(
        'connect.cli.core.terminal.get_style',
        return_value=style,
    )
    c = Console()
    c.header('header text', fg='aa')

    assert isinstance(mocked_print.mock_calls[0].args[0], Panel)
    assert mocked_print.mock_calls[0].args[0].renderable.plain == 'header text'
    assert mocked_print.mock_calls[0].args[0].renderable.justify == 'center'
    assert mocked_print.mock_calls[0].args[0].renderable.style == style
    assert mocked_print.mock_calls[0].args[0].box == box.ROUNDED


def test_console_continue_or_quit_continue(mocker):
    mocked_print = mocker.patch.object(Console, 'print')
    prompt = mocker.MagicMock(return_value=True)
    mocked_confirm = mocker.patch(
        'connect.cli.core.terminal.Confirm',
        return_value=prompt,
    )
    c = Console()

    assert c.continue_or_quit() is None
    mocked_confirm.assert_called_once_with(
        "Press 'c' to continue or 'q' to quit",
        console=c,
        choices=['c', 'q'],
        show_choices=False,
        show_default=True,
    )
    assert mocked_print.call_count == 2


def test_console_continue_or_quit_skip_confirm(mocker):
    mocked_print = mocker.patch.object(Console, 'print')

    c = Console()
    c.skip_confirm = True

    assert c.continue_or_quit() is None
    assert mocked_print.call_count == 0


def test_console_continue_or_quit_quit(mocker):
    mocked_print = mocker.patch.object(Console, 'print')
    prompt = mocker.MagicMock(return_value=False)
    mocker.patch(
        'connect.cli.core.terminal.Confirm',
        return_value=prompt,
    )
    c = Console()
    with pytest.raises(Abort):
        c.continue_or_quit()

    assert mocked_print.call_count == 1


def test_console_status_progress(mocker):
    live = mocker.MagicMock()
    mocker.patch(
        'connect.cli.core.terminal.Live',
        return_value=live,
    )
    c = Console()

    with c.status_progress() as (status, progress):
        assert isinstance(status, Status)
        assert isinstance(progress, Progress)

import os
import contextlib

from click.exceptions import Abort
from rich import box
from rich.console import Console as _Console, Group
from rich.live import Live
from rich.status import Status as _Status
from rich.style import Style
from rich.panel import Panel
from rich.prompt import Confirm
from rich.progress import (
    BarColumn, MofNCompleteColumn, Progress, SpinnerColumn,
    TaskProgressColumn, TextColumn, TimeElapsedColumn,
)
from rich.table import Table
from rich.text import Text

from connect.utils.terminal.markdown import render


def get_style(
    fg=None,
    bg=None,
    bold=None,
    dim=None,
    underline=None,
    overline=None,
    italic=None,
    blink=None,
    reverse=None,
    strikethrough=None,
):
    return Style(
        color=fg,
        bgcolor=bg,
        bold=bold,
        dim=dim,
        underline=underline,
        overline=overline,
        italic=italic,
        blink=blink,
        reverse=reverse,
        strike=strikethrough,
    )


class Status(_Status):
    def update(
        self,
        status,
        *,
        spinner=None,
        spinner_style=None,
        speed=None,
        fg=None,
        bg=None,
        bold=None,
        dim=None,
        underline=None,
        overline=None,
        italic=None,
        blink=None,
        reverse=None,
        strikethrough=None,
    ):
        style = get_style(
            fg=fg,
            bg=bg,
            bold=bold,
            dim=dim,
            underline=underline,
            overline=overline,
            italic=italic,
            blink=blink,
            reverse=reverse,
            strikethrough=strikethrough,
        )
        return super().update(
            Text(status, style=style),
            spinner=spinner,
            spinner_style=spinner_style,
            speed=speed,
        )


class Console(_Console):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._skip_confirm = False
        self._silent = False
        self._verbose = False
        self._page_size = 25

    @property
    def silent(self):
        return self._silent

    @silent.setter
    def silent(self, value):
        self._silent = value
        self._file = open(os.devnull, 'w') if value else None

    @property
    def skip_confirm(self):
        return self._skip_confirm

    @skip_confirm.setter
    def skip_confirm(self, value):
        self._skip_confirm = value

    @property
    def verbose(self):
        return self._verbose

    @verbose.setter
    def verbose(self, value):
        self._verbose = value

    @property
    def page_size(self):
        return self._page_size

    @page_size.setter
    def page_size(self, value):
        self._page_size = value

    def progress(self):
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description:<80}"),
            BarColumn(style='cyan', finished_style='green3'),
            MofNCompleteColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=self,
            expand=True,
        )

    @contextlib.contextmanager
    def status_progress(self):
        status = Status('')
        progress = self.progress()
        with Live(Group(status, progress), console=self):
            yield status, progress

    def confirm(
        self,
        message,
        abort=False,
    ):
        if self._skip_confirm:
            return True

        self.print()
        prompt = Confirm(
            message, console=self,
        )

        result = prompt(default=False)
        if not result and abort:
            raise Abort()

        self.print()
        return result

    def continue_or_quit(self):
        if self._skip_confirm:
            return

        self.print()

        prompt = Confirm(
            "Press 'c' to continue or 'q' to quit",
            console=self,
            choices=['c', 'q'],
            show_choices=False,
            show_default=True,
        )

        if not prompt(default='c'):
            raise Abort()

        self.print()

    def markdown(self, md):
        rendered = render(md)
        for line in rendered.splitlines():
            self.print(line, soft_wrap=True)

    def header(
        self,
        text,
        fg='dodger_blue2',
        bg=None,
        bold=None,
        dim=None,
        underline=None,
        overline=None,
        italic=None,
        blink=None,
        reverse=None,
        strikethrough=None,
    ):
        style = get_style(
            fg=fg,
            bg=bg,
            bold=bold,
            dim=dim,
            underline=underline,
            overline=overline,
            italic=italic,
            blink=blink,
            reverse=reverse,
            strikethrough=strikethrough,
        )
        header = Text(text, justify='center', style=style)
        self.print(
            Panel(
                header,
                box=box.ROUNDED,
            ),
        )

    def table(
        self,
        columns=None,
        rows=None,
        expand=False,
    ):
        if not (columns and rows):
            return

        chunks = [
            rows[i:i + self.page_size]
            for i in range(0, len(rows), self.page_size)
        ] if not self.skip_confirm else [rows]

        for chunk_count, chunk in enumerate(chunks):
            table = Table(
                box=box.ROUNDED,
                border_style='blue',
                header_style='deep_sky_blue1',
                expand=expand,
            )
            for col in columns:
                if isinstance(col, (tuple, list)) and len(col) == 2:
                    justify, header = col
                else:
                    header = col
                    justify = 'left'
                table.add_column(header, justify=justify)

            for row in chunk:
                table.add_row(*[str(item) for item in row])

            self.print(table)
            if chunk_count < len(chunks) - 1:
                self.continue_or_quit()

    def echo(self, message=''):
        self.print(message)

    def secho(
        self,
        message,
        fg=None,
        bg=None,
        bold=None,
        dim=None,
        underline=None,
        overline=None,
        italic=None,
        blink=None,
        reverse=None,
        strikethrough=None,
    ):
        style = get_style(
            fg=fg,
            bg=bg,
            bold=bold,
            dim=dim,
            underline=underline,
            overline=overline,
            italic=italic,
            blink=blink,
            reverse=reverse,
            strikethrough=strikethrough,
        )
        self.print(message, style=style)


console = Console(highlight=False)

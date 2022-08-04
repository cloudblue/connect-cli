import os
import shutil
import stat

from rich import box
from rich.markdown import Markdown
from rich.table import Table
from rich.syntax import Syntax

from connect.cli.core.terminal import console


def force_delete(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def purge_dir(dir):
    if os.path.isdir(dir):
        shutil.rmtree(dir, onerror=force_delete)


def slugify(name):
    return name.lower().strip().replace(' ', '_').replace('-', '_').replace('.', '_').replace(',', '')


def show_validation_result_table(validation_items):
    for item in validation_items:
        table = Table(
            box=box.ROUNDED,
            show_header=False,
        )
        table.add_column('Field', style='blue')
        table.add_column('Value')
        level_color = 'red' if item.level == 'ERROR' else 'yellow'
        table.add_row('Level', f'[bold {level_color}]{item.level}[/]')
        table.add_row('Message', Markdown(item.message))
        table.add_row('File', item.file or '-')
        table.add_row(
            'Code',
            Syntax(
                item.code,
                'python3',
                theme='ansi_light',
                dedent=True,
                line_numbers=True,
                start_line=item.start_line,
                highlight_lines={item.lineno},
            ) if item.code else '-',
        )
        console.print(table)

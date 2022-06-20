# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2022 Ingram Micro. All Rights Reserved.

from collections import defaultdict

from connect.cli.core.terminal import console


class SynchronizerStats(dict):
    """
    Track stats of synchronizer and print results when finished.
    This groups the stats in different modules.

    To increment stats of a module:

    stats['module name'].updated()  # +1 updated
    stats['module name'].deleted(3)  # +3 deleted

    To track errors:

    stats['module name'].error('error message')  # add error not related to any row
    stats['module name'].error('first error', 7)  # add an error in row #7
    stats['module name'].error(['second error', 'third error'], 7)  # add more errors in row #7
    stats['module name'].error('the error', range(1, 11))  # add an error in rows #1 to #10
    """

    COLUMNS = (
        'Module',
        ('right', 'Processed'),
        ('right', 'Created'),
        ('right', 'Updated'),
        ('right', 'Deleted'),
        ('right', 'Skipped'),
        ('right', 'Errors'),
    )

    def __init__(self, *args, operation='Sync', header='Results of synchronization'):
        self._initial_modules = args
        self.operation = operation
        self.header = header
        self.reset()

    def __str__(self):
        return '\n'.join(f'{k} - {v}' for k, v in self.items())

    def __getitem__(self, key):
        if key not in self:
            self[key] = _SynchronizerStatsModule(key)
        return super().__getitem__(key)

    def reset(self):
        """
        reset to initial modules, resetting all their stats.
        """
        self.clear()
        for module_name in self._initial_modules:
            self[module_name]

    def print(self):
        console.header(self.header)
        self.print_results()
        self.print_errors()

    def print_results(self):
        console.table(
            columns=self.COLUMNS,
            rows=[
                (module_stats.name, *module_stats.get_counts_as_tuple())
                for module_stats in self.values()
            ],
            expand=True,
        )

    def print_errors(self):  # noqa: CCR001
        total_error_count = sum(
            len(module_stats._errors) + len(module_stats._row_errors)
            for module_stats in self.values()
        )
        if total_error_count == 0:
            return

        console.confirm(
            f'\n{self.operation} operation had {total_error_count} errors, do you want to see them?',
            abort=True,
        )

        console.echo('')
        for module_stats in filter(lambda ms: ms._errors or ms._row_errors, self.values()):
            console.secho(f'Module {module_stats.name}:\n', fg='magenta')

            if module_stats._errors:
                console.echo('  Errors')
                console.echo("\n".join(f'    - {msg}' for msg in module_stats._errors))
                console.echo('')

            # group rows with same error message to avoid long prints in bulk errors
            first_row = None
            current_error = None
            for row_idx, messages in module_stats._row_errors.items():
                error = "\n".join(f'    - {msg}' for msg in messages)
                if not first_row:
                    first_row = row_idx
                if not current_error:
                    current_error = error
                if error != current_error:
                    self._print_error(current_error, first_row, row_idx - 1)
                    current_error = error
                    first_row = row_idx
            if current_error:
                self._print_error(current_error, first_row, row_idx)

    def _print_error(self, error, row, last_row=None):
        if last_row is None or row == last_row:
            console.echo(f'  Errors at row #{row}')
        else:
            console.echo(f'  Errors at rows #{row} to #{last_row}')
        console.echo(error)
        console.echo('')


class _SynchronizerStatsModule:

    def __init__(self, name):
        self.name = name
        self.reset()

    def __str__(self):
        return ', '.join(f'{k}: {v}' for k, v in self.get_counts_as_dict().items())

    def reset(self):
        self._updated = 0
        self._created = 0
        self._deleted = 0
        self._skipped = 0
        self._errors = []
        self._row_errors = defaultdict(list)

    def updated(self, count=1):
        self._updated += count

    def created(self, count=1):
        self._created += count

    def deleted(self, count=1):
        self._deleted += count

    def skipped(self, count=1):
        self._skipped += count

    def error(self, err, row=None):
        if not isinstance(err, (list, tuple)):
            err = [err]

        if row is None:
            self._errors.extend(err)
        elif hasattr(row, '__iter__'):
            for r in row:
                self._row_errors[r].extend(err)
        else:
            self._row_errors[row].extend(err)

    def get_processed_count(self):
        return (
            self._updated + self._created + self._deleted + self._skipped
            + len(self._errors) + len(self._row_errors)
        )

    def get_counts_as_dict(self):
        return {
            'processed': self.get_processed_count(),
            'created': self._created,
            'updated': self._updated,
            'deleted': self._deleted,
            'skipped': self._skipped,
            'errors': len(self._errors) + len(self._row_errors),
        }

    def get_counts_as_tuple(self):
        return (
            self.get_processed_count(),
            self._created,
            self._updated,
            self._deleted,
            self._skipped,
            len(self._errors) + len(self._row_errors),
        )


class SynchronizerStatsSingleModule(_SynchronizerStatsModule):
    """
    Track the stats of a single module.
    """

    def __init__(self, module_name):
        super().__init__(module_name)
        self.__stats = SynchronizerStats()
        self.__stats[module_name] = self

    def __str__(self):
        return f'{self.name} - {super().__str__()}'

    def print(self):
        self.__stats.print()

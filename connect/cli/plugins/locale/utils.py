import click
from cmr import render


def icon_for_autotranslate(resource):
    return '\u2713' if resource['auto_translation'] else '\u2716'


def stats_of_translations(resource):
    count = resource["stats"]["translations"]
    return count or '-'


def row_format_resource(*fields):
    return ('| {} ' * len(fields)).format(*fields) + '|\n'  # noqa: P103


def table_formater_resource(resource_str_list, count_of_resources, paging, page_size):
    header = resource_str_list[:1]
    if paging % page_size == 0:
        start = 1 if paging == page_size else paging - page_size
        if paging > page_size:
            start += 1
        click.echo(render(''.join(header + resource_str_list[start:])))
    else:
        start = count_of_resources - ((paging - 1) % page_size)
        if resource_str_list[start:] and len(resource_str_list[1:]) == count_of_resources:
            click.echo(render(''.join(header + resource_str_list[start:])))

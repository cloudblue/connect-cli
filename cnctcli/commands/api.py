import json

import click

from cnct import ConnectError, ConnectFluent
from cnct.client.models import Collection, Item


class ApiGroup(click.Group):
    def list_commands(self, ctx):
        cmds = super().list_commands(ctx)
        if ctx.info_name == 'api':
            return [cmd for cmd in cmds if cmd not in ('get', 'search', 'item')]
        if ctx.info_name == 'collection':
            return ['item', 'search', 'create', 'info']
        return cmds


def show_help(ctx, param, value):
    if not value:
        return value
    api = ctx
    while api.info_name != 'api':
        api = api.parent

    formatter = ctx.make_formatter()

    click.echo(ctx.get_usage() + ' COMMAND1 [ARGS]...\n')
    ctx.command.format_help_text(ctx, formatter)
    ctx.command.format_options(ctx, formatter)
    api.command.format_commands(ctx, formatter)
    click.echo(formatter.getvalue())
    return value
    # ctx.command.get_help_option_names(ctx)

    # click.echo(options)


@click.group(cls=ApiGroup, name='api', chain=True, invoke_without_command=True)
@click.option('--pretty', '-p', is_flag=True)
def grp_api(pretty):
    pass


@grp_api.resultcallback()
def process_browse(processors, pretty):
    config = click.get_current_context().obj
    config.validate()
    client = ConnectFluent(
        config.active.api_key,
        endpoint=config.active.endpoint,
    )
    result = client
    if not processors:
        click.echo(click.get_current_context().get_help())
    for processor in processors:
        result = processor(result)

    if isinstance(result, (list, dict)):
        if pretty:
            print(json.dumps(result, indent=2))
        else:
            print(json.dumps(result))


@grp_api.command('ns', short_help='Access a namespace')
@click.argument('name', metavar='namespace_name', nargs=1, required=True)
def ns(name):
    def processor(obj):
        return obj.ns(name)
    return processor


@grp_api.command('collection', short_help='Access a collection')
@click.argument('name', metavar='collection_name', nargs=1, required=False)
@click.option(
    '--help',
    '-h',
    'help_',
    callback=show_help,
    is_flag=True,
    expose_value=True,
    # is_eager=True,
    help='Show this message and exit.',
)
def collection(name, help_):
    def processor(obj):
        if help_:
            return
        if not name:
            click.secho('Missing parameter: name', fg='red')
            return
        return obj.collection(name)
    return processor


@grp_api.command('item', short_help='Access an item within the collection.')
@click.argument('item_id', metavar='item_id', nargs=1, required=True)
def item(item_id):
    def processor(obj):
        if not isinstance(obj, Collection):
            raise Exception('not a collection')
        return obj.item(item_id)
    return processor


@grp_api.command('filter', short_help='Search for items within the collection.')
@click.argument('query', metavar='query', nargs=1, required=False)
@click.option('--iterate/--no-iterate', is_flag=True, default=True)
def filter_(query, iterate):

    def processor(obj):
        for result in obj.filter(query):
            click.echo(json.dumps(result))
    return processor


@grp_api.command('get')
def get():
    def processor(obj):
        if not isinstance(obj, Item):
            raise Exception('not an Item')
        return obj.get()
    return processor


@grp_api.command('post')
@click.argument('payload', metavar='payload', nargs=1, required=False)
def post(payload):
    def processor(obj):
        try:
            return obj.post(payload=json.loads(payload))
        except ConnectError as ce:
            return {
                'status_code': ce.status_code,
                'error_code': ce.error_code,
                'errors': ce.errors,
            }
    return processor


@grp_api.command('create')
@click.argument('payload', metavar='payload', nargs=1, required=False, type=click.File('r'))
def create(payload):
    def processor(obj):
        try:
            return obj.create(payload=json.loads(payload.read()))
        except ConnectError as ce:
            return {
                'status_code': ce.status_code,
                'error_code': ce.error_code,
                'errors': ce.errors,
            }
    return processor


@grp_api.command('action', short_help='Access an action for an item.')
@click.argument('name', metavar='action_name', nargs=1, required=True)
def action(name):
    def processor(obj):
        return obj.action(name)
    return processor


@grp_api.command('docs', short_help='Show API docs.')
def docs():
    def processor(obj):
        obj.help()
    return processor

import click


def continue_or_quit():
    while True:
        click.echo('')
        click.echo("Press 'c' to continue or 'q' to quit ", nl=False)
        c = click.getchar()
        click.echo()
        if c == 'c':
            return True
        if c == 'q':
            return False

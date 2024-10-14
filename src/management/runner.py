import click

@click.command()
@click.option('--count', default=1, help='Number of greetings.')
def hello(count):
    """Simple program that greets NAME for a total of COUNT times."""
    click.echo(f"Hello {count}!")

if __name__ == '__main__':
    hello()
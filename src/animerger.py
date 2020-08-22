import click
from scanus import Scanus
from container import Stream, MetaContainer
from argument import Argument


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        click.echo("Interactive mode not implemented")


@cli.command(help = "Scan path for containers")
@click.argument("path", type=click.Path())
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode")
@click.option("-s", "--silent", is_flag=True, help="Enables silent mode")
@click.option(
    "--special",
    "-r",
    "--sp",
    is_flag=True,
    help="Turn on nested search in path (special ep search).",
)
def scan(path, special, verbose, silent):
    scanner = Scanus()
    scanner.search_sp = special
    scanner.scan_directory(path)
    if not silent:
        click.echo("Scan directory: {}".format(path))
        if len(scanner.container_list):
            result_str = "Found {} containers.".format(len(scanner.container_list))
            if len(scanner.attach_list):
                result_str = result_str[:-1] + ", with {} attachments".format(
                    len(scanner.attach_list)
                )
            click.echo(result_str)
        else:
            click.echo("Containers not found.")
        if verbose:
            for i, container in enumerate(scanner.container_list, start=1):
                click.echo("Container №{0}:".format(i))
                for i, file in enumerate(container, start=1):
                    click.echo("{:3d}. {}".format(i, file))
            print("\nAttachments:")
            for i, attach in enumerate(scanner.attach_list, start=1):
                click.echo("{:3d}. {}".format(i, attach))
    return (scanner.container_list,scanner.attach_list)

@cli.command(help = "Generate ffmpeg command line for merging containers")
@click.argument("path", type=click.Path())
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode")
@click.option("-s", "--silent", is_flag=True, help="Enables silent mode")
@click.option(
    "--special",
    "-r",
    "--sp",
    is_flag=True,
    help="Turn on nested search in path (special ep search).",
)
def compile(path, special, verbose, silent):
    container_list,attach_list = scan(path,special,verbose,silent)
    for container in container_list:
        meta_container = MetaContainer(container,attach_list)
        

@cli.command(help = "Merge containers")
@click.argument("path", type=click.Path())
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode")
@click.option("-s", "--silent", is_flag=True, help="Enables silent mode")
@click.option(
    "--special",
    "-r",
    "--sp",
    is_flag=True,
    help="Turn on nested search in path (special ep search).",
)
def merge(path, special, verbose, silent):
    scan_result = scan(path,special,verbose,silent)



if __name__ == "__main__":
    cli()

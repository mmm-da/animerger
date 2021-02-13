import click
from scanus import Scanus
from container import Stream, MetaContainer
from argument import Argument
from subprocess import run

def __scan(path, special, verbose, silent):
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
            click.echo("Containers not found.", err=True)
        if verbose:
            for i, container in enumerate(scanner.container_list, start=1):
                click.echo("Container №{0}:".format(i))
                for i, file in enumerate(container, start=1):
                    click.echo("{:3d}. ".format(i) + "%s" % click.format_filename(file))
            print("\nAttachments:")
            for i, attach in enumerate(scanner.attach_list, start=1):
                click.echo("{:3d}. ".format(i) + "%s" % click.format_filename(attach))
    return (scanner.container_list, scanner.attach_list)

@click.command(help="Generate ffmpeg command line for merging containers")
@click.argument("path", type=click.Path())
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose mode")
@click.option("-s", "--silent", is_flag=True, help="Enable silent mode")
@click.option(
    "-r",
    "--special",
    is_flag=True,
    help="Turn on nested search in path (special ep search).",
)
@click.option("--output_path", type=click.types.Path(), help="Output path")
@click.option("--video_codec", "--vc", type=str, help="Video stream output codec")
@click.option("--audio_codec", "--ac", type=str, help="Audio stream output codec")
@click.option("--title", "-t", type=str, help="Title of release")
@click.option("--additional_args", type=str, help="Additional args to ffmpeg")
@click.option("--name_template", type=str, help="Template for naming containers")
@click.option(
    "-c", "--only_compile", is_flag=True, help="Only generate command for ffmpeg"
)
def merge(
    path,
    special,
    verbose,
    silent,
    name_template,
    title,
    video_codec,
    audio_codec,
    save_path,
    additional_args,
    only_compile,
):
    container_list, attach_list = __scan(path, special, verbose, silent)
    command_list = []

    for i, container in enumerate(container_list, start=1):
        meta_container = MetaContainer(container, attach_list, name_template, title)
        command = Argument.compile_mkv(
            meta_container,
            video_codec=video_codec,
            audio_codec=audio_codec,
            additional_args=additional_args,
            save_path=save_path,
        )
        command_list.append(command)
        if not silent:
            click.echo("Container №{} - {}".format(i, meta_container.name))
            if only_compile:
                click.echo("Command: ")
                click.echo(command)
            if verbose:
                click.echo("Streams: ")
                for stream in meta_container.stream_list:
                    print(stream)
        if not only_compile:
            run(command)

if __name__ == "__main__":
    merge()

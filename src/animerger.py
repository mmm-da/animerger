from os import environ
import typer
from typing import Optional

from constants import VERSION
from environment import environment

app = typer.Typer()

def version_callback(value: bool):
    if value:
        typer.echo(f"animerger version: {VERSION}")
        typer.echo(f"source code: https://github.com/mmm-da/animerger")
        raise typer.Exit()

def verbose_callback(value: int):
    if (value > 5) or (value < 0):
        typer.echo(
            typer.style("verbose level should be in range 0 - 5", fg=typer.colors.RED, bold=True)
        )
        raise typer.Exit()
    if value >= 2:
        print(f"animerger version: {VERSION}\n")    
    if value >= 4:
        print(environment)

@app.command()
def merge(
    path: str,
    recursive: bool = typer.Option(False , "--recursive","-r", show_default=False),
    dry_run: bool = typer.Option(False ,"--dry_run", show_default=False),
    guess_title: bool = typer.Option(False , "--guess_title" ,show_default=False),    
    verbose: int = typer.Option(1, "--verbose", "-v", callback=verbose_callback,help="animerger verbose level [0-5]"),
    title: str = typer.Option(None, "--title", "-t"),
    video_codec_args: str = typer.Option(None, "--video_codec_args"),
    audio_codec_args: str = typer.Option(None, "--audio_codec_args"),
    other_args: str = typer.Option(None, "--other_args"),
    output: str = typer.Option(None, "--output", "-o"),
    profile: str = typer.Option(None, "--profile", "-p"),
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback
    )
    ):
    pass

if __name__ == "__main__":
    app()

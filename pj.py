#!/usr/bin/env python3
"""pretty print json files, optionally expanding each dict."""

__author__ = 'Brandon Wells'
__email__ = 'b.w.prog@outlook.com'
__copyright__ = '© 2024 Brandon Wells'
__license__ = 'GPL3+'
__status__ = 'Development'
__update__ = '2024.02.06'
__version__ = '0.5.0'


import json
from collections.abc import Callable
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich import print
from rich.pretty import Pretty
from rich.traceback import install

# cap file size at 10MB by default
MAX_FILE_SIZE = 10_000_000

install()
app: Callable[..., None] = typer.Typer(rich_markup_mode='rich')
ver: str = f'pj.py [green]- (Print JSON) -[/] [blue]{__version__}[/] [green]({__update__})[/]'


# ~~~ #
def callback_version(version: bool) -> None:
    """Print version and exit.

    Parameters
    ----------
    version : bool
        CLI option -v/--version to print program version

    Raises
    ------
    typer.Exit
        normal cleanup and exit after completing request
    """
    if version:
        print(f'\n{ver}\n')
        raise typer.Exit


# ~~~ #
@app.command()
def main(
        file: Annotated[Path, typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            show_default=False,
            rich_help_panel='[blue]JSON FILE[/]',
            help='the JSON file to pretty print',
        )],
        flag_e_expand: Annotated[bool, typer.Option(
            '-e',
            '--expand-all',
            rich_help_panel='[yellow]JP Options[/]',
            help='expand all depths',
        )] = False,
        flag_d_depth: Annotated[Optional[int | None], typer.Option(
            '-d',
            '--max-depth',
            rich_help_panel='[yellow]JP Options[/]',
            help='maximum depth to expand',
        )] = None,
        flag_g_guides: Annotated[bool, typer.Option(
            '-g',
            '--guides',
            rich_help_panel='[yellow]JP Options[/]',
            help='print indent guides',
        )] = False,
        flag_l_length: Annotated[Optional[int | None], typer.Option(
            '-l',
            '--max-length',
            rich_help_panel='[yellow]JP Options[/]',
            help='maximum depth of an object before abbreviating',
        )] = None,
        flag_m_size: Annotated[int, typer.Option(
            '-m',
            '--max-file-size',
            rich_help_panel='[yellow]JP Options[/]',
            show_default=False,
            help=('maximum size of JSON file to read (protect from running out of RAM) '
                  f'\[default: {MAX_FILE_SIZE:,}]'),  # noqa: W605 , PGH003 # type: ignore
        )] = MAX_FILE_SIZE,
        flag_s_string: Annotated[Optional[int | None], typer.Option(
            '-s',
            '--max-string',
            rich_help_panel='[yellow]JP Options[/]',
            help='maximum length of string before truncating',
        )] = None,
        flag_t_tabs: Annotated[int, typer.Option(
            '-t',
            '--tab-size',
            rich_help_panel='[yellow]JP Options[/]',
            help='number of spaces of indent',
        )] = 4,
        flag_v_validate: Annotated[bool, typer.Option(
            '-v',
            '--validate',
            rich_help_panel='[yellow]JP Options[/]',
            help="don't output, just read to validate proper JSON",
        )] = False,
        version: Annotated[bool, typer.Option(
            '--version',
            is_eager=True,
            callback=callback_version,
            help='Print version and exit.',
        )] = False,
) -> None:
    """pj.py - (Print JSON)"""  # noqa: D400
    # check file size and exit if too big
    if (file_size := file.stat().st_size) > flag_m_size:
        print(f'[red]ERROR:[/] size of file too large to read. ([yellow]{file_size} > {flag_m_size}[/])')
        raise typer.Exit(code=1)

    # read and validate JSON, exit printing the error if invalid
    try:
        with file.open(mode='r') as f:
            valid_json_file = json.load(fp=f)
    except json.JSONDecodeError as e:
        print(f'[red]ERROR:[/] Invalid JSON data. File maybe corrupt or improperly formatted.\n\t{e}')
        raise typer.Exit(code=1) from None

    # if validate only, confirm without printing file
    if flag_v_validate:
        print(f'File: {file} [green]* valid JSON file *[/]')
    else:
        # prettify the valid JSON object
        pretty_json_file = Pretty(valid_json_file,
                                indent_size=flag_t_tabs,
                                indent_guides=flag_g_guides,
                                max_length=flag_l_length,
                                max_string=flag_s_string,
                                max_depth=flag_d_depth,
                                expand_all=flag_e_expand)
        print(pretty_json_file)


# ~~~ #
if __name__ == '__main__':

    app()

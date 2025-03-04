# SPDX-FileCopyrightText: 2023-present Henry Watkins <h.watkins@ucl.ac.uk>
#
# SPDX-License-Identifier: MIT

"""Command line interface for labellasso."""

import sys

import click

from labellasso.__about__ import __version__
from labellasso.app import create_bokeh_app, start_bokeh_server
from labellasso.data import DataValidationError


@click.command(
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.option("--port", default=5006, type=int, help="Port to run the Bokeh server on.")
@click.option(
    "--address", default="localhost", help="Address to run the Bokeh server on."
)
@click.option(
    "--x-column", default="x", help="Name of the column to use for x-coordinates."
)
@click.option(
    "--y-column", default="y", help="Name of the column to use for y-coordinates."
)
@click.option(
    "--name-column", default="name", help="Name of the column to use for point names."
)
@click.version_option(version=__version__, prog_name="labellasso")
@click.argument("input_file", type=click.Path(exists=True))
def labellasso(
    port: int,
    address: str,
    x_column: str,
    y_column: str,
    name_column: str,
    input_file: str,
) -> None:
    """
    A simple data-point labelling tool using scatterplot lasso.

    INPUT_FILE should be a CSV file containing at least three columns:
    - A name column (default: 'name')
    - An x-coordinate column (default: 'x')
    - A y-coordinate column (default: 'y')

    The tool will create a new file with the suffix '_labelled' containing
    the original data plus a 'label' column with the assigned labels.
    """
    try:
        # Display startup information
        click.echo(f"LabelLasso v{__version__}")
        click.echo(f"Opening Bokeh application on http://{address}:{port}/")

        # Create and start the application
        app = create_bokeh_app(input_file)
        start_bokeh_server(app, port, address)

    except FileNotFoundError as e:
        click.secho(f"Error: {e}", fg="red")
        sys.exit(1)
    except DataValidationError as e:
        click.secho(f"Error in input data: {e}", fg="red")
        sys.exit(1)
    except Exception as e:
        click.secho(f"Unexpected error: {e}", fg="red")
        sys.exit(1)

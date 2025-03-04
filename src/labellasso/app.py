# SPDX-FileCopyrightText: 2023-present Henry Watkins <h.watkins@ucl.ac.uk>
#
# SPDX-License-Identifier: MIT

"""Bokeh application for labellasso."""

from pathlib import Path
from typing import Callable

from bokeh.document import Document
from bokeh.layouts import column, row
from bokeh.server.server import Server

from labellasso.data import (
    create_column_data_source,
    get_label_statistics,
    load_data,
    save_data,
    update_labels,
)
from labellasso.plot import (
    create_input_widget,
    create_save_button,
    create_scatter_plot,
    update_plot_title,
)


def create_bokeh_app(input_file_path: str) -> Callable[[Document], None]:
    """
    Create a Bokeh application for interactive data labeling.

    Args:
        input_file_path: Path to the input CSV file

    Returns:
        Callable function to be used with Bokeh server

    Raises:
        FileNotFoundError: If the input file doesn't exist
    """

    def app(doc: Document) -> None:
        """
        Bokeh application for interactive data labeling.

        Args:
            doc: Bokeh document to populate
        """
        input_file = Path(input_file_path)

        try:
            # Load and validate data
            df, output_path = load_data(input_file)

            # Create data source
            source = create_column_data_source(df)

            # Get label statistics
            unlabeled_percentage, unique_labels = get_label_statistics(df)

            # Create plot
            p, hover = create_scatter_plot(
                source,
                [*list(unique_labels), ""],
                f"Scatter plot lasso labeller, labeled: {100-unlabeled_percentage:.1f}%",
            )

            # Set up widgets
            text = create_input_widget()
            button = create_save_button()

            # Set up callbacks
            def add_label_callback(attrname: str, old: str, new: str) -> None:
                """Callback for adding labels to selected points."""
                nonlocal df
                df = update_labels(df, source, source.selected.indices, text.value)
                unlabeled_percentage, _ = get_label_statistics(df)
                update_plot_title(p, unlabeled_percentage)

            def save_data_callback() -> None:
                """Callback for saving labeled data."""
                try:
                    save_data(df, output_path)
                    doc.add_next_tick_callback(
                        lambda: doc.add_notification(
                            f"Data saved to {output_path.name}", type="success"
                        )
                    )
                except IOError as err:
                    doc.add_next_tick_callback(
                        lambda err=err: doc.add_notification(
                            f"Error saving data: {err}", type="error"
                        )
                    )

            # Connect callbacks
            text.on_change("value", add_label_callback)
            button.on_click(save_data_callback)

            # Set up layout
            inputs = column(text, button)
            doc.add_root(row(inputs, p, width=800))
            doc.title = "LabelLasso"

        except Exception as e:
            # Handle errors in application initialization
            error_message = f"Error initializing application: {e!s}"
            doc.add_root(column(error_message))
            doc.title = "LabelLasso - Error"

    return app


def start_bokeh_server(
    app_func: Callable[[Document], None], port: int = 5006, address: str = "localhost"
) -> None:
    """
    Start a Bokeh server with the specified application.

    Args:
        app_func: Application function to run
        port: Port to run the server on
        address: Address to bind the server to
    """
    server = Server({"/": app_func}, num_procs=1, port=port, address=address)
    server.start()

    # Open browser
    server.io_loop.add_callback(server.show, "/")

    # Start the server
    server.io_loop.start()

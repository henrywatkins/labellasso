import random
import sys
from pathlib import Path

import click
import numpy as np
import pandas as pd
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import (Button, CategoricalColorMapper, ColumnDataSource,
                          HoverTool, Slider, TextInput)
from bokeh.palettes import Category10, Category20, Turbo256
from bokeh.plotting import figure, show
from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature
from bokeh.server.server import Server
from bokeh.transform import factor_cmap

from labellasso.__about__ import __version__


def app(doc):
    input_file = Path(sys.argv[-1])
    filename = input_file.stem
    new_path = input_file.with_name(filename + "_labelled.csv")

    df = pd.read_csv(input_file, index_col=False)
    if not ("label" in df.columns):
        df["label"] = ""
    df.loc[df["label"].isna(), "label"] = ""
    source = ColumnDataSource(df)
    hover = HoverTool(tooltips=[("Name", "@name"), ("Label", "@label")])

    TOOLS = "crosshair,pan,zoom_in,zoom_out,box_zoom,reset,save,lasso_select,box_select"

    p = figure(tools=TOOLS, title="Scatter plot lasso labeller")
    unique_labels = df["label"].unique().astype(str).tolist()
    cmap = factor_cmap("label", Category20[3], unique_labels)
    p.scatter(source=source, fill_alpha=0.6, color=cmap)

    # Set up widgets
    text = TextInput(title="Input label name for selected points", value="label name")
    button = Button(label="save labels", button_type="success")
    p.add_tools(hover)

    # Set up callbacks
    def add_label(attrname, old, new):
        df.loc[source.selected.indices, "label"] = text.value
        source.data = ColumnDataSource.from_df(df)
        proportion = 100 * (df["label"].value_counts(normalize=True)[""])
        p.title.text = f"Scatter plot lasso labeller, labelled: {proportion}%"

    def save_data():
        df.to_csv(new_path, index=False)

    text.on_change("value", add_label)
    button.on_click(save_data)
    # Set up layouts and add to document
    inputs = column(text, button)
    doc.add_root(row(inputs, p, width=800))
    doc.title = "lasso"


@click.command(
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.option("--port", default=5006, help="Port to run the Bokeh server on.")
@click.option(
    "--address", default="localhost", help="Address to run the Bokeh server on."
)
@click.version_option(version=__version__, prog_name="labellasso")
@click.argument("input_file", type=click.Path(exists=True))
def labellasso(port, address, input_file):
    """A simple data-point labelling tool using scatterplot lasso"""
    click.echo(f"Opening Bokeh application on http://{address}:{port}/")
    server = Server({"/": app}, num_procs=1, port=port, address=address)
    server.start()
    server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()

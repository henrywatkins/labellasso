""" Present an interactive function explorer with slider widgets.
Scrub the sliders to change the properties of the ``sin`` curve, or
type into the title text box to update the title of the plot.
Use the ``bokeh serve`` command to run the example by executing:
    bokeh serve bokeh_lasso.py
at your command prompt. Then navigate to the URL
    http://localhost:5006/lasso
in your browser.
"""


import pathlib
import numpy as np
import pandas as pd
from bokeh.plotting import figure, show

from bokeh.palettes import Category10, Category20
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import (
    ColumnDataSource,
    Slider,
    TextInput,
    Button,
    HoverTool,
    CategoricalColorMapper,
)
from bokeh.plotting import figure


data_path = pathlib.Path("test.csv")

filename = data_path.stem
new_path = data_path.with_name(filename + "_labelled.csv")

df = pd.read_csv(data_path, index_col=False)

# df["class"] = df["class"].fillna("null")
df["label"] = np.nan
df["colour"] = np.nan
df.loc[df["class"].isna(), "colour"] = "noclass"
df.loc[~df["class"].isna(), "colour"] = "withclass"


source = ColumnDataSource(df)

hover = HoverTool(tooltips=[("Name", "@name"), ("Class", "@class")])
color_mapper = CategoricalColorMapper(
    factors=["noclass", "withclass", "labelled"], palette=Category10[3]
)

TOOLS = "crosshair,pan,zoom_in,zoom_out,box_zoom,reset,save,lasso_select,"

p = figure(tools=TOOLS, title="Scatter plot lasso labeller")

p.scatter(
    source=source, fill_alpha=0.6, color=dict(field="colour", transform=color_mapper)
)
# Set up widgets
text = TextInput(title="Input label name for selected points", value="labelname")
button = Button(label="save labels", button_type="success")
p.add_tools(hover)

# Set up callbacks
def add_label(attrname, old, new):
    df.loc[source.selected.indices, "label"] = text.value
    df.loc[source.selected.indices, "colour"] = "labelled"
    source.data = df


def save_data():
    df.to_csv(new_path, index=False)


text.on_change("value", add_label)
button.on_click(save_data)

# Set up layouts and add to document
inputs = column(text, button)

curdoc().add_root(row(inputs, p, width=800))
curdoc().title = "lasso"

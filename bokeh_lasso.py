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
import random
import numpy as np
import pandas as pd
from bokeh.plotting import figure, show

from bokeh.palettes import Category10, Category20, Turbo256
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
#
#SOURCE_DATA = "../label_lasso_entity_data_tsne_endweighted_inprogress_labelled.csv"
SOURCE_DATA = "../lasso_entity_data_freq_label_labelled.csv"
#SOURCE_DATA = "../lasso_entity_data_freq_label.csv"

data_path = pathlib.Path(SOURCE_DATA)

filename = data_path.stem
new_path = data_path.with_name(filename + "_labelled.csv")

df = pd.read_csv(data_path, index_col=False)


if not ("label" in df.columns):
    df["label"] = np.nan
if not ("colour" in df.columns):
    df["colour"] = np.nan

df.loc[df["class"].isna(), "colour"] = "noclass"
#df.loc[~df["class"].isna(), "colour"] = "withclass"
df.loc[~df["class"].isna(), "colour"] = df.loc[~df["class"].isna(), "class"]
df.loc[~df["label"].isna(), "colour"] = "labelled"

MIN = 3
df["x"] = df["tsne_x"]
df["y"] = df["tsne_y"]
df["size"] = 0.3*np.sqrt(df["frequency"])
df.loc[df["size"]<MIN, "size"] = MIN
print(df.sample(10))
source = ColumnDataSource(df)

hover = HoverTool(tooltips=[("Name", "@name"), ("Class", "@class")])
#factors = ["noclass", "withclass", "labelled"]
#cmap = Category10[len(factors)]
factors = list(df["colour"].unique())
factors.append("noclass")
factors.append("labelled")
#cmap = [c for i, c in enumerate(Turbo256) if i%len(factors)==0]
cmap = []
turbo = list(Turbo256)
for i in factors:
    colour = turbo.pop(random.randint(0,len(turbo)))
    cmap.append(colour)
color_mapper = CategoricalColorMapper(
    factors=factors, palette= cmap
)

TOOLS = "crosshair,pan,zoom_in,zoom_out,box_zoom,reset,save,lasso_select,box_select"

p = figure(tools=TOOLS, title="Scatter plot lasso labeller")

p.scatter(
    source=source, size="size", fill_alpha=0.6, color=dict(field="colour", transform=color_mapper)
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
    proportion = 100*(df.loc[~df["label"].isna(), "frequency"].sum()/df["frequency"].sum())
    p.title.text = f"Scatter plot lasso labeller, labelled: {proportion}%"


def save_data():
    df.to_csv(new_path, index=False)


text.on_change("value", add_label)
button.on_click(save_data)

# Set up layouts and add to document
inputs = column(text, button)

curdoc().add_root(row(inputs, p, width=800))
curdoc().title = "lasso"

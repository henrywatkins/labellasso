""" Present an interactive function explorer with slider widgets.
Scrub the sliders to change the properties of the ``sin`` curve, or
type into the title text box to update the title of the plot.
Use the ``bokeh serve`` command to run the example by executing:
    bokeh serve report_lasso.py
at your command prompt. Then navigate to the URL
    http://localhost:5006/report_lasso
in your browser.

Host on network with
bokeh serve --address 192.168.1.208 --port 5001 --allow-websocket-origin=192.168.1.201:5001 --allow-websocket-origin=192.168.1.208:5001 --show simple_app.py

"""


from pathlib import Path
import random
import numpy as np
import pandas as pd
import pickle
from numba import jit

from bokeh.plotting import figure, show
from bokeh.palettes import Category10, Turbo256, Spectral, Bokeh, Set1, Set2
from bokeh.io import curdoc
from bokeh.layouts import column, row, gridplot
from bokeh.transform import linear_cmap
from bokeh.models import (
    ColumnDataSource,
    Slider,
    TextInput,
    Button,
    HoverTool,
    CrosshairTool,
    Span,
    CategoricalColorMapper,
    Paragraph,
    Div,
    Select,
    MultiChoice,
)
from bokeh.plotting import figure

# ROOT = Path("/home/hwatkins/Desktop/neuroData/lasso_data/lasso_data_071222")
ROOT = Path("/home/hwatkins/Desktop/neuroNLP/runs/path_model_030123/lasso_data")
DATA = ROOT / "lasso_report_data.csv"
out_path = ROOT

usecols = [
    "X",
    "Y",
    "_X",
    "_Y",
    "asserted-terms",
    "has-pathology-cerebrovascular",
    "has-pathology-congenital-developmental",
    "has-pathology-csf-disorders",
    "has-pathology-endocrine",
    "has-pathology-haemorrhagic",
    "has-pathology-infectious",
    "has-pathology-inflammatory-autoimmune",
    "has-pathology-ischaemic",
    "has-pathology-metabolic-nutritional-toxic",
    "has-pathology-musculoskeletal",
    "has-pathology-neoplastic-paraneoplastic",
    "has-pathology-neurodegenerative-dementia",
    "has-pathology-opthalmological",
    "has-pathology-traumatic",
    "has-pathology-treatment",
    "has-pathology-vascular",
]

df = pd.read_csv(DATA, low_memory=False, index_col=False, usecols=usecols)
vectors = np.load(ROOT / "lasso_report_vectors.npy")
vocab = pickle.load(open(ROOT / "lasso_report_vocab.pkl", "rb"))
reversed_vocab = {j: i for i, j in vocab.items()}
filename = DATA.stem
new_path = DATA.with_name(filename + "_labelled.csv")


@jit(nopython=True, parallel=True)
def numba_cluster_feat_mccs(cluster_id, feature_vecs, cluster_vec):
    """numba-accelerated matthews correlation coefficient calculation
    for finding base features most heavily correlated with cluster ids"""
    mccs = []
    for feature_idx in range(feature_vecs.shape[1]):
        in_cluster = cluster_vec == cluster_id
        has_feature = feature_vecs[:, feature_idx] > 0.0
        tp = np.logical_and(in_cluster, has_feature).sum()
        fp = np.logical_and(np.logical_not(in_cluster), has_feature).sum()
        tn = np.logical_and(
            np.logical_not(in_cluster), np.logical_not(has_feature)
        ).sum()
        fn = np.logical_and(in_cluster, np.logical_not(has_feature)).sum()
        num = tp * tn - fp * fn
        denom = np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
        MCC = num / denom
        mccs.append(MCC)
    mccs = np.array(mccs)
    return mccs


if not ("label" in df.columns):
    df["label"] = "unlabelled"
if not ("colour" in df.columns):
    df["colour"] = "nocolour"
if not ("has-selected-features" in df.columns):
    df["has-selected-features"] = "False"

df["asserted_terms"] = df["asserted-terms"].str.replace("\n", ", ")

pathology_columns = [i for i in df.columns if "has-path" in i]
pathology_columns_and = [i + "_and" for i in pathology_columns]
pathology_columns_ = [j + "_" for j in pathology_columns]
pathology_columns_and_ = [j + "_" for j in pathology_columns_and]


df[pathology_columns_] = df[pathology_columns].astype(str)
df[pathology_columns_and] = df[pathology_columns]
df[pathology_columns_and_] = df[pathology_columns_and].astype(str)


factors = ["True", "False", "nocolour", "labelled", "unlabelled", "other"]
cmap = Category10[6]
# color_palettes = []
color_mapper = CategoricalColorMapper(factors=factors, palette=cmap)
colour_options = (
    ["label", "has-selected-features"] + pathology_columns_ + pathology_columns_and_
)
feature_options = sorted(list(vocab.values()))


df["x"] = df["X"]
df["y"] = df["Y"]
source = ColumnDataSource(df)


hist, hx, hy = np.histogram2d(df["x"], df["y"], bins=500)
hist += 1
hist = np.log10(hist).T

width = Span(dimension="width", line_width=1)
height = Span(dimension="height", line_width=1)

TOOLS = "pan,zoom_in,zoom_out,box_zoom,reset,save,lasso_select,box_select"

p = figure(
    tools=TOOLS,
    title="Scatter plot lasso labeller",
    output_backend="webgl",
    x_range=(min(hx), max(hx)),
    y_range=(min(hy), max(hy)),
)
p.add_tools(CrosshairTool(overlay=[width, height]))
p.scatter(
    source=source,
    fill_alpha=0.6,
    radius=0.003,
    color=dict(field="colour", transform=color_mapper),
)


hover = HoverTool(tooltips=[("Terms", "@asserted_terms")])

# Set up widgets
text = TextInput(title="Input label name for selected points", value="labelname")
info = Paragraph(text="Important features", width=200, height=100)
save_button = Button(label="save labels", button_type="success")
update_button = Button(label="update plot", button_type="success")
calculate_button = Button(label="calculate feature importances", button_type="success")
color_chooser = Select(
    title="Colour points by:", value="Labelled?", options=colour_options
)
feature_selector = MultiChoice(
    title="Choose individual report features:", value=[], options=feature_options
)

p.add_tools(hover)
HTOOLS = "pan,zoom_in,zoom_out,box_zoom,reset,save"
h = figure(
    tools=HTOOLS,
    x_range=p.x_range,
    y_range=p.y_range,
    title="Density plot",
    output_backend="webgl",
)
h.add_tools(CrosshairTool(overlay=[width, height]))
h.image(
    image=[hist],
    x=hx[0],
    y=hy[0],
    dw=hx[-1] - hx[0],
    dh=hy[-1] - hy[0],
    palette="Viridis256",
)

# Set up callbacks
def add_label(attrname, old, new):
    df.loc[source.selected.indices, "label"] = text.value
    source.data.update(df)


def calculate_features():
    cluster_ids = np.zeros(vectors.shape[0], dtype=int)
    cluster_ids[source.selected.indices] = 1
    mccs = numba_cluster_feat_mccs(1, vectors, cluster_ids)
    sorts = np.argsort(mccs)[-5:]
    terms = ", ".join([vocab[k] for k in sorts])
    info.text = f"Important features: \n{terms}"


def save_data():
    df.to_csv(new_path, index=False)


def change_colour(attrname, old, new):
    df["colour"] = df[color_chooser.value]
    source.data.update(df)


def change_features(attrname, old, new):
    feature_idxs = [reversed_vocab[j] for j in feature_selector.value]
    feature_matrix = vectors[:, feature_idxs].sum(axis=1).astype(bool)
    df["has-selected-features"] = feature_matrix
    for i in pathology_columns_and:
        df[i] = df[i] & df["has-selected-features"]
    df[pathology_columns_and_] = df[pathology_columns_and].astype(str)
    df["has-selected-features"] = df["has-selected-features"].astype(str)
    df["colour"] = df["has-selected-features"]
    source.data.update(df)


text.on_change("value", add_label)
color_chooser.on_change("value", change_colour)
feature_selector.on_change("value", change_features)
save_button.on_click(save_data)
calculate_button.on_click(calculate_features)


# Set up layouts and add to document
inputs = column(
    text,
    calculate_button,
    info,
    color_chooser,
    feature_selector,
    update_button,
    save_button,
)
plots = column(p, h)

curdoc().add_root(row(inputs, plots, width=800))
curdoc().title = "lasso"

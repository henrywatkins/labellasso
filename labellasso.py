#!/bin/#!/usr/bin/env python

import argparse
import pathlib

import numpy as np
import pandas as pd
from matplotlib.widgets import LassoSelector, TextBox, Button
from matplotlib.path import Path


class SelectFromCollection:
    """
    Select indices from a matplotlib collection using `LassoSelector`.

    Selected indices are saved in the `ind` attribute. This tool fades out the
    points that are not part of the selection (i.e., reduces their alpha
    values). If your collection has alpha < 1, this tool will permanently
    alter the alpha values.

    Note that this tool selects collection objects based on their *origins*
    (i.e., `offsets`).

    Parameters
    ----------
    ax : `~matplotlib.axes.Axes`
        Axes to interact with.
    collection : `matplotlib.collections.Collection` subclass
        Collection you want to select from.
    alpha_other : 0 <= float <= 1
        To highlight a selection, this tool sets all selected points to an
        alpha value of 1 and non-selected points to *alpha_other*.
    """

    def __init__(self, ax, collection, alpha_other=0.3):
        self.canvas = ax.figure.canvas
        self.collection = collection
        self.alpha_other = alpha_other

        self.xys = collection.get_offsets()
        self.Npts = len(self.xys)

        # Ensure that we have separate colors for each object
        self.fc = collection.get_facecolors()
        if len(self.fc) == 0:
            raise ValueError("Collection must have a facecolor")
        elif len(self.fc) == 1:
            self.fc = np.tile(self.fc, (self.Npts, 1))

        self.lasso = LassoSelector(ax, onselect=self.onselect)
        self.ind = []

    def onselect(self, verts):
        path = Path(verts)
        self.ind = np.nonzero(path.contains_points(self.xys))[0]
        self.fc[:, -1] = self.alpha_other
        self.fc[self.ind, -1] = 1
        self.collection.set_facecolors(self.fc)
        self.canvas.draw_idle()

    def disconnect(self):
        self.lasso.disconnect_events()
        self.fc[:, -1] = 1
        self.collection.set_facecolors(self.fc)
        self.canvas.draw_idle()


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    parser = argparse.ArgumentParser(
        description="Lasso a set of points and give them a label."
    )
    parser.add_argument("input", type=str, help="input file of data to label")
    args = parser.parse_args()

    data_path = pathlib.Path(args.input)

    df = pd.read_csv(data_path)
    filename = data_path.stem
    new_path = data_path.with_name(filename + "_labelled.csv")

    df["label"] = ""

    subplot_kw = dict(
        xlim=(df["x"].min(), df["x"].max()),
        ylim=(df["y"].min(), df["y"].max()),
        autoscale_on=False,
    )
    fig, ax = plt.subplots(subplot_kw=subplot_kw, figsize=(30, 30))
    fig.subplots_adjust(bottom=0.25)
    ax.set_title("Lasso points, add label, then press enter")

    pts = ax.scatter(df["x"], df["y"], s=5, c="b")
    selector = SelectFromCollection(ax, pts)
    archetype_df = df[df["colour"] != -1]
    key_pts = ax.scatter(archetype_df["x"], archetype_df["y"], s=5, c="y")

    annot = ax.annotate(
        "",
        xy=(0, 0),
        xytext=(20, 20),
        textcoords="offset points",
        bbox=dict(boxstyle="round", fc="w"),
        arrowprops=dict(arrowstyle="->"),
    )
    annot.set_visible(False)
    c = df["colour"].to_numpy()
    cmap = plt.cm.RdYlGn
    norm = plt.Normalize(1, 4)
    textboxintput = "No label"

    def submit(expression):
        textboxintput = str(expression)
        ax.autoscale_view()
        ax.set_yax
        fig.canvas.draw()

    axbox = fig.add_axes([0.1, 0.1, 0.8, 0.075])
    text_box = TextBox(axbox, "Label")
    buttonbox = fig.add_axes([0.1, 0.01, 0.8, 0.075])
    button = Button(buttonbox, "Save labelled data")

    def save_data(event):
        df.to_csv(new_path, index=False)

    button.on_clicked(save_data)

    def accept(event):
        if event.key == "enter":
            print("Selected points:")
            print(selector.xys[selector.ind])
            df_to_show = df.iloc[selector.ind]
            print(text_box.text)
            df.loc[selector.ind, "label"] = str(text_box.text)
            pts = ax.scatter(df_to_show["x"], df_to_show["y"], s=5, c="r")
            fig.canvas.draw()
            print(df["label"].value_counts())

    def update_annot(ind):
        pos = pts.get_offsets()[ind["ind"][0]]
        annot.xy = pos
        text = "\n".join(
            [str(df["name"][n]) + " : " + str(df["class"][n]) for n in ind["ind"]]
        )
        annot.set_text(text)
        annot.get_bbox_patch().set_facecolor(cmap(norm(c[ind["ind"][0]])))
        annot.get_bbox_patch().set_alpha(0.4)

    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            cont, ind = pts.contains(event)
            if cont:
                update_annot(ind)
                annot.set_visible(True)
                fig.canvas.draw_idle()
            else:
                if vis:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()

    fig.canvas.mpl_connect("key_press_event", accept)
    fig.canvas.mpl_connect("motion_notify_event", hover)

    plt.show()

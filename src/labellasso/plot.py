# SPDX-FileCopyrightText: 2023-present Henry Watkins <h.watkins@ucl.ac.uk>
#
# SPDX-License-Identifier: MIT

"""Plotting functionality for labellasso."""

from typing import List, Tuple

from bokeh.models import Button, ColumnDataSource, HoverTool, TextInput
from bokeh.palettes import Category10, Category20
from bokeh.plotting import figure
from bokeh.transform import factor_cmap


def create_scatter_plot(
    source: ColumnDataSource,
    unique_labels: List[str],
    title: str = "Scatter plot lasso labeller",
) -> Tuple[figure, HoverTool]:
    """
    Create a scatter plot for data labeling.

    Args:
        source: ColumnDataSource containing the data
        unique_labels: List of unique labels in the data
        title: Title for the plot

    Returns:
        Tuple containing the figure and hover tool
    """
    # Create figure with explicit tools
    p = figure(
        title=title,
        tools="pan,zoom_in,zoom_out,box_zoom,reset,save",  # Basic tools
    )

    # Add selection tools explicitly to ensure proper naming
    from bokeh.models import BoxSelectTool, LassoSelectTool

    p.add_tools(LassoSelectTool())
    p.add_tools(BoxSelectTool())

    # Set up color mapping for labels
    cmap = factor_cmap(
        "label",
        Category20[20] if len(unique_labels) > 10 else Category10[10],
        unique_labels,
    )

    # Add scatter points
    p.scatter(x="x", y="y", source=source, fill_alpha=0.6, size=10, color=cmap)

    # Create hover tool
    hover = HoverTool(tooltips=[("Name", "@name"), ("Label", "@label")])
    p.add_tools(hover)

    return p, hover


def create_input_widget(initial_value: str = "label name") -> TextInput:
    """
    Create a text input widget for label entry.

    Args:
        initial_value: Initial value for the text input

    Returns:
        TextInput widget
    """
    return TextInput(title="Input label name for selected points", value=initial_value)


def create_save_button() -> Button:
    """
    Create a button for saving labeled data.

    Returns:
        Button widget
    """
    return Button(label="save labels", button_type="success")


def update_plot_title(p: figure, unlabeled_percentage: float) -> None:
    """
    Update the plot title with labeling progress.

    Args:
        p: Figure to update
        unlabeled_percentage: Percentage of unlabeled data points

    Returns:
        None
    """
    labeled_percentage = 100 - unlabeled_percentage
    p.title.text = f"Scatter plot lasso labeller, labeled: {labeled_percentage:.1f}%"

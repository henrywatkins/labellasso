# SPDX-FileCopyrightText: 2023-present Henry Watkins <h.watkins@ucl.ac.uk>
#
# SPDX-License-Identifier: MIT

"""Tests for the plot module in the labellasso package."""

from bokeh.models import Button, ColumnDataSource, HoverTool, TextInput
from bokeh.plotting import figure

from labellasso.plot import (
    create_input_widget,
    create_save_button,
    create_scatter_plot,
    update_plot_title,
)


def test_create_scatter_plot(sample_column_source: ColumnDataSource) -> None:
    """Test creating a scatter plot."""
    # Create scatter plot
    unique_labels = ["label1", "label2", ""]
    p, hover = create_scatter_plot(sample_column_source, unique_labels)

    # Check results
    assert isinstance(p, figure)
    assert isinstance(hover, HoverTool)
    assert p.title.text == "Scatter plot lasso labeller"

    # Check that the plot has the expected tools
    # Check for tool types instead of names since names might not be reliable
    from bokeh.models import BoxSelectTool, LassoSelectTool

    tool_types = [type(tool) for tool in p.tools]
    assert LassoSelectTool in tool_types
    assert BoxSelectTool in tool_types

    # Check hover tooltips
    assert any("Name" in tip for tip in hover.tooltips)
    assert any("Label" in tip for tip in hover.tooltips)


def test_create_scatter_plot_with_custom_title(
    sample_column_source: ColumnDataSource,
) -> None:
    """Test creating a scatter plot with a custom title."""
    # Create scatter plot with custom title
    unique_labels = ["label1", "label2", ""]
    custom_title = "Custom Plot Title"
    p, hover = create_scatter_plot(sample_column_source, unique_labels, custom_title)

    # Check results
    assert p.title.text == custom_title


def test_create_input_widget() -> None:
    """Test creating a text input widget."""
    # Create input widget
    text_input = create_input_widget()

    # Check results
    assert isinstance(text_input, TextInput)
    assert text_input.value == "label name"
    assert "selected points" in text_input.title.lower()


def test_create_input_widget_with_custom_value() -> None:
    """Test creating a text input widget with a custom initial value."""
    # Create input widget with custom value
    custom_value = "custom label"
    text_input = create_input_widget(custom_value)

    # Check results
    assert text_input.value == custom_value


def test_create_save_button() -> None:
    """Test creating a save button."""
    # Create save button
    button = create_save_button()

    # Check results
    assert isinstance(button, Button)
    assert button.label.lower() == "save labels"
    assert button.button_type == "success"


def test_update_plot_title() -> None:
    """Test updating the plot title with labeling progress."""
    # Create figure
    p = figure(title="Initial Title")

    # Update title with different unlabeled percentages
    update_plot_title(p, 100.0)
    assert p.title.text == "Scatter plot lasso labeller, labeled: 0.0%"

    update_plot_title(p, 50.0)
    assert p.title.text == "Scatter plot lasso labeller, labeled: 50.0%"

    update_plot_title(p, 0.0)
    assert p.title.text == "Scatter plot lasso labeller, labeled: 100.0%"

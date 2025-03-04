# SPDX-FileCopyrightText: 2023-present Henry Watkins <h.watkins@ucl.ac.uk>
#
# SPDX-License-Identifier: MIT

"""
LabelLasso: A simple data-point labelling tool using scatterplot lasso.

This package provides a simple interactive tool for labeling data points in
a scatter plot using lasso selection. It is built on top of Bokeh for visualization
and interactive features.

Main components:
- CLI: Command-line interface for launching the tool
- Data: Functions for loading, validating, and saving data
- Plot: Functions for creating visualizations
- App: Bokeh application implementation
"""

from labellasso.__about__ import __version__

__all__ = ["__version__"]

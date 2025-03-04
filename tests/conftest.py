# SPDX-FileCopyrightText: 2023-present Henry Watkins <h.watkins@ucl.ac.uk>
#
# SPDX-License-Identifier: MIT

"""Pytest configuration and fixtures for LabelLasso tests."""

from pathlib import Path

import pandas as pd
import pytest
from bokeh.models import ColumnDataSource


@pytest.fixture
def sample_data_dir(tmp_path: Path) -> Path:
    """Create a directory with sample data files for testing."""
    # Create the directory
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    return data_dir


@pytest.fixture
def sample_csv_file(sample_data_dir: Path) -> Path:
    """Create a sample CSV file for testing."""
    # Create sample data
    data = {
        "name": ["point1", "point2", "point3", "point4", "point5"],
        "x": [1.0, 2.0, 3.0, 4.0, 5.0],
        "y": [5.0, 4.0, 3.0, 2.0, 1.0],
    }

    # Create DataFrame
    df = pd.DataFrame(data)

    # Save to CSV
    csv_path = sample_data_dir / "sample.csv"
    df.to_csv(csv_path, index=False)

    return csv_path


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Create a sample DataFrame for testing."""
    # Create sample data
    data = {
        "name": ["point1", "point2", "point3", "point4", "point5"],
        "x": [1.0, 2.0, 3.0, 4.0, 5.0],
        "y": [5.0, 4.0, 3.0, 2.0, 1.0],
        "label": ["", "", "label1", "", "label2"],
    }

    # Create DataFrame
    return pd.DataFrame(data)


@pytest.fixture
def sample_column_source(sample_df: pd.DataFrame) -> ColumnDataSource:
    """Create a sample ColumnDataSource for testing."""
    return ColumnDataSource(sample_df)

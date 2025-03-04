# SPDX-FileCopyrightText: 2023-present Henry Watkins <h.watkins@ucl.ac.uk>
#
# SPDX-License-Identifier: MIT

"""Tests for the data module in the labellasso package."""

from pathlib import Path

import pandas as pd
import pytest
from bokeh.models import ColumnDataSource

from labellasso.data import (
    DataValidationError,
    create_column_data_source,
    get_label_statistics,
    load_data,
    save_data,
    update_labels,
)


def test_load_data_with_valid_file(sample_csv_file: Path) -> None:
    """Test loading data from a valid CSV file."""
    # Load data
    df, output_path = load_data(sample_csv_file)

    # Check DataFrame structure
    assert isinstance(df, pd.DataFrame)
    assert "name" in df.columns
    assert "x" in df.columns
    assert "y" in df.columns
    assert "label" in df.columns
    assert len(df) == 5

    # Check that all labels are initialized as empty strings
    assert all(label == "" for label in df["label"])

    # Check output path
    assert output_path.name == "sample_labelled.csv"


def test_load_data_with_nonexistent_file() -> None:
    """Test loading data from a non-existent file."""
    with pytest.raises(FileNotFoundError):
        load_data(Path("/nonexistent/file.csv"))


def test_load_data_with_missing_columns(sample_data_dir: Path) -> None:
    """Test loading data with missing required columns."""
    # Create CSV with missing columns
    data = {"name": ["point1", "point2"], "x": [1.0, 2.0]}
    df = pd.DataFrame(data)
    csv_path = sample_data_dir / "missing_columns.csv"
    df.to_csv(csv_path, index=False)

    # Try to load data
    with pytest.raises(DataValidationError) as excinfo:
        load_data(csv_path)

    # Check error message
    assert "Missing required columns" in str(excinfo.value)
    assert "y" in str(excinfo.value)


def test_create_column_data_source(sample_df: pd.DataFrame) -> None:
    """Test creating a ColumnDataSource from a DataFrame."""
    # Create ColumnDataSource
    source = create_column_data_source(sample_df)

    # Check result
    assert isinstance(source, ColumnDataSource)
    assert "name" in source.data
    assert "x" in source.data
    assert "y" in source.data
    assert "label" in source.data
    assert len(source.data["name"]) == 5


def test_save_data(sample_df: pd.DataFrame, tmp_path: Path) -> None:
    """Test saving data to a CSV file."""
    # Define output path
    output_path = tmp_path / "output.csv"

    # Save data
    save_data(sample_df, output_path)

    # Check that the file exists
    assert output_path.exists()

    # Load the saved file and check its contents
    saved_df = pd.read_csv(output_path)

    # Replace NaN values with empty strings to match original DataFrame
    saved_df = saved_df.fillna("")

    # Compare DataFrames
    assert saved_df.equals(sample_df)


def test_get_label_statistics(sample_df: pd.DataFrame) -> None:
    """Test calculating label statistics."""
    # Get label statistics
    unlabeled_percentage, unique_labels = get_label_statistics(sample_df)

    # Check results
    assert unlabeled_percentage == 60.0  # 3 out of 5 are unlabeled
    assert unique_labels == {"label1", "label2"}


def test_update_labels(
    sample_df: pd.DataFrame, sample_column_source: ColumnDataSource
) -> None:
    """Test updating labels for selected data points."""
    # Update labels for points 0 and 1
    indices = [0, 1]
    updated_df = update_labels(sample_df, sample_column_source, indices, "new_label")

    # Check that the labels were updated
    assert updated_df.loc[0, "label"] == "new_label"
    assert updated_df.loc[1, "label"] == "new_label"
    assert updated_df.loc[2, "label"] == "label1"  # Unchanged
    assert updated_df.loc[3, "label"] == ""  # Unchanged
    assert updated_df.loc[4, "label"] == "label2"  # Unchanged

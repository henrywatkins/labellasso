# SPDX-FileCopyrightText: 2023-present Henry Watkins <h.watkins@ucl.ac.uk>
#
# SPDX-License-Identifier: MIT

"""Data loading, validation, and saving functionality for labellasso."""

from pathlib import Path
from typing import List, Set, Tuple

import pandas as pd
from bokeh.models import ColumnDataSource


class DataValidationError(Exception):
    """Exception raised when data validation fails."""

    pass


def load_data(input_file: Path) -> Tuple[pd.DataFrame, Path]:
    """
    Load data from a CSV file and validate its structure.

    Args:
        input_file: Path to the input CSV file

    Returns:
        Tuple containing the loaded DataFrame and the path for saving labeled data

    Raises:
        FileNotFoundError: If the input file doesn't exist
        DataValidationError: If the data doesn't have the required columns
        pd.errors.ParserError: If the CSV file cannot be parsed
    """
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    try:
        df = pd.read_csv(input_file, index_col=False)
    except pd.errors.ParserError as e:
        raise DataValidationError(f"Failed to parse CSV file: {e}")

    # Check for required columns
    required_columns = {"name", "x", "y"}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise DataValidationError(
            f"Missing required columns: {', '.join(missing_columns)}. "
            f"CSV file must contain 'name', 'x', and 'y' columns."
        )

    # Initialize label column if not present
    if "label" not in df.columns:
        df["label"] = ""
    else:
        # Ensure all NaN labels are converted to empty strings
        df.loc[df["label"].isna(), "label"] = ""

    # Generate output path
    filename = input_file.stem
    output_path = input_file.with_name(filename + "_labelled.csv")

    return df, output_path


def create_column_data_source(df: pd.DataFrame) -> ColumnDataSource:
    """
    Create a ColumnDataSource from a DataFrame.

    Args:
        df: DataFrame containing the data

    Returns:
        ColumnDataSource for Bokeh visualizations
    """
    return ColumnDataSource(df)


def save_data(df: pd.DataFrame, output_path: Path) -> None:
    """
    Save labeled data to a CSV file.

    Args:
        df: DataFrame containing the labeled data
        output_path: Path where the CSV file will be saved

    Raises:
        IOError: If the file cannot be saved
    """
    try:
        # Make a copy of the dataframe to avoid modifying the original
        df_copy = df.copy()

        # Ensure empty strings are preserved (not converted to NaN)
        df_copy.to_csv(output_path, index=False, na_rep="")
    except IOError as e:
        raise IOError(f"Failed to save labeled data to {output_path}: {e}")


def get_label_statistics(df: pd.DataFrame) -> Tuple[float, Set[str]]:
    """
    Calculate statistics about labeled data.

    Args:
        df: DataFrame containing the data

    Returns:
        Tuple containing:
        - Percentage of unlabeled data points
        - Set of unique labels
    """
    # Get percentage of unlabeled data points
    try:
        unlabeled = df["label"].value_counts(normalize=True).get("", 0) * 100
    except KeyError:
        unlabeled = 0

    # Get unique labels (excluding empty label)
    unique_labels = set(df["label"].unique().astype(str))
    if "" in unique_labels:
        unique_labels.remove("")

    return unlabeled, unique_labels


def update_labels(
    df: pd.DataFrame, source: ColumnDataSource, indices: List[int], label_value: str
) -> pd.DataFrame:
    """
    Update labels for selected data points.

    Args:
        df: DataFrame containing the data
        source: ColumnDataSource for the plot
        indices: Indices of selected data points
        label_value: Label to assign to selected data points

    Returns:
        Updated DataFrame
    """
    if not indices:
        return df

    df.loc[indices, "label"] = label_value
    source.data = ColumnDataSource.from_df(df)
    return df

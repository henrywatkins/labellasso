# LabelLasso

A simple interactive tool for labeling data points using scatterplot lasso selection.

## Features

- Interactive scatterplot visualization of data points
- Lasso and box selection tools for selecting points to label
- Automatic tracking of labeling progress
- Save labeled data to CSV with a single click
- Customizable column mappings

## Installation

```console
pip install labellasso
```

## Usage

Basic usage with default column names:

```console
labellasso data.csv
```

This will spin up a Bokeh server. Navigate to http://localhost:5006 in your browser to start labeling.

### Command Line Options

```console
$ labellasso --help
Usage: labellasso [OPTIONS] INPUT_FILE

  A simple data-point labelling tool using scatterplot lasso.

  INPUT_FILE should be a CSV file containing at least three columns:
  - A name column (default: 'name')
  - An x-coordinate column (default: 'x')
  - A y-coordinate column (default: 'y')

  The tool will create a new file with the suffix '_labelled' containing
  the original data plus a 'label' column with the assigned labels.

Options:
  --port INTEGER            Port to run the Bokeh server on.
  --address TEXT            Address to run the Bokeh server on.
  --x-column TEXT           Name of the column to use for x-coordinates.
  --y-column TEXT           Name of the column to use for y-coordinates.
  --name-column TEXT        Name of the column to use for point names.
  --version                 Show the version and exit.
  -h, --help                Show this message and exit.
```

### Input Data Format

The CSV file should have at least the following columns:
- `name`: Identifier for each data point
- `x`: X-coordinate for plotting
- `y`: Y-coordinate for plotting

Example input file:

```csv
name,x,y
point1,1.2,3.4
point2,2.3,4.5
point3,3.4,5.6
```

### Labeling Workflow

1. Load your data using the command line
2. Select points using lasso or box selection tools
3. Enter a label name in the text input
4. Selected points will be assigned the label
5. Click "save labels" to save the labeled data
6. The output will be saved as `<input-filename>_labelled.csv`

## TODO

Bugs on saving after labelling

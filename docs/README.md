# Developer Documentation for LabelLasso

## Architecture

LabelLasso follows a modular architecture with the following components:

- **CLI Module**: Command-line interface for the application
- **Data Module**: Data loading, validation, and manipulation
- **Plot Module**: Visualization and interactive plot components
- **App Module**: Bokeh application and server implementation

## Code Structure

```
labellasso/
├── __about__.py    # Version information
├── __init__.py     # Package initialization
├── __main__.py     # Entry point for python -m labellasso
├── app.py          # Bokeh application 
├── cli/            # Command-line interface
│   └── __init__.py # CLI implementation
├── data.py         # Data handling functions
└── plot.py         # Plotting functions
```

## Data Flow

1. User provides CSV file through CLI
2. Data is loaded and validated
3. Bokeh app is initialized with the data
4. User interacts with the visualization to label points
5. Labeled data is saved to a new CSV file

## Adding New Features

### Adding a New Visualization Type

1. Add a new function to `plot.py`
2. Update the app factory in `app.py`
3. Add an option to the CLI in `cli/__init__.py`

### Supporting a New Data Format

1. Add a new function to `data.py`
2. Update the data loading function in `data.py`
3. Add an option to the CLI in `cli/__init__.py`

## Testing

- Unit tests are provided for all modules
- Run tests with `pytest`
- Test coverage can be checked with `pytest --cov=labellasso`

## Development Environment

- Use `rye sync` to set up the development environment
- Run `ruff check .` for linting
- Run `ruff format .` for code formatting
- Run `mypy src` for type checking
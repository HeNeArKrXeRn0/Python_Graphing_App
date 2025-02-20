# Python Graphing Application

This is a Python-based application for graphing data from CSV files. The application uses Tkinter for the graphical user interface and Matplotlib for plotting graphs.

## Features

- Load CSV files and plot graphs based on selected columns.
- Customize graph titles, axis labels, and scaling factors.
- Normalize data on the X and Y axes.
- Set axis limits for both X and Y axes.
- Save graphs as PNG or SVG files.
- Reset the application to its initial state.

## Requirements

- Python 3.x
- Tkinter (usually included with Python)
- Matplotlib
- Pandas
- Chardet (for detecting file encoding)

## Installation

1. Clone the repository or download the source code.
2. Install the required Python packages using pip:

    ```sh
    pip install matplotlib pandas chardet
    ```

## Usage

1. Navigate to the directory containing the source code.
2. Run the application:

    ```sh
    python app/main.py
    ```

## File Structure

- [main.py]: Entry point of the application.
- [gui.py]: Contains the [GraphingApp] class which defines the GUI and its functionality.
- [file_manager.py]: Manages file selection and loading.
- [plot_manager.py]: Manages plotting and saving graphs.
- [graph_icon.ico]: Icon for the application window.

## Graphing Application

### GraphingApp Class

The [GraphingApp] class is responsible for creating the main application window and handling user interactions. It includes the following key components:

- **Folder Selection**: Allows users to select a folder containing CSV files.
- **Column Index Selection**: Allows users to specify the columns to be used for the X and Y data.
- **Separator Selection**: Allows users to select the separator used in the CSV files.
- **Axis Labels and Title**: Allows users to set custom labels for the X and Y axes and the graph title.
- **Scaling Factors**: Allows users to set scaling factors for the X and Y data.
- **Normalization**: Allows users to normalize the X and Y data.
- **Axis Limits**: Allows users to set limits for the X and Y axes.
- **Legend Labels**: Allows users to set custom labels for the graph legend.
- **Log Window**: Displays log messages and errors.

### Methods

- [create_widgets()]: Creates and arranges the GUI elements.
- [create_axis_inputs(parent)]: Creates input fields for axis labels, title, scaling factors, and axis limits.
- [create_legend_inputs()]: Creates input fields for legend labels.
- [create_buttons()]: Creates buttons for showing, saving, and resetting the graph.
- [select_folder()]: Opens a dialog to select a folder containing CSV files.
- [load_files()]: Loads the selected CSV files.
- [show_graph()]: Plots the graph based on the selected options.
- [save_graph()]: Saves the graph as a PNG or SVG file.
- [reset_app()]: Resets the application to its initial state.

## License

This project is licensed under the MIT License.

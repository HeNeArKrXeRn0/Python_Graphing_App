import os
import matplotlib.pyplot as plt
import pandas as pd
import chardet
import json
from settings import (
    COLOR_PALETTE, FIGURE_WIDTH, FIGURE_HEIGHT,
    DEFAULT_LINE_STYLE, DEFAULT_MARKER_STYLE, DEFAULT_LINE_WIDTH,
    DEFAULT_GRID_ENABLED, DEFAULT_PRESET_FILE
)

class PlotManager:
    def __init__(self):
        # Set the color palette for the plots
        # COLOR_PALETTE is defined in settings.py
        self.colors = COLOR_PALETTE
        self.current_fig = None
        self.current_ax = None

    def plot_graph(
            self,
            files,
            x_label,
            y_label,
            title,
            scale_x=1.0,
            scale_y=1.0,
            normalize_x=False,
            normalize_y=False,
            legend_labels=None,
            x_limits=None,
            use_x_limits=False,
            y_limits=None,
            use_y_limits=False,
            header_rows=1,
            x_col=0,
            y_col=1,
            separator=',',
            line_style=DEFAULT_LINE_STYLE,
            marker_style=DEFAULT_MARKER_STYLE,
            line_width=DEFAULT_LINE_WIDTH,
            grid_enabled=DEFAULT_GRID_ENABLED):
        """
        Plots a graph using data from one or more CSV files.
        All parameters set in the GUI are passed to this method.
        """
        if not files:
            raise ValueError("No files provided for plotting.")

        # Create the plot
        fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
        self.current_fig = fig
        self.current_ax = ax

        errors = []

        for ii, file in enumerate(files):
            x_data, y_data, error = self.read_csv_data(file, x_col, y_col, header_rows, separator)

            if error:
                errors.append(f"{os.path.basename(file)}: {error}")
                continue

            if normalize_x and x_data is not None and len(x_data) > 0:
                x_data = x_data / x_data.max()
            if normalize_y and y_data is not None and len(y_data) > 0:
                y_data = y_data / y_data.max()

            if x_data is not None:
                x_data = x_data * scale_x
            if y_data is not None:
                y_data = y_data * scale_y

            ax.plot(
                x_data, y_data,
                label=legend_labels[ii] if legend_labels and ii < len(legend_labels) else os.path.basename(file),
                color=self.colors[ii % len(self.colors)],
                linestyle=line_style,
                marker=marker_style,
                linewidth=line_width
            )

        # Customize plot
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(title)
        ax.grid(grid_enabled)

        # Apply axis limits if provided
        if use_x_limits:
            ax.set_xlim(x_limits)
        if use_y_limits:
            ax.set_ylim(y_limits)

        # Add legend if labels are provided
        if legend_labels or len(files) > 1:
            ax.legend(loc='best')

        # Enable zoom/pan tools
        fig.canvas.toolbar_visible = True
        fig.canvas.header_visible = False
        fig.canvas.footer_visible = False

        # Store reference for later use
        self.current_fig = fig
        self.current_ax = ax

        # Show the plot
        plt.show()

        return errors

    def read_csv_data(self, file_path: str, x_col: int, y_col: int, metadata_rows: int, sep_type: str):
        """
        Reads CSV data from a file and extracts the specified columns.

        Args:
            file_path (str): Path to the CSV file.
            x_col (int): Index of the column to be used as X data.
            y_col (int): Index of the column to be used as Y data.
            metadata_rows (int): Number of header rows in the CSV file.
            sep_type (str): Separator used in the CSV file.

        Returns:
            tuple: (x_data, y_data, error_message)
                   x_data and y_data are pandas Series or None
                   error_message is None if successful, otherwise a string
        """
        try:
            # Detect file encoding
            with open(file_path, 'rb') as file:
                raw_data = file.read()
                result = chardet.detect(raw_data)
                encoding_detected = result['encoding'] or 'utf-8'

            # Read the CSV file with specified header and skiprows
            data = pd.read_csv(
                file_path,
                sep=sep_type,
                encoding=encoding_detected,
                skiprows=metadata_rows,
                engine='python',
                header=0)

            # Extract X and Y data
            # Check if the data in specified columns is numeric (instead of text)
            if pd.api.types.is_numeric_dtype(data.iloc[:, x_col]):
                x_data = data.iloc[:, x_col]
            else:
                # If the data is not numeric, use the index as X data
                x_data = data.index

            if pd.api.types.is_numeric_dtype(data.iloc[:, y_col]):
                y_data = data.iloc[:, y_col]
            else:
                # If the data is not numeric, return an error
                return None, None, f"Column {y_col} is not numeric."

            return x_data, y_data, None

        except FileNotFoundError:
            return None, None, f"File not found: {os.path.basename(file_path)}"
        except pd.errors.EmptyDataError:
            return None, None, "No data found in file."
        except pd.errors.ParserError as e:
            return None, None, f"Parser error: {str(e)}"
        except UnicodeDecodeError as e:
            return None, None, f"Encoding error: {str(e)}"
        except IndexError:
            return None, None, "Column index out of range."
        except Exception as e:
            return None, None, f"Error: {str(e)}"

    def save_graph(self, file_path):
        """
        Saves the currently displayed graph to a file.

        Args:
            file_path (str): Path to save the graph (e.g., .png, .svg).
        """
        if not file_path:
            raise ValueError("File path is required to save the graph.")

        try:
            plt.savefig(file_path)
        except Exception as e:
            raise IOError(f"Failed to save graph: {e}")

    def close_graph(self):
        """Closes all open matplotlib figures."""
        plt.close('all')
        self.current_fig = None
        self.current_ax = None

    def save_preset(self, preset_name, settings_dict):
        """
        Save graph settings to a JSON preset file.

        Args:
            preset_name (str): Name for the preset
            settings_dict (dict): Dictionary of settings to save
        """
        try:
            # Load existing presets or create new dict
            if os.path.exists(DEFAULT_PRESET_FILE):
                with open(DEFAULT_PRESET_FILE, 'r') as f:
                    presets = json.load(f)
            else:
                presets = {}

            # Add new preset
            presets[preset_name] = settings_dict

            # Save presets
            with open(DEFAULT_PRESET_FILE, 'w') as f:
                json.dump(presets, f, indent=2)

            return True, f"Preset '{preset_name}' saved."

        except Exception as e:
            return False, f"Failed to save preset: {str(e)}"

    def load_preset(self, preset_name):
        """
        Load graph settings from a preset file.

        Args:
            preset_name (str): Name of the preset to load

        Returns:
            tuple: (success, settings_dict or error_message)
        """
        try:
            if not os.path.exists(DEFAULT_PRESET_FILE):
                return False, "No presets found."

            with open(DEFAULT_PRESET_FILE, 'r') as f:
                presets = json.load(f)

            if preset_name not in presets:
                return False, f"Preset '{preset_name}' not found."

            return True, presets[preset_name]

        except Exception as e:
            return False, f"Failed to load preset: {str(e)}"

    def list_presets(self):
        """
        List all available presets.

        Returns:
            list: List of preset names
        """
        try:
            if not os.path.exists(DEFAULT_PRESET_FILE):
                return []

            with open(DEFAULT_PRESET_FILE, 'r') as f:
                presets = json.load(f)

            return list(presets.keys())

        except Exception:
            return []
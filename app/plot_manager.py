import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import chardet
import json
from matplotlib.ticker import LogLocator, LogFormatterMathtext, NullFormatter
from settings import (
    COLOR_PALETTE, FIGURE_WIDTH, FIGURE_HEIGHT,
    DEFAULT_LINE_STYLE, DEFAULT_MARKER_STYLE, DEFAULT_LINE_WIDTH,
    DEFAULT_GRID_ENABLED, DEFAULT_PRESET_FILE, DEFAULT_HEADER_ROWS,
    DEFAULT_LOG_X, DEFAULT_LOG_Y
)

class PlotManager:
    def __init__(self):
        # Set the color palette for the plots
        # COLOR_PALETTE is defined in settings.py
        self.colors = COLOR_PALETTE
        self.current_fig = None
        self.current_ax = None

    @staticmethod
    def filter_nonpositive_pairs(x_data, y_data, log_x, log_y):
        """
        Drop the points that a log-scaled axis physically cannot display.

        A base-10 log axis cannot render a value <= 0. X and Y are paired, so a
        point dropped for one axis takes the other axis's value with it. The
        filter runs on the RAW column values, which keeps the reported count
        and minimum a statement about the file rather than about whatever
        Normalize/Scale are about to be applied on top.

        Args:
            x_data (array-like): X values (pandas Series, index, or ndarray).
            y_data (array-like): Y values.
            log_x (bool): True when the X axis is log-scaled.
            log_y (bool): True when the Y axis is log-scaled.

        Returns:
            tuple: (x_kept, y_kept, warnings). The arrays are numpy ndarrays,
                   or the untouched inputs when neither axis is logarithmic.
                   warnings is a list of filename-free strings, X before Y.
                   NaN is deliberately kept: Matplotlib already draws it as a
                   gap in the line.
        """
        warnings = []
        if not log_x and not log_y:
            return x_data, y_data, warnings

        x = np.asarray(x_data, dtype=float)
        y = np.asarray(y_data, dtype=float)

        bad_x = (x <= 0) if log_x else np.zeros(x.shape, dtype=bool)
        bad_y = (y <= 0) if log_y else np.zeros(y.shape, dtype=bool)

        total = len(y)
        if log_x and bad_x.any():
            warnings.append(
                f"{int(bad_x.sum())} of {total} X values <= 0 omitted "
                f"(log X); min was {x[bad_x].min():.2e}")
        if log_y and bad_y.any():
            warnings.append(
                f"{int(bad_y.sum())} of {total} Y values <= 0 omitted "
                f"(log Y); min was {y[bad_y].min():.2e}")

        keep = ~(bad_x | bad_y)
        return x[keep], y[keep], warnings

    @staticmethod
    def apply_log_axes(ax, log_x, log_y, grid_enabled=False):
        """
        Switch the requested axes to a base-10 logarithmic scale.

        Matplotlib's default minor formatter labels every minor tick, which is
        unreadable over several decades, so the minor ticks are explicitly
        silenced. Faint minor gridlines accompany the grid when it is on; they
        draw nothing on a linear axis, whose minor locator is a NullLocator.

        Args:
            ax (matplotlib.axes.Axes): the axes to configure.
            log_x (bool): True to log-scale the X axis.
            log_y (bool): True to log-scale the Y axis.
            grid_enabled (bool): True to add faint minor gridlines.
        """
        if log_x:
            ax.set_xscale('log', base=10)
            ax.xaxis.set_major_locator(LogLocator(base=10))
            ax.xaxis.set_major_formatter(LogFormatterMathtext(base=10))
            ax.xaxis.set_minor_locator(LogLocator(base=10, subs=np.arange(2, 10) * 0.1))
            ax.xaxis.set_minor_formatter(NullFormatter())

        if log_y:
            ax.set_yscale('log', base=10)
            ax.yaxis.set_major_locator(LogLocator(base=10))
            ax.yaxis.set_major_formatter(LogFormatterMathtext(base=10))
            ax.yaxis.set_minor_locator(LogLocator(base=10, subs=np.arange(2, 10) * 0.1))
            ax.yaxis.set_minor_formatter(NullFormatter())

        if grid_enabled and (log_x or log_y):
            ax.grid(which='minor', visible=True, linestyle=':', alpha=0.4)

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
            header_rows=DEFAULT_HEADER_ROWS,
            x_col=0,
            y_col=1,
            separator=',',
            line_style=DEFAULT_LINE_STYLE,
            marker_style=DEFAULT_MARKER_STYLE,
            line_width=DEFAULT_LINE_WIDTH,
            grid_enabled=DEFAULT_GRID_ENABLED,
            log_x=DEFAULT_LOG_X,
            log_y=DEFAULT_LOG_Y):
        """
        Plots a graph using data from one or more CSV files.
        All parameters set in the GUI are passed to this method.

        log_x/log_y switch the axes to a base-10 logarithmic scale; points
        whose log-scaled value is <= 0 are dropped and reported in the
        returned warnings.

        Returns:
            list: warning strings, one per problem encountered. A bare
                  "<file>: <reason>" line means that file could not be
                  plotted; a "[WARN] <file>: ..." line means some of its
                  points were omitted from a log axis.
        """
        if not files:
            raise ValueError("No files provided for plotting.")

        # Create the plot
        fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
        self.current_fig = fig
        self.current_ax = ax

        # Log scales are applied before any limits so that autoscale and
        # set_xlim/set_ylim both operate against the final scale
        self.apply_log_axes(ax, log_x, log_y, grid_enabled)

        errors = []

        for ii, file in enumerate(files):
            x_data, y_data, error = self.read_csv_data(file, x_col, y_col, header_rows, separator)

            if error:
                errors.append(f"{os.path.basename(file)}: {error}")
                continue

            # A log axis physically cannot draw a value <= 0. Drop those points
            # and report exactly how many, so the curve never silently loses its
            # sub-threshold region. '[WARN]' marks an omission; a bare line
            # above means the whole file failed.
            x_data, y_data, drop_warnings = self.filter_nonpositive_pairs(
                x_data, y_data, log_x, log_y)
            errors.extend(
                f"[WARN] {os.path.basename(file)}: {warning}"
                for warning in drop_warnings)

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

    def has_graph(self):
        """
        Returns True if a graph is currently displayed.

        Also returns False if the graph window was closed by the user, since
        Matplotlib then discards the figure and saving would produce a blank image.
        """
        return (
            self.current_fig is not None
            and plt.fignum_exists(self.current_fig.number)
        )

    def save_graph(self, file_path):
        """
        Saves the currently displayed graph to a file.

        Args:
            file_path (str): Path to save the graph (e.g., .png, .svg).

        Raises:
            ValueError: If no graph is currently displayed.
        """
        if not file_path:
            raise ValueError("File path is required to save the graph.")

        if not self.has_graph():
            raise ValueError("No graph is currently displayed. Click 'Show Graph' first.")

        try:
            # Save the tracked figure explicitly: plt.savefig() would fall back
            # to a blank figure if the displayed one was discarded
            self.current_fig.savefig(file_path)
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
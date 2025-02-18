import os
import matplotlib.pyplot as plt
import pandas as pd
import chardet
from settings import COLOR_PALETTE, FIGURE_WIDTH, FIGURE_HEIGHT

class PlotManager:
    def __init__(self):
        self.colors = COLOR_PALETTE

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
            separator=','):
        """
        Plots a graph using data from one or more CSV files.
        """
        if not files:
            raise ValueError("No files provided for plotting.")

        # Create the plot
        fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))

        for ii, file in enumerate(files):
            try:
                x_data, y_data = self.read_csv_data(file, x_col, y_col, header_rows, separator)

                if normalize_x:
                    x_data /= x_data.max()
                if normalize_y:
                    y_data /= y_data.max()

                x_data *= scale_x
                y_data *= scale_y

                ax.plot(
                    x_data, y_data,
                    label=legend_labels[ii] if legend_labels and ii < len(legend_labels) else os.path.basename(file),
                    color=self.colors[ii % len(self.colors)]
                )

            except Exception as e:
                print(f"Error processing file {file}: {e}")

        # Customize plot
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(title)
        ax.grid(True)

        # Apply axis limits if provided
        if use_x_limits:
            ax.set_xlim(x_limits)
        if use_y_limits:
            ax.set_ylim(y_limits)

        # Add legend if labels are provided
        if legend_labels or len(files) > 1:
            ax.legend(loc='best')

        # Show the plot
        plt.show()

    def read_csv_data(self, file_path, x_col, y_col, metadata_rows, sep_type):
        """
        Reads CSV data from a file and extracts the specified columns.

        Args:
            file_path (str): Path to the CSV file.
            x_col (int): Index of the column to be used as X data.
            y_col (int): Index of the column to be used as Y data.
            header_rows (int): Number of header rows in the CSV file.
            sep_type (str): Separator used in the CSV file.

        Returns:
            tuple: Two pandas Series objects containing the X and Y data.
        """
        try:
            # Detect file encoding
            with open(file_path, 'rb') as file:
                raw_data = file.read()
                result = chardet.detect(raw_data)
                encoding_detected = result['encoding']

            # Read the CSV file with specified header and skiprows
            data = pd.read_csv(
                file_path, 
                sep=sep_type, 
                encoding=encoding_detected, 
                skiprows=metadata_rows, 
                engine='python',
                header=0)
            
            # Debug prints to verify the content of the data
            # print(f"Data loaded from {file_path}")
            # print(f"header_rows = {metadata_rows}")
            # print(data.head())

            # Extract X and Y data
            if pd.api.types.is_numeric_dtype(data.iloc[:, x_col]):
                x_data = data.iloc[:, x_col]
                # Debug prints to verify the content of x_data
                # print(f"x_data (first 5 rows):\n{x_data.head()}")
            else:
                x_data = data.index
            
            if pd.api.types.is_numeric_dtype(data.iloc[:, y_col]):
                y_data = data.iloc[:, y_col]
            else:
                raise ValueError(f"Column {y_col} is not numeric.")

            # Debug prints to verify the content of x_data and y_data
            # print(f"y_data (first 5 rows):\n{y_data.head()}")

            return x_data, y_data

        except FileNotFoundError:
            print(f"Error: File {file_path} not found.")
        except pd.errors.EmptyDataError:
            print(f"Error: No data found in file {file_path}.")
        except pd.errors.ParserError as e:
            print(f"Error parsing CSV file {file_path}: {e}")
        except UnicodeDecodeError as e:
            print(f"Error processing file {file_path}: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

        return None, None

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
            print(f"Graph saved to {file_path}")
        except Exception as e:
            raise IOError(f"Failed to save graph: {e}")

    def close_graph(self):
        """Closes all open matplotlib figures."""
        plt.close('all')
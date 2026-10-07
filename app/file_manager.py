import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, Text, Scrollbar
import chardet
from settings import MAX_FILES, SEPARATORS_DICT, DEFAULT_HEADER_ROWS

class FileManager:
    def __init__(self):
        self.max_files = MAX_FILES
        self.folder_path = None
        self.files = []

    def select_folder(self):
        """
        Opens a dialog to select a folder and updates the folder path.
        """
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path = folder_selected
        return self.folder_path

    def load_files(self):
        """
        Opens a file dialog to select CSV files from the selected folder.
        Returns:
            List of selected file paths.
        """
        if not self.folder_path:
            messagebox.showerror("Error", "Please select a folder first.")
            return []

        file_types = [("CSV files", "*.csv")]
        files_selected = filedialog.askopenfilenames(initialdir=self.folder_path, filetypes=file_types)

        if files_selected:
            if len(files_selected) > self.max_files:
                messagebox.showerror("Error", f"You can only load up to {self.max_files} files.")
                return []

            self.files = sorted(files_selected)
        return self.files

    def log_files(self):
        """
        Prepares a log message of the loaded files.
        Returns:
            str: Log message for the files.
        """
        if not self.files:
            return "No files loaded."

        log_message = "Loaded Files:\n"
        log_message += "\n".join(self.files)
        return log_message

    def preview_file(self, file_path, header_rows=DEFAULT_HEADER_ROWS, separator=',', num_rows=10):
        """
        Preview the first few rows of a CSV file.

        Args:
            file_path: Path to the CSV file
            header_rows: Number of header rows to skip
            separator: CSV separator character
            num_rows: Number of data rows to preview

        Returns:
            tuple: (DataFrame with preview data, column names/indices, detected separator)
        """
        try:
            # Detect file encoding
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding'] or 'utf-8'

            # Read the CSV file
            data = pd.read_csv(
                file_path,
                sep=separator,
                encoding=encoding,
                skiprows=header_rows,
                engine='python',
                header=0,
                nrows=num_rows
            )

            # Generate column info
            column_info = []
            for i, col in enumerate(data.columns):
                column_info.append(f"{i}: {col}")

            return data, column_info, separator

        except Exception as e:
            return None, [], str(e)

    def detect_separator(self, file_path, header_rows=DEFAULT_HEADER_ROWS):
        """
        Auto-detect the best separator for a CSV file by testing common separators.

        Args:
            file_path: Path to the CSV file
            header_rows: Number of header rows to skip

        Returns:
            tuple: (best_separator, detected_columns)
        """
        # Try each separator and see which gives the most columns
        best_separator = ','
        max_columns = 0

        for sep_name, sep_char in SEPARATORS_DICT.items():
            try:
                # Detect encoding
                with open(file_path, 'rb') as f:
                    raw_data = f.read()
                    result = chardet.detect(raw_data)
                    encoding = result['encoding'] or 'utf-8'

                # Try to read with this separator
                data = pd.read_csv(
                    file_path,
                    sep=sep_char,
                    encoding=encoding,
                    skiprows=header_rows,
                    engine='python',
                    header=0,
                    nrows=5
                )

                # Count columns
                num_columns = len(data.columns)
                if num_columns > max_columns and num_columns > 1:
                    max_columns = num_columns
                    best_separator = sep_char

            except Exception:
                continue

        # Generate column info for best separator
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding'] or 'utf-8'

            data = pd.read_csv(
                file_path,
                sep=best_separator,
                encoding=encoding,
                skiprows=header_rows,
                engine='python',
                header=0,
                nrows=5
            )
            column_info = [f"{i}: {col}" for i, col in enumerate(data.columns)]
        except Exception:
            column_info = []

        return best_separator, column_info

    def show_preview_dialog(self, file_path, header_rows=DEFAULT_HEADER_ROWS, separator=','):
        """
        Show a preview dialog with the file data.

        Args:
            file_path: Path to the CSV file
            header_rows: Number of header rows to skip
            separator: CSV separator character
        """
        data, column_info, used_sep = self.preview_file(file_path, header_rows, separator)

        if data is None:
            messagebox.showerror("Error", f"Failed to preview file: {column_info}")
            return

        # Create preview window
        preview_window = Toplevel()
        preview_window.title(f"Data Preview: {os.path.basename(file_path)}")
        preview_window.geometry("800x500")

        # Column info text
        col_frame = tk.Frame(preview_window)
        col_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(col_frame, text="Columns:").pack(anchor=tk.W)
        for col in column_info:
            tk.Label(col_frame, text=f"  {col}", anchor=tk.W).pack(anchor=tk.W)

        # Separator info
        tk.Label(col_frame, text=f"Detected Separator: '{used_sep}'", anchor=tk.W).pack(anchor=tk.W)

        # Data preview in a scrollable text widget
        text_frame = tk.Frame(preview_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        scrollbar = Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        preview_text = Text(text_frame, wrap=tk.NONE, yscrollcommand=scrollbar.set)
        preview_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=preview_text.yview)

        # Add column headers
        preview_text.insert(tk.END, "\t".join(str(col) for col in data.columns) + "\n")
        preview_text.insert(tk.END, "-" * 80 + "\n")

        # Add data rows
        for _, row in data.iterrows():
            preview_text.insert(tk.END, "\t".join(str(val) for val in row) + "\n")

        preview_text.config(state=tk.DISABLED)

        # Close button
        tk.Button(preview_window, text="Close", command=preview_window.destroy).pack(pady=10)

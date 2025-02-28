import os
import pandas as pd
from tkinter import filedialog, messagebox
from settings import MAX_FILES

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

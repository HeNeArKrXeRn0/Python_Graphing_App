import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from file_manager import FileManager
from plot_manager import PlotManager
import os
from settings import (
    MAX_FILES, DEFAULT_X_LABEL, DEFAULT_Y_LABEL, DEFAULT_TITLE,
    SEPARATORS_DICT, LINE_STYLES, MARKER_STYLES,
    DEFAULT_LINE_STYLE, DEFAULT_MARKER_STYLE,
    DEFAULT_LINE_STYLE_NAME, DEFAULT_MARKER_STYLE_NAME,
    DEFAULT_LINE_WIDTH, DEFAULT_GRID_ENABLED, DEFAULT_HEADER_ROWS
)

class GraphingApp:
    def __init__(self, root):
        # Setup the GUI window
        self.root = root
        self.root.title("Python Graphing Application")
        self.root.geometry("900x900")
        self.root.resizable(False, True)
        # Set the icon
        icon_path = os.path.join(os.path.dirname(__file__), '../assets/graph_icon.ico')
        self.root.iconbitmap(icon_path)

        # Managers for file and plot operations
        self.file_manager = FileManager()
        self.plot_manager = PlotManager()

        # Tkinter Variables
        self.select_folder_var = tk.StringVar(value="")
        self.x_label = tk.StringVar(value=DEFAULT_X_LABEL)
        self.y_label = tk.StringVar(value=DEFAULT_Y_LABEL)
        self.title = tk.StringVar(value=DEFAULT_TITLE)
        self.scale_factor_x = tk.DoubleVar(value=1.0)
        self.scale_factor_y = tk.DoubleVar(value=1.0)
        self.normalize_x = tk.BooleanVar()
        self.normalize_y = tk.BooleanVar()
        self.header_rows = tk.IntVar(value=DEFAULT_HEADER_ROWS)
        self.x_column_index = tk.IntVar(value=0)
        self.y_column_index = tk.IntVar(value=1)

        # Separator selection variables
        # separator_name is the display name in the GUI, separator_str is the actual separator
        self.separator_name = tk.StringVar()
        self.separator_name.set("Comma")
        self.separator_str = tk.StringVar()
        self.separator_str.set(",")

        # X/Y limits
        self.x_min = tk.StringVar(value="")
        self.x_max = tk.StringVar(value="")
        self.use_x_limits = tk.BooleanVar()
        self.y_min = tk.StringVar(value="")
        self.y_max = tk.StringVar(value="")
        self.use_y_limits = tk.BooleanVar()

        # Legend labels
        self.legend_entries = []

        # Column dropdown variables
        self.x_column_var = tk.StringVar(value="Auto (0)")
        self.y_column_var = tk.StringVar(value="Auto (1)")
        self.column_options = []

        # Customization variables (hold GUI display names, e.g. "Solid" / "None")
        self.line_style_var = tk.StringVar(value=DEFAULT_LINE_STYLE_NAME)
        self.marker_style_var = tk.StringVar(value=DEFAULT_MARKER_STYLE_NAME)
        self.line_width_var = tk.DoubleVar(value=DEFAULT_LINE_WIDTH)
        self.grid_enabled_var = tk.BooleanVar(value=DEFAULT_GRID_ENABLED)

        # Status variable
        self.status_var = tk.StringVar(value="Ready")

        # Create UI Elements defined below
        self.create_widgets()

    def create_widgets(self):
        # Status bar
        status_frame = tk.Frame(self.root)
        status_frame.pack(fill=tk.X, padx=5, pady=2)
        status_label = tk.Label(status_frame, text="Status:", font=('Arial', 9, 'bold'))
        status_label.pack(side=tk.LEFT)
        status_bar = tk.Label(status_frame, textvariable=self.status_var, fg="green", anchor=tk.W)
        status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Folder selection
        folder_frame = tk.Frame(self.root)
        folder_frame.pack(pady=5)
        folder_label = tk.Label(folder_frame, text="Select Folder:")
        folder_label.pack(side=tk.LEFT)
        folder_entry = tk.Entry(folder_frame, textvariable=self.select_folder_var, width=80)
        folder_entry.pack(side=tk.LEFT, padx=5)

        # Browse button, to select folder from a dialog
        browse_button = tk.Button(folder_frame, text="Browse", command=self.select_folder)
        browse_button.pack(side=tk.LEFT)

        # Load files button
        load_button = tk.Button(folder_frame, text="Load Files", command=self.load_files)
        load_button.pack(side=tk.LEFT)

        # Preview button
        preview_button = tk.Button(folder_frame, text="Preview Data", command=self.preview_data)
        preview_button.pack(side=tk.LEFT, padx=5)

        # X and Y column index selection FRAME
        column_frame = tk.Frame(self.root)
        column_frame.pack(pady=2)

        # Header rows entry
        header_label = tk.Label(column_frame, text="Number of Header Rows:")
        header_label.grid(row=0, column=0, padx=5, pady=3)
        header_entry = tk.Entry(column_frame, textvariable=self.header_rows, width=5)
        header_entry.grid(row=0, column=1, padx=5, pady=3)

        # Separator selection
        def set_sep_variable(value):
            self.separator_str.set(SEPARATORS_DICT[self.separator_name.get()])

        # Separator selection dropdown menu
        separator_label = tk.Label(column_frame, text="Separator:")
        separator_label.grid(row=0, column=2, padx=5, pady=3)
        separator_menu = tk.OptionMenu(column_frame, self.separator_name, *SEPARATORS_DICT.keys(), command=set_sep_variable)
        separator_menu.grid(row=0, column=3, padx=5, pady=3)

        # Auto-detect separator button
        detect_sep_button = tk.Button(column_frame, text="Auto-Detect Separator", command=self.detect_separator)
        detect_sep_button.grid(row=0, column=4, padx=5, pady=3)

        # X and Y column selection with dropdowns
        x_column_label = tk.Label(column_frame, text="X Column:")
        x_column_label.grid(row=1, column=0, padx=5, pady=5)
        self.x_column_dropdown = tk.OptionMenu(column_frame, self.x_column_var, *["Auto (0)"], command=self.on_x_column_change)
        self.x_column_dropdown.grid(row=1, column=1, padx=5, pady=5)

        y_column_label = tk.Label(column_frame, text="Y Column:")
        y_column_label.grid(row=1, column=2, padx=5, pady=5)
        self.y_column_dropdown = tk.OptionMenu(column_frame, self.y_column_var, *["Auto (1)"], command=self.on_y_column_change)
        self.y_column_dropdown.grid(row=1, column=3, padx=5, pady=5)

        # Log window
        log_frame = tk.Frame(self.root)
        log_frame.pack(pady=10)

        log_label = tk.Label(log_frame, text="Log:")
        log_label.pack(anchor=tk.W)

        self.log_text = tk.Text(log_frame, height=10, width=100)
        self.log_text.pack()

        # Axis labels and title
        axis_frame = tk.Frame(self.root)
        axis_frame.pack(pady=10)

        # Axis inputs created in a separate function
        self.create_axis_inputs(axis_frame)
        # Legend inputs created in a separate function
        self.create_legend_inputs()
        # Customization options
        self.create_customization_inputs()
        # Buttons created in a separate function
        self.create_buttons()

    def create_customization_inputs(self):
        """
        Create the input fields for graph customization options
        """
        custom_frame = tk.Frame(self.root)
        custom_frame.pack(pady=10)

        # Line style
        line_style_label = tk.Label(custom_frame, text="Line Style:")
        line_style_label.grid(row=0, column=0, padx=5, pady=3)
        self.line_style_dropdown = tk.OptionMenu(custom_frame, self.line_style_var, *LINE_STYLES.keys(), command=lambda v: None)
        self.line_style_dropdown.grid(row=0, column=1, padx=5, pady=3)

        # Marker style
        marker_style_label = tk.Label(custom_frame, text="Marker Style:")
        marker_style_label.grid(row=0, column=2, padx=5, pady=3)
        self.marker_style_dropdown = tk.OptionMenu(custom_frame, self.marker_style_var, *MARKER_STYLES.keys(), command=lambda v: None)
        self.marker_style_dropdown.grid(row=0, column=3, padx=5, pady=3)

        # Line width
        line_width_label = tk.Label(custom_frame, text="Line Width:")
        line_width_label.grid(row=1, column=0, padx=5, pady=3)
        line_width_entry = tk.Entry(custom_frame, textvariable=self.line_width_var, width=5)
        line_width_entry.grid(row=1, column=1, padx=5, pady=3)

        # Grid toggle
        grid_check = tk.Checkbutton(custom_frame, text="Enable Grid", variable=self.grid_enabled_var)
        grid_check.grid(row=1, column=2, padx=5, pady=3, columnspan=2)

        # Preset buttons
        preset_frame = tk.Frame(self.root)
        preset_frame.pack(pady=5)

        save_preset_button = tk.Button(preset_frame, text="Save Preset", command=self.save_preset)
        save_preset_button.pack(side=tk.LEFT, padx=5)

        load_preset_button = tk.Button(preset_frame, text="Load Preset", command=self.load_preset)
        load_preset_button.pack(side=tk.LEFT, padx=5)

    @staticmethod
    def style_to_symbol(mapping, value, default_symbol):
        """
        Convert a style display name (e.g. "Dashed") to its Matplotlib symbol.
        Accepts a raw symbol as-is (backward compat with old presets).
        """
        if value in mapping:  # display name
            return mapping[value]
        if value in mapping.values():  # already a Matplotlib symbol
            return value
        return default_symbol

    @staticmethod
    def symbol_to_name(mapping, value, default_name):
        """
        Convert a Matplotlib symbol (e.g. "--") to its display name.
        Accepts a display name as-is (new preset format).
        """
        if value in mapping:  # already a display name
            return value
        inverse = {symbol: name for name, symbol in mapping.items()}
        return inverse.get(value, default_name)

    def create_axis_inputs(self, parent):
        """
        Create the input fields for axis labels, title, scale factors, and normalization
        parent: the parent frame to pack the input fields
        """
        x_label_label = tk.Label(parent, text="X-axis Label:")
        x_label_label.grid(row=0, column=0, padx=5, pady=5)
        x_label_entry = tk.Entry(parent, textvariable=self.x_label)
        x_label_entry.grid(row=0, column=1, padx=5, pady=5)

        y_label_label = tk.Label(parent, text="Y-axis Label:")
        y_label_label.grid(row=1, column=0, padx=5, pady=5)
        y_label_entry = tk.Entry(parent, textvariable=self.y_label)
        y_label_entry.grid(row=1, column=1, padx=5, pady=5)

        title_label = tk.Label(parent, text="Chart Title:")
        title_label.grid(row=2, column=0, padx=5, pady=5)
        title_entry = tk.Entry(parent, textvariable=self.title)
        title_entry.grid(row=2, column=1, padx=5, pady=5)

        scale_x_label = tk.Label(parent, text="Scale Factor X:")
        scale_x_label.grid(row=0, column=2, padx=5, pady=5)
        scale_x_entry = tk.Entry(parent, textvariable=self.scale_factor_x)
        scale_x_entry.grid(row=0, column=3, padx=5, pady=5)

        scale_y_label = tk.Label(parent, text="Scale Factor Y:")
        scale_y_label.grid(row=1, column=2, padx=5, pady=5)
        scale_y_entry = tk.Entry(parent, textvariable=self.scale_factor_y)
        scale_y_entry.grid(row=1, column=3, padx=5, pady=5)

        normalize_x_check = tk.Checkbutton(parent, text="Normalize X", variable=self.normalize_x)
        normalize_x_check.grid(row=0, column=4, columnspan=4)

        normalize_y_check = tk.Checkbutton(parent, text="Normalize Y", variable=self.normalize_y)
        normalize_y_check.grid(row=1, column=4, columnspan=2)

        # Axis Limits
        x_min_label = tk.Label(parent, text="X Min:")
        x_min_label.grid(row=3, column=0, padx=5, pady=5)
        x_min_entry = tk.Entry(parent, textvariable=self.x_min)
        x_min_entry.grid(row=3, column=1, padx=5, pady=5)

        x_max_label = tk.Label(parent, text="X Max:")
        x_max_label.grid(row=3, column=2, padx=5, pady=5)
        x_max_entry = tk.Entry(parent, textvariable=self.x_max)
        x_max_entry.grid(row=3, column=3, padx=5, pady=5)

        # Add checkbox for X Limits
        use_x_limits_check = tk.Checkbutton(parent, text="Use X Limits", variable=self.use_x_limits)
        use_x_limits_check.grid(row=3, column=4, columnspan=2)

        y_min_label = tk.Label(parent, text="Y Min:")
        y_min_label.grid(row=4, column=0, padx=5, pady=5)
        y_min_entry = tk.Entry(parent, textvariable=self.y_min)
        y_min_entry.grid(row=4, column=1, padx=5, pady=5)

        y_max_label = tk.Label(parent, text="Y Max:")
        y_max_label.grid(row=4, column=2, padx=5, pady=5)
        y_max_entry = tk.Entry(parent, textvariable=self.y_max)
        y_max_entry.grid(row=4, column=3, padx=5, pady=5)

        # Add checkbox for Y Limits
        use_y_limits_check = tk.Checkbutton(parent, text="Use Y Limits", variable=self.use_y_limits)
        use_y_limits_check.grid(row=4, column=4, columnspan=2)
        
    def create_legend_inputs(self):
        # Legend section title, packed in root
        legend_section_title = tk.Label(self.root, text="Legend Labels")
        legend_section_title.pack(pady=5)
        # Legend labels input frame, packed in root
        legend_input_frame = tk.Frame(self.root)
        legend_input_frame.pack(pady=10)
        # Create legend labels and entries, total of MAX_FILES split into 2 columns
        for i in range(MAX_FILES):
            legend_label = tk.Label(legend_input_frame, text=f"Legend {i+1}:")
            legend_entry = tk.Entry(legend_input_frame, width=30)
            if i < MAX_FILES//2:
                legend_label.grid(row=i, column=0, padx=3, pady=3)
                legend_entry.grid(row=i, column=1, padx=3, pady=3)
            else:
                legend_label.grid(row=i-MAX_FILES//2, column=2, padx=3, pady=3)
                legend_entry.grid(row=i-MAX_FILES//2, column=3, padx=3, pady=3)
            
            # store the legend entries in a list
            self.legend_entries.append(legend_entry)

    def create_buttons(self):
        """
        Create the buttons for plotting, clearing, saving, and resetting the application
        """
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        plot_button = tk.Button(button_frame, text="Show Graph", command=self.show_graph)
        plot_button.grid(row=0, column=0, padx=10)

        clear_button = tk.Button(button_frame, text="Close Graph", command=self.plot_manager.close_graph)
        clear_button.grid(row=0, column=1, padx=10)

        save_button = tk.Button(button_frame, text="Save Graph", command=self.save_graph)
        save_button.grid(row=0, column=2, padx=10)

        reset_button = tk.Button(button_frame, text="Reset", command=self.reset_app)
        reset_button.grid(row=0, column=3, padx=10)

    # Attempt to create a function to select the current folder from a copy-pasted path, not working
    # def select_current_folder(self):
    #     self.log_text.insert(tk.END, "Function Not Implemented\n")
    #     # self.select_folder_var.set(folder_entry.get())
    #     # self.log_text.insert(tk.END, f"Folder Selected Manually :\n {folder_entry.get()}\n")

    def select_folder(self):
        folder_path = self.file_manager.select_folder()
        self.select_folder_var.set(folder_path)
        if folder_path:
            self.status_var.set(f"Folder selected: {folder_path}")
        else:
            self.status_var.set("No folder selected")

    def load_files(self):
        files = self.file_manager.load_files()
        log_message = self.file_manager.log_files()
        self.log_text.insert(tk.END, f"{log_message}\n")
        if files:
            self.status_var.set(f"Loaded {len(files)} file(s)")
            # Update column dropdowns based on first file
            self.update_column_dropdowns()
        else:
            self.status_var.set("No files loaded")

    def preview_data(self):
        """
        Preview the first loaded CSV file
        """
        if not self.file_manager.files:
            messagebox.showerror("Error", "No files loaded. Please load CSV files first.")
            return

        try:
            header_rows = self.header_rows.get()
            separator = self.separator_str.get()
            self.file_manager.show_preview_dialog(
                self.file_manager.files[0],
                header_rows,
                separator
            )
            self.status_var.set("Preview shown")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview data: {e}")
            self.status_var.set(f"Error: {str(e)}")

    def detect_separator(self):
        """
        Auto-detect the best separator for the first loaded file
        """
        if not self.file_manager.files:
            messagebox.showerror("Error", "No files loaded. Please load CSV files first.")
            return

        try:
            header_rows = self.header_rows.get()
            best_sep, column_info = self.file_manager.detect_separator(
                self.file_manager.files[0],
                header_rows
            )

            # Update separator dropdown to match detected separator
            for sep_name, sep_char in SEPARATORS_DICT.items():
                if sep_char == best_sep:
                    self.separator_name.set(sep_name)
                    self.separator_str.set(best_sep)
                    break

            self.log_text.insert(tk.END, f"Auto-detected separator: '{best_sep}'\n")
            self.status_var.set(f"Separator detected: '{best_sep}'")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to detect separator: {e}")
            self.status_var.set(f"Error: {str(e)}")

    def on_x_column_change(self, value):
        """
        Handle X column dropdown selection
        """
        if value.startswith("Auto"):
            self.x_column_index.set(0)
        else:
            try:
                col_idx = int(value.split(":")[0])
                self.x_column_index.set(col_idx)
            except:
                pass

    def on_y_column_change(self, value):
        """
        Handle Y column dropdown selection
        """
        if value.startswith("Auto"):
            self.y_column_index.set(1)
        else:
            try:
                col_idx = int(value.split(":")[0])
                self.y_column_index.set(col_idx)
            except:
                pass

    def update_column_dropdowns(self):
        """
        Update X/Y column dropdowns based on loaded file headers
        """
        if not self.file_manager.files:
            return

        try:
            header_rows = self.header_rows.get()
            separator = self.separator_str.get()

            # Get column info from first file
            data, column_info, _ = self.file_manager.preview_file(
                self.file_manager.files[0],
                header_rows,
                separator,
                num_rows=1
            )

            if data is not None and len(column_info) > 0:
                # Update dropdown options
                options = ["Auto (0)"] + column_info
                self.column_options = options

                # Update X dropdown
                menu = self.x_column_dropdown['menu']
                menu.delete(0, 'end')
                for option in options:
                    menu.add_command(label=option, command=lambda v=option: self.on_x_column_change(v))

                # Update Y dropdown
                menu = self.y_column_dropdown['menu']
                menu.delete(0, 'end')
                for option in options:
                    menu.add_command(label=option, command=lambda v=option: self.on_y_column_change(v))

                self.status_var.set(f"Columns detected: {len(column_info)}")
        except Exception as e:
            self.log_text.insert(tk.END, f"Warning: Could not update column dropdowns: {e}\n")

    def save_preset(self):
        """
        Save current graph settings as a preset
        """
        preset_name = simpledialog.askstring("Save Preset", "Enter preset name:")
        if not preset_name:
            return

        try:
            settings_dict = {
                'x_label': self.x_label.get(),
                'y_label': self.y_label.get(),
                'title': self.title.get(),
                'scale_factor_x': self.scale_factor_x.get(),
                'scale_factor_y': self.scale_factor_y.get(),
                'normalize_x': self.normalize_x.get(),
                'normalize_y': self.normalize_y.get(),
                'header_rows': self.header_rows.get(),
                'x_column_index': self.x_column_index.get(),
                'y_column_index': self.y_column_index.get(),
                'separator': self.separator_str.get(),
                'line_style': self.line_style_var.get(),
                'marker_style': self.marker_style_var.get(),
                'line_width': self.line_width_var.get(),
                'grid_enabled': self.grid_enabled_var.get(),
            }

            if self.use_x_limits.get():
                settings_dict['x_min'] = self.x_min.get()
                settings_dict['x_max'] = self.x_max.get()
            if self.use_y_limits.get():
                settings_dict['y_min'] = self.y_min.get()
                settings_dict['y_max'] = self.y_max.get()

            success, message = self.plot_manager.save_preset(preset_name, settings_dict)
            if success:
                messagebox.showinfo("Success", message)
                self.status_var.set(f"Preset saved: {preset_name}")
            else:
                messagebox.showerror("Error", message)
                self.status_var.set(f"Error: {message}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save preset: {e}")
            self.status_var.set(f"Error: {str(e)}")

    def load_preset(self):
        """
        Load a preset and apply settings to the GUI
        """
        try:
            presets = self.plot_manager.list_presets()
            if not presets:
                messagebox.showinfo("Info", "No presets available.")
                return

            preset_name = simpledialog.askstring("Load Preset", "Enter preset name:", initialvalue=presets[0] if presets else "")
            if not preset_name:
                return

            success, settings = self.plot_manager.load_preset(preset_name)
            if success:
                # Apply settings to GUI
                self.x_label.set(settings.get('x_label', DEFAULT_X_LABEL))
                self.y_label.set(settings.get('y_label', DEFAULT_Y_LABEL))
                self.title.set(settings.get('title', DEFAULT_TITLE))
                self.scale_factor_x.set(settings.get('scale_factor_x', 1.0))
                self.scale_factor_y.set(settings.get('scale_factor_y', 1.0))
                self.normalize_x.set(settings.get('normalize_x', False))
                self.normalize_y.set(settings.get('normalize_y', False))
                self.header_rows.set(settings.get('header_rows', DEFAULT_HEADER_ROWS))
                self.x_column_index.set(settings.get('x_column_index', 0))
                self.y_column_index.set(settings.get('y_column_index', 1))
                self.separator_str.set(settings.get('separator', ','))

                # Update separator name
                for sep_name, sep_char in SEPARATORS_DICT.items():
                    if sep_char == self.separator_str.get():
                        self.separator_name.set(sep_name)
                        break

                self.line_style_var.set(self.symbol_to_name(
                    LINE_STYLES, settings.get('line_style', DEFAULT_LINE_STYLE_NAME), DEFAULT_LINE_STYLE_NAME))
                self.marker_style_var.set(self.symbol_to_name(
                    MARKER_STYLES, settings.get('marker_style', DEFAULT_MARKER_STYLE_NAME), DEFAULT_MARKER_STYLE_NAME))
                self.line_width_var.set(settings.get('line_width', DEFAULT_LINE_WIDTH))
                self.grid_enabled_var.set(settings.get('grid_enabled', DEFAULT_GRID_ENABLED))

                if 'x_min' in settings:
                    self.x_min.set(settings['x_min'])
                if 'x_max' in settings:
                    self.x_max.set(settings['x_max'])
                if 'y_min' in settings:
                    self.y_min.set(settings['y_min'])
                if 'y_max' in settings:
                    self.y_max.set(settings['y_max'])

                messagebox.showinfo("Success", f"Preset '{preset_name}' loaded.")
                self.status_var.set(f"Preset loaded: {preset_name}")
            else:
                messagebox.showerror("Error", settings)
                self.status_var.set(f"Error: {settings}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load preset: {e}")
            self.status_var.set(f"Error: {str(e)}")

    def show_graph(self):
        # Get the legend labels from the entry fields
        legend_labels = [entry.get() for entry in self.legend_entries if entry.get().strip()]

        # Validation: Check if files are loaded
        if not self.file_manager.files:
            messagebox.showerror("Error", "No files loaded. Please load CSV files first.")
            self.status_var.set("Error: No files loaded")
            return

        # Validation: Check header rows
        try:
            header_rows = self.header_rows.get()
            if header_rows < 0:
                raise ValueError("Header rows must be non-negative")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid header rows value: {e}")
            self.status_var.set("Error: Invalid header rows")
            return

        # Validation: Get and validate column indices
        try:
            x_col = self.x_column_index.get()
            y_col = self.y_column_index.get()
            if x_col < 0 or y_col < 0:
                raise ValueError("Column indices must be non-negative")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid column index: {e}")
            self.status_var.set("Error: Invalid column index")
            return

        # Validation: Validate numeric inputs for scale factors
        try:
            scale_x = self.scale_factor_x.get()
            scale_y = self.scale_factor_y.get()
            if scale_x <= 0 or scale_y <= 0:
                raise ValueError("Scale factors must be positive")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid scale factor: {e}")
            self.status_var.set("Error: Invalid scale factor")
            return

        # Validation: Validate axis limits if used
        x_limits = None
        y_limits = None
        try:
            if self.use_x_limits.get():
                x_min = float(self.x_min.get()) if self.x_min.get() else None
                x_max = float(self.x_max.get()) if self.x_max.get() else None
                if x_min is not None and x_max is not None and x_min >= x_max:
                    raise ValueError("X min must be less than X max")
                x_limits = (x_min, x_max)

            if self.use_y_limits.get():
                y_min = float(self.y_min.get()) if self.y_min.get() else None
                y_max = float(self.y_max.get()) if self.y_max.get() else None
                if y_min is not None and y_max is not None and y_min >= y_max:
                    raise ValueError("Y min must be less than Y max")
                y_limits = (y_min, y_max)
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid axis limits: {e}")
            self.status_var.set("Error: Invalid axis limits")
            return

        try:
            # Pass the plot parameters from the Tkinter Vars to the plot manager
            errors = self.plot_manager.plot_graph(
                files=self.file_manager.files,
                x_label=self.x_label.get(),
                y_label=self.y_label.get(),
                title=self.title.get(),
                scale_x=scale_x,
                scale_y=scale_y,
                normalize_x=self.normalize_x.get(),
                normalize_y=self.normalize_y.get(),
                legend_labels=legend_labels,
                header_rows=header_rows,
                x_col=x_col,
                y_col=y_col,
                separator=self.separator_str.get(),
                x_limits=x_limits,
                use_x_limits=self.use_x_limits.get(),
                y_limits=y_limits,
                use_y_limits=self.use_y_limits.get(),
                line_style=self.style_to_symbol(LINE_STYLES, self.line_style_var.get(), DEFAULT_LINE_STYLE),
                marker_style=self.style_to_symbol(MARKER_STYLES, self.marker_style_var.get(), DEFAULT_MARKER_STYLE),
                line_width=self.line_width_var.get(),
                grid_enabled=self.grid_enabled_var.get()
            )

            # Report any errors from file processing
            if errors:
                error_msg = "Warnings during plotting:\n" + "\n".join(errors)
                self.log_text.insert(tk.END, f"{error_msg}\n")
                self.status_var.set(f"Graph plotted with {len(errors)} warning(s)")
            else:
                self.status_var.set("Graph plotted successfully")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to plot graph: {e}")
            self.status_var.set(f"Error: {str(e)}")

    def save_graph(self):
        # Guard: refuse to save when no graph window is currently displayed
        if not self.plot_manager.has_graph():
            messagebox.showwarning(
                "No graph to save",
                "No graph is currently displayed.\nClick 'Show Graph' first, then save.")
            self.status_var.set("Save cancelled: no graph displayed")
            return

        file_types = [("PNG files", "*.png"), ("SVG files", "*.svg")]
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=file_types)

        if file_path:
            try:
                self.plot_manager.save_graph(file_path)
                messagebox.showinfo("Success", f"Graph saved to {file_path}")
                self.status_var.set(f"Graph saved: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save graph: {e}")
                self.status_var.set(f"Error: {str(e)}")

    def reset_app(self):
        # Clear the file manager files list
        # Reset all the Tkinter variables to their default values
        self.file_manager.files = []
        self.log_text.delete(1.0, tk.END)
        self.plot_manager.close_graph()
        self.x_label.set(DEFAULT_X_LABEL)
        self.y_label.set(DEFAULT_Y_LABEL)
        self.title.set(DEFAULT_TITLE)
        self.scale_factor_x.set(1.0)
        self.scale_factor_y.set(1.0)
        self.normalize_x.set(False)
        self.normalize_y.set(False)
        self.header_rows.set(DEFAULT_HEADER_ROWS)
        self.x_column_index.set(0)
        self.y_column_index.set(1)
        self.x_column_var.set("Auto (0)")
        self.y_column_var.set("Auto (1)")
        self.line_style_var.set(DEFAULT_LINE_STYLE_NAME)
        self.marker_style_var.set(DEFAULT_MARKER_STYLE_NAME)
        self.line_width_var.set(DEFAULT_LINE_WIDTH)
        self.grid_enabled_var.set(DEFAULT_GRID_ENABLED)
        self.x_min.set("")
        self.x_max.set("")
        self.y_min.set("")
        self.y_max.set("")
        self.use_x_limits.set(False)
        self.use_y_limits.set(False)
        self.separator_name.set("Comma")
        self.separator_str.set(",")
        for entry in self.legend_entries:
            entry.delete(0, tk.END)
        self.status_var.set("Ready")
        # Reset column dropdowns
        self.column_options = ["Auto (0)"]
        menu = self.x_column_dropdown['menu']
        menu.delete(0, 'end')
        menu.add_command(label="Auto (0)", command=lambda v="Auto (0)": self.on_x_column_change(v))
        menu = self.y_column_dropdown['menu']
        menu.delete(0, 'end')
        menu.add_command(label="Auto (1)", command=lambda v="Auto (1)": self.on_y_column_change(v))
        self.log_text.insert(tk.END, "Application reset.\n")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = GraphingApp(root)
    root.mainloop()

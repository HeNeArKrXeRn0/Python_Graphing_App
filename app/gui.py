import tkinter as tk
from tkinter import messagebox, filedialog
from file_manager import FileManager
from plot_manager import PlotManager
import os
from settings import MAX_FILES, DEFAULT_X_LABEL, DEFAULT_Y_LABEL, DEFAULT_TITLE, SEPARATORS_DICT

class GraphingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Graphing Application")
        self.root.geometry("900x750")
        self.root.resizable(False, False)
        icon_path = os.path.join(os.path.dirname(__file__), '../assets/graph_icon.ico')
        self.root.iconbitmap(icon_path)

        # Managers
        self.file_manager = FileManager()
        self.plot_manager = PlotManager()

        # Variables
        self.select_folder_var = tk.StringVar(value="")
        self.x_label = tk.StringVar(value=DEFAULT_X_LABEL)
        self.y_label = tk.StringVar(value=DEFAULT_Y_LABEL)
        self.title = tk.StringVar(value=DEFAULT_TITLE)
        self.scale_factor_x = tk.DoubleVar(value=1.0)
        self.scale_factor_y = tk.DoubleVar(value=1.0)
        self.normalize_x = tk.BooleanVar()
        self.normalize_y = tk.BooleanVar()
        self.header_rows = tk.IntVar(value=1)
        self.x_column_index = tk.IntVar(value=0)
        self.y_column_index = tk.IntVar(value=1)

        # Separator selection variables
        self.separator_name = tk.StringVar()
        self.separator_name.set("Comma")
        self.separator_str = tk.StringVar()
        self.separator_str.set(",")

        # X/Y limits
        self.x_min = tk.DoubleVar(value=None)
        self.x_max = tk.DoubleVar(value=None)
        self.use_x_limits = tk.BooleanVar()
        self.y_min = tk.DoubleVar(value=None)
        self.y_max = tk.DoubleVar(value=None)
        self.use_y_limits = tk.BooleanVar()

        # Legend labels
        self.legend_entries = []

        # UI Elements
        self.create_widgets()

    def create_widgets(self):
        # Folder selection
        folder_frame = tk.Frame(self.root)
        folder_frame.pack(pady=5)
        folder_label = tk.Label(folder_frame, text="Select Folder:")
        folder_label.pack(side=tk.LEFT)
        folder_entry = tk.Entry(folder_frame, textvariable=self.select_folder_var, width=100)
        folder_entry.pack(side=tk.LEFT, padx=5)

        # folder_enter_button = tk.Button(folder_frame, text="Select", command=self.select_current_folder)
        # folder_enter_button.pack(side=tk.LEFT)

        browse_button = tk.Button(folder_frame, text="Browse", command=self.select_folder)
        browse_button.pack(side=tk.LEFT)

        # Load files button
        load_button = tk.Button(folder_frame, text="Load Files", command=self.load_files)
        load_button.pack(side=tk.LEFT)

        # X and Y column index selection
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

        separator_label = tk.Label(column_frame, text="Separator:")
        separator_label.grid(row=0, column=2, padx=5, pady=3)
        separator_menu = tk.OptionMenu(column_frame, self.separator_name, *SEPARATORS_DICT.keys(), command=set_sep_variable)
        separator_menu.grid(row=0, column=3, padx=5, pady=3)

        # X and Y column index entry
        x_column_label = tk.Label(column_frame, text="X Column Index:")
        x_column_label.grid(row=1, column=0, padx=5, pady=5)
        x_column_entry = tk.Entry(column_frame, textvariable=self.x_column_index, width=5)
        x_column_entry.grid(row=1, column=1, padx=5, pady=5)
        y_column_label = tk.Label(column_frame, text="Y Column Index:")
        y_column_label.grid(row=1, column=2, padx=5, pady=5)
        y_column_entry = tk.Entry(column_frame, textvariable=self.y_column_index, width=5)
        y_column_entry.grid(row=1, column=3, padx=5, pady=5)

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

        self.create_axis_inputs(axis_frame)
        self.create_legend_inputs()
        self.create_buttons()

    def create_axis_inputs(self, parent):
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
        for i in range(MAX_FILES):
            legend_label = tk.Label(legend_input_frame, text=f"Legend {i+1}:")
            legend_entry = tk.Entry(legend_input_frame, width=30)
            if i < MAX_FILES//2:
                legend_label.grid(row=i, column=0, padx=3, pady=3)
                legend_entry.grid(row=i, column=1, padx=3, pady=3)
            else:
                legend_label.grid(row=i-MAX_FILES//2, column=2, padx=3, pady=3)
                legend_entry.grid(row=i-MAX_FILES//2, column=3, padx=3, pady=3)

            self.legend_entries.append(legend_entry)

    def create_buttons(self):
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

    # def select_current_folder(self):
    #     self.log_text.insert(tk.END, "Function Not Implemented\n")
    #     # self.select_folder_var.set(folder_entry.get())
    #     # self.log_text.insert(tk.END, f"Folder Selected Manually :\n {folder_entry.get()}\n")

    def select_folder(self):
        folder_path = self.file_manager.select_folder()
        self.select_folder_var.set(folder_path)

    def load_files(self):
        files = self.file_manager.load_files()
        log_message = self.file_manager.log_files()
        self.log_text.insert(tk.END, f"{log_message}\n")

    def show_graph(self):
        legend_labels = [entry.get() for entry in self.legend_entries if entry.get().strip()]
        # print(f'Separator used : {self.separator_str}')

        try:
            self.plot_manager.plot_graph(
                files=self.file_manager.files,
                x_label=self.x_label.get(),
                y_label=self.y_label.get(),
                title=self.title.get(),
                scale_x=self.scale_factor_x.get(),
                scale_y=self.scale_factor_y.get(),
                normalize_x=self.normalize_x.get(),
                normalize_y=self.normalize_y.get(),
                legend_labels=legend_labels,
                header_rows=self.header_rows.get(),
                x_col=self.x_column_index.get(),
                y_col=self.y_column_index.get(),
                separator=self.separator_str.get(),
                x_limits=(self.x_min.get(), self.x_max.get()),
                use_x_limits=self.use_x_limits.get(),
                y_limits=(self.y_min.get(), self.y_max.get()),
                use_y_limits=self.use_y_limits.get()
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to plot graph: {e}")

    def save_graph(self):
        file_types = [("PNG files", "*.png"), ("SVG files", "*.svg")]
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=file_types)

        if file_path:
            try:
                self.plot_manager.save_graph(file_path)
                messagebox.showinfo("Success", f"Graph saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save graph: {e}")

    def reset_app(self):
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
        for entry in self.legend_entries:
            entry.delete(0, tk.END)

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = GraphingApp(root)
    root.mainloop()

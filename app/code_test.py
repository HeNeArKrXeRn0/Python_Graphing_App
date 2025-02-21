import tkinter as tk
import os

os.system("cls")

root = tk.Tk()

separator_name = tk.StringVar()
separator_name.set("Comma")
separator_str = tk.StringVar()
separator_str.set(",")

available_separators = {
    "Comma": ",",
    "Semicolon": ";",
    "Colon": ":",
    "Space": " ",
    "Tab": "\t"
}

def set_variable(value):
    separator_str.set(available_separators[separator_name.get()])
    print(separator_str.get())

def print_separator():
    print(separator_str.get())

separator_menu = tk.OptionMenu(root, separator_name, *available_separators.keys(), command=set_variable)
separator_menu.pack()

folder_button = tk.Button(root, text="Print Var", command=print_separator)
folder_button.pack()

root.mainloop()
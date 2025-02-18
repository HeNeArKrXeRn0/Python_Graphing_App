from tkinter import Tk
from gui import GraphingApp
import os

if __name__ == "__main__":
    os.system("cls")
    # Create the main application window
    root = Tk()
    app = GraphingApp(root)
    # Run the application
    root.mainloop()
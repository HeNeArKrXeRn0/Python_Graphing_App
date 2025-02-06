from tkinter import Tk
from gui import GraphingApp

if __name__ == "__main__":
    # Create the main application window
    root = Tk()
    app = GraphingApp(root)
    # Run the application
    root.mainloop()
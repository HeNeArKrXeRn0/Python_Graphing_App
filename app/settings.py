# settings.py

# Default values for graph settings
DEFAULT_X_LABEL = "X (unit)"
DEFAULT_Y_LABEL = "Y (unit)"
DEFAULT_TITLE = "Graph"
# DEFAULT_NORMALIZE_X = False
# DEFAULT_NORMALIZE_Y = False

# Application limits
MAX_FILES = 12

# Separator options
SEPARATORS_DICT = {
    "Comma": ",",
    "Semicolon": ";",
    "Colon": ":",
    "Space": " ",
    "Tab": "\t"
}

# Graph appearance
COLOR_PALETTE = [
    'tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple',
    'tab:cyan', 'tab:olive', 'tab:pink', 'salmon', 'royalblue',
    'magenta', 'lime'
]
FIGURE_WIDTH = 5 * 1.618  # Golden ratio width
FIGURE_HEIGHT = 5

# # Logging
# LOG_NO_FILES = "No files loaded."
# LOG_SELECTED_FOLDER = "Selected Folder: {folder}\n"
# LOG_LOADED_FILES = "Loaded Files:\n{files}\n"

# settings.py

# Default values for graph settings
DEFAULT_X_LABEL = "X (unit)"
DEFAULT_Y_LABEL = "Y (unit)"
DEFAULT_TITLE = "Graph"

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

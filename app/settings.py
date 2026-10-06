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

# Line style options
LINE_STYLES = {
    "Solid": "-",
    "Dashed": "--",
    "Dotted": ":",
    "Dash-dot": "-."
}

# Marker style options
MARKER_STYLES = {
    "None": "",
    "Circle": "o",
    "Square": "s",
    "Triangle": "^",
    "Diamond": "D",
    "Pentagon": "p",
    "Star": "*",
    "Hexagon": "h",
    "Plus": "+",
    "X": "x",
    "Dot": "."
}

# Default customization values
DEFAULT_LINE_STYLE = "-"
DEFAULT_MARKER_STYLE = ""
DEFAULT_LINE_WIDTH = 2.0
DEFAULT_GRID_ENABLED = True
DEFAULT_PRESET_FILE = "graph_presets.json"

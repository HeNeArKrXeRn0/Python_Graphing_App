# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

**Run the application:**
```bash
python app/main.py
```

**Install dependencies (using uv):**
```bash
uv sync
```

**Install dependencies (using pip):**
```bash
pip install -r requirements.txt
```

**Run tests (headless — the suite forces the Agg backend):**
```bash
uv run pytest
```

**Lint:**
```bash
uv run ruff check .
```

`requirements.txt` is generated; regenerate it after editing dependencies with
`uv export --no-dev --no-hashes --frozen --no-emit-project -o requirements.txt`.

## Architecture

This is a Tkinter-based GUI application for plotting CSV data with Matplotlib.

**Key Components:**

- **`main.py`** - Entry point; creates the Tkinter root window and instantiates `GraphingApp`
- **`gui.py`** - `GraphingApp` class: main GUI controller with Tkinter variables for all user inputs, input validation, column dropdowns, customization controls, and preset save/load
- **`file_manager.py`** - `FileManager` class: folder/file dialogs, CSV preview (`preview_file()` / `show_preview_dialog()`), and separator auto-detection (`detect_separator()`)
- **`plot_manager.py`** - `PlotManager` class: Matplotlib plotting, log-axis scaling, CSV data reading, graph saving, and preset persistence
- **`settings.py`** - Constants: `MAX_FILES`, `SEPARATORS_DICT`, `COLOR_PALETTE`, style maps (`LINE_STYLES`, `MARKER_STYLES`), and default values (`DEFAULT_HEADER_ROWS = 0`, labels, line/marker/grid defaults)

**Data Flow:**
1. User selects folder → `FileManager.select_folder()`
2. User loads CSV files → `FileManager.load_files()` stores paths in `self.files`
3. Optional: `Preview Data` → `FileManager.show_preview_dialog()`; `Auto-Detect Separator` → `FileManager.detect_separator()`; column dropdowns refresh from the first file's headers
4. User clicks "Show Graph" → `GraphingApp.show_graph()` validates inputs and calls `PlotManager.plot_graph()`
5. `PlotManager` reads CSV data with `read_csv_data()`, drops points a log axis cannot draw (`filter_nonpositive_pairs()`), applies normalization/scaling, plots with Matplotlib; per-file failures and omissions are collected and returned as warnings instead of aborting
6. Graph can be saved via `PlotManager.save_graph()` (guarded by `has_graph()`) or closed with `close_graph()`

**Key Design Patterns:**
- Manager pattern: `FileManager` and `PlotManager` separate concerns from GUI logic
- Tkinter `StringVar`/`DoubleVar`/`BooleanVar` for reactive UI state
- Color palette from `settings.py` ensures consistent curve coloring across files
- Style dropdowns store GUI display names ("Solid", "Square"); `GraphingApp.style_to_symbol()` converts to Matplotlib symbols at plot time, `symbol_to_name()` converts back when loading presets (accepts both the new name format and legacy raw symbols)

**Presets:**
- `PlotManager.save_preset()` / `load_preset()` / `list_presets()` persist named setting bundles to `DEFAULT_PRESET_FILE` (`graph_presets.json`, resolved relative to the current working directory)
- `graph_presets.json` is runtime state and is gitignored; presets written before a key existed load via `.get(key, DEFAULT_...)`, so adding a setting is backwards compatible

**Log Axes:**
- `Log X` / `Log Y` checkbuttons feed `log_x` / `log_y` through to `plot_graph()`; `PlotManager.apply_log_axes()` switches to base 10 and installs `LogFormatterMathtext` on major ticks plus `NullFormatter` on minor ticks — without the latter, Matplotlib labels every minor tick on a log axis
- Scales are applied immediately after `plt.subplots()`, so `set_xlim`/`set_ylim` run against the final scale
- A log axis cannot render a value <= 0. `PlotManager.filter_nonpositive_pairs()` drops those points **as pairs** (a dropped Y takes its X) before normalization, and returns a `[WARN] ... n of m Y values <= 0 omitted (log Y); min was ...` message that rides the existing warnings path into the log box and status bar. Reported counts/minima describe the raw file values
- `GraphingApp.validate_axis_limits()` rejects a non-positive limit on a log-scaled axis; Matplotlib would otherwise silently ignore such a bound

**Numeric input gotcha:**
- Reading a Tk `IntVar`/`DoubleVar` whose text is not a number raises `tkinter.TclError`, which is **not** a `ValueError`. Validation blocks around `.get()` must catch `(ValueError, tk.TclError)`. Fields held in `StringVar`s and parsed with `float()` only ever raise `ValueError`

**Tests:**
- `tests/` runs headless: `tests/conftest.py` forces the Agg backend before anything imports `plot_manager` (which imports pyplot at module level). `pythonpath = ["app"]` in `pyproject.toml` resolves the flat `app/` imports
- Tests target the pure/static helpers; none calls `plot_graph()`, which ends in `plt.show()`

**CSV Handling:**
- Supports configurable header rows (number of metadata rows skipped before the header, default 0), column indices, and separators (comma, semicolon, colon, space, tab)
- Uses `chardet` for encoding detection
- Auto-detects numeric columns; uses index as X if column is non-numeric

**Saving Graph Guard:**
- `PlotManager.has_graph()` returns False when no figure is displayed or the graph window was closed; `save_graph()` raises `ValueError` in that case and `GraphingApp.save_graph()` shows a warning before the save dialog, preventing blank white PNG/SVG exports

**Packaging note:**
- `pyproject.toml` declares a `uv_build` package with console script `python-graphing-app = "python_graphing_app:main"`, but `src/python_graphing_app/` is an empty stub and `app/` uses flat imports — the console script does not work yet; run via `python app/main.py`

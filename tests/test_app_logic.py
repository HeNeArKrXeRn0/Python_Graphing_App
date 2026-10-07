"""
Tests for the app's existing non-GUI logic.

These cover behaviour the log-axis work leans on: separator detection, the CSV
reader and its fallbacks, the data preview, and the style-name/symbol mapping
used by presets.
"""

import pytest

from file_manager import FileManager
from plot_manager import PlotManager
from settings import LINE_STYLES, MARKER_STYLES, SEPARATORS_DICT
from gui import GraphingApp


@pytest.fixture
def file_manager():
    return FileManager()


@pytest.fixture
def plot_manager():
    return PlotManager()


def write_csv(tmp_path, name, text):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return str(path)


class TestDetectSeparator:
    def test_comma_file_is_detected(self, file_manager, reference_csv):
        separator, columns = file_manager.detect_separator(str(reference_csv), 0)
        assert separator == ","
        assert columns == ["0: DAC", "1: Laser Power"]

    def test_semicolon_file_is_detected(self, file_manager, tmp_path):
        path = write_csv(tmp_path, "semi.csv", "a;b;c\n1;2;3\n4;5;6\n")
        separator, columns = file_manager.detect_separator(path, 0)
        assert separator == ";"
        assert columns == ["0: a", "1: b", "2: c"]

    def test_tab_file_is_detected(self, file_manager, examples_dir):
        # the UTF-16 data-logger export is tab separated throughout
        path = examples_dir / "Test_File_UTF-16.csv"
        separator, _ = file_manager.detect_separator(str(path), 0)
        assert separator == "\t"

    def test_single_column_file_falls_back_to_comma(self, file_manager, tmp_path):
        path = write_csv(tmp_path, "one.csv", "value\n1\n2\n")
        separator, _ = file_manager.detect_separator(path, 0)
        assert separator == ","

    def test_every_separator_key_is_a_single_character(self):
        assert set(SEPARATORS_DICT.values()) == {",", ";", ":", " ", "\t"}


class TestPreviewFile:
    def test_returns_frame_columns_and_separator(self, file_manager, reference_csv):
        data, columns, separator = file_manager.preview_file(str(reference_csv))
        assert data is not None
        assert len(data) == 10  # the default preview window
        assert columns == ["0: DAC", "1: Laser Power"]
        assert separator == ","

    def test_num_rows_is_respected(self, file_manager, reference_csv):
        data, _, _ = file_manager.preview_file(str(reference_csv), num_rows=3)
        assert len(data) == 3

    def test_missing_file_reports_an_error(self, file_manager):
        data, columns, error = file_manager.preview_file("does_not_exist.csv")
        assert data is None
        assert columns == []
        assert error  # message text is not contractual

    def test_utf16_file_decodes(self, file_manager, examples_dir):
        # exercises the chardet encoding-detection path
        path = examples_dir / "Test_File_UTF-16.csv"
        data, columns, error = file_manager.preview_file(str(path), separator="\t")
        assert data is not None, error
        assert columns


class TestReadCsvData:
    def test_reads_the_selected_columns(self, plot_manager, reference_csv):
        x, y, error = plot_manager.read_csv_data(str(reference_csv), 0, 1, 0, ",")
        assert error is None
        assert len(x) == 4096
        assert len(y) == 4096
        assert x.iloc[0] == 0
        assert y.iloc[0] == pytest.approx(1.00187e-05)

    def test_non_numeric_x_column_falls_back_to_the_row_index(
            self, plot_manager, tmp_path):
        path = write_csv(tmp_path, "text.csv", "name,value\nalpha,1.5\nbeta,2.5\n")
        x, y, error = plot_manager.read_csv_data(path, 0, 1, 0, ",")
        assert error is None
        assert list(x) == [0, 1]
        assert list(y) == [1.5, 2.5]

    def test_non_numeric_y_column_is_an_error(self, plot_manager, tmp_path):
        path = write_csv(tmp_path, "text.csv", "name,value\nalpha,1.5\nbeta,2.5\n")
        x, y, error = plot_manager.read_csv_data(path, 1, 0, 0, ",")
        assert x is None and y is None
        assert error == "Column 0 is not numeric."

    def test_missing_file_is_reported(self, plot_manager):
        x, y, error = plot_manager.read_csv_data("absent.csv", 0, 1, 0, ",")
        assert x is None and y is None
        assert error == "File not found: absent.csv"

    def test_column_index_out_of_range_is_reported(self, plot_manager, reference_csv):
        x, y, error = plot_manager.read_csv_data(str(reference_csv), 0, 9, 0, ",")
        assert x is None and y is None
        assert error == "Column index out of range."

    def test_utf16_file_is_decoded_not_rejected(self, plot_manager, examples_dir):
        path = examples_dir / "Test_File_UTF-16.csv"
        _, _, error = plot_manager.read_csv_data(str(path), 0, 1, 12, "\t")
        # whatever the layout does or does not yield, the encoding must not be
        # the thing that fails
        assert error is None or "Encoding error" not in error


class TestStyleNameMapping:
    def test_display_name_becomes_a_matplotlib_symbol(self):
        assert GraphingApp.style_to_symbol(LINE_STYLES, "Dashed", "-") == "--"
        assert GraphingApp.style_to_symbol(MARKER_STYLES, "Square", "") == "s"

    def test_raw_symbol_passes_through_for_old_presets(self):
        assert GraphingApp.style_to_symbol(LINE_STYLES, "--", "-") == "--"
        assert GraphingApp.style_to_symbol(MARKER_STYLES, "s", "") == "s"

    def test_unknown_name_falls_back_to_the_default(self):
        assert GraphingApp.style_to_symbol(LINE_STYLES, "Wobbly", "-") == "-"
        assert GraphingApp.style_to_symbol(MARKER_STYLES, "Wobbly", "") == ""

    def test_symbol_becomes_a_display_name(self):
        assert GraphingApp.symbol_to_name(LINE_STYLES, "--", "Solid") == "Dashed"
        assert GraphingApp.symbol_to_name(MARKER_STYLES, "s", "None") == "Square"

    def test_display_name_passes_through(self):
        assert GraphingApp.symbol_to_name(LINE_STYLES, "Dotted", "Solid") == "Dotted"

    def test_unknown_symbol_falls_back_to_the_default_name(self):
        assert GraphingApp.symbol_to_name(LINE_STYLES, "?", "Solid") == "Solid"

    @pytest.mark.parametrize("mapping", [LINE_STYLES, MARKER_STYLES])
    def test_every_entry_round_trips(self, mapping):
        for name, symbol in mapping.items():
            forward = GraphingApp.style_to_symbol(mapping, name, symbol)
            assert forward == symbol
            assert GraphingApp.symbol_to_name(mapping, forward, name) == name

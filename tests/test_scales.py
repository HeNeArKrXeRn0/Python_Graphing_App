"""
Tests for the logarithmic axis feature.

Everything exercised here is deliberately the pure/non-GUI surface: the
non-positive filter, the tick configuration (against a bare Figure, which has
no canvas and so cannot display), the limit validator, and preset persistence.
plot_graph() is never called because it ends in plt.show().
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import matplotlib.axes
from matplotlib.figure import Figure
from matplotlib.ticker import LogFormatterMathtext, NullFormatter

import plot_manager
from plot_manager import PlotManager
from settings import DEFAULT_LOG_X, DEFAULT_LOG_Y
from gui import GraphingApp

# The exact warning the shipped reference curve must produce under Log Y
REFERENCE_Y_WARNING = "10 of 4096 Y values <= 0 omitted (log Y); min was -2.01e-06"
TEST_Y_WARNING = "16 of 4096 Y values <= 0 omitted (log Y); min was -4.01e-06"
X_WARNING = "1 of 4096 X values <= 0 omitted (log X); min was 0.00e+00"


@pytest.fixture
def grid_calls(monkeypatch):
    """Capture every ax.grid(...) call, so tick/grid behaviour is observable."""
    calls = []
    monkeypatch.setattr(
        matplotlib.axes.Axes, "grid",
        lambda self, *args, **kwargs: calls.append((args, kwargs)))
    return calls


def make_axes():
    """An Axes with no canvas: nothing here can open a window."""
    return Figure().add_subplot(111)


class TestFilterNonPositivePairs:
    def test_nothing_log_scaled_is_a_noop(self):
        x = np.array([0.0, -1.0, 2.0])
        y = np.array([-5.0, 3.0, 4.0])
        x_kept, y_kept, warnings = PlotManager.filter_nonpositive_pairs(
            x, y, False, False)
        assert warnings == []
        # inputs handed straight back, untouched
        assert x_kept is x and y_kept is y

    def test_log_y_message_is_exact(self):
        x = np.array([1.0, 2.0, 3.0, 4.0])
        y = np.array([1e-3, -2.007e-6, 0.0, 5e-2])
        x_kept, y_kept, warnings = PlotManager.filter_nonpositive_pairs(
            x, y, False, True)
        assert warnings == ["2 of 4 Y values <= 0 omitted (log Y); min was -2.01e-06"]
        np.testing.assert_array_equal(x_kept, [1.0, 4.0])
        np.testing.assert_array_equal(y_kept, [1e-3, 5e-2])

    def test_log_x_reports_a_zero_minimum(self):
        x = np.array([0.0, 1.0, 2.0])
        y = np.array([1.0, 1.0, 1.0])
        _, _, warnings = PlotManager.filter_nonpositive_pairs(x, y, True, False)
        assert warnings == ["1 of 3 X values <= 0 omitted (log X); min was 0.00e+00"]

    def test_dropped_point_takes_its_partner_with_it(self):
        # The Y at index 1 is non-positive, so its X must leave with it
        x = np.array([10.0, 20.0, 30.0])
        y = np.array([1.0, -1.0, 2.0])
        x_kept, y_kept, _ = PlotManager.filter_nonpositive_pairs(x, y, False, True)
        np.testing.assert_array_equal(x_kept, [10.0, 30.0])
        np.testing.assert_array_equal(y_kept, [1.0, 2.0])

    def test_both_axes_report_x_before_y(self):
        x = np.array([0.0, 1.0, 2.0])
        y = np.array([-1.0, 1.0, 2.0])
        _, _, warnings = PlotManager.filter_nonpositive_pairs(x, y, True, True)
        assert len(warnings) == 2
        assert "log X" in warnings[0]
        assert "log Y" in warnings[1]

    def test_all_positive_produces_no_warnings(self):
        x = np.array([1.0, 2.0])
        y = np.array([1e-9, 1.0])
        x_kept, y_kept, warnings = PlotManager.filter_nonpositive_pairs(x, y, True, True)
        assert warnings == []
        assert len(x_kept) == 2 and len(y_kept) == 2

    def test_all_nonpositive_empties_both_series(self):
        x = np.array([-3.0, -2.0, -1.0])
        y = np.array([0.0, 0.0, 0.0])
        x_kept, y_kept, warnings = PlotManager.filter_nonpositive_pairs(x, y, False, True)
        assert len(x_kept) == 0 and len(y_kept) == 0
        assert warnings[0].startswith("3 of 3 Y values")

    def test_nan_is_kept_and_not_counted(self):
        # Matplotlib already renders NaN as a gap in the line
        x = np.array([1.0, 2.0, 3.0])
        y = np.array([1.0, np.nan, 2.0])
        x_kept, y_kept, warnings = PlotManager.filter_nonpositive_pairs(x, y, False, True)
        assert warnings == []
        assert len(y_kept) == 3

    def test_accepts_series_and_index_inputs(self):
        # read_csv_data returns a Series for a numeric column, and may return a
        # RangeIndex when the X column is not numeric
        series = pd.Series([1e-4, -1e-6, 2e-4])
        index = pd.RangeIndex(3)
        x_kept, y_kept, warnings = PlotManager.filter_nonpositive_pairs(
            index, series, False, True)
        assert warnings == ["1 of 3 Y values <= 0 omitted (log Y); min was -1.00e-06"]
        np.testing.assert_array_equal(x_kept, [0, 2])
        np.testing.assert_array_equal(y_kept, [1e-4, 2e-4])

    def test_returns_ndarrays_when_filtering(self):
        x_kept, y_kept, _ = PlotManager.filter_nonpositive_pairs(
            pd.Series([1.0, 2.0]), pd.Series([1.0, 2.0]), True, True)
        assert isinstance(x_kept, np.ndarray)
        assert isinstance(y_kept, np.ndarray)


class TestRealExampleData:
    """Locks in the numbers quoted in the README and the end-to-end check."""

    @pytest.fixture
    def reference_data(self, reference_csv):
        manager = PlotManager()
        x, y, error = manager.read_csv_data(str(reference_csv), 0, 1, 0, ",")
        assert error is None
        return x, y

    def test_reference_curve_log_y_warning(self, reference_data):
        x, y = reference_data
        x_kept, y_kept, warnings = PlotManager.filter_nonpositive_pairs(
            x, y, False, True)
        assert warnings == [REFERENCE_Y_WARNING]
        assert len(y_kept) == 4096 - 10

    def test_test_curve_log_y_warning(self, test_csv):
        manager = PlotManager()
        x, y, error = manager.read_csv_data(str(test_csv), 0, 1, 0, ",")
        assert error is None
        _, _, warnings = PlotManager.filter_nonpositive_pairs(x, y, False, True)
        assert warnings == [TEST_Y_WARNING]

    def test_both_curves_drop_their_first_row_under_log_x(self, reference_data, test_csv):
        x, y = reference_data
        _, _, warnings = PlotManager.filter_nonpositive_pairs(x, y, True, False)
        assert warnings == [X_WARNING]

        manager = PlotManager()
        x2, y2, error = manager.read_csv_data(str(test_csv), 0, 1, 0, ",")
        assert error is None
        _, _, warnings = PlotManager.filter_nonpositive_pairs(x2, y2, True, True)
        assert warnings[0] == X_WARNING

    def test_log_x_and_log_y_dropped_points_do_not_overlap(self, reference_data):
        # DAC 0 has a positive power reading, so the X-dropped point is not one
        # of the Y-dropped ones: 4096 - 1 - 10 survive
        x, y = reference_data
        x_kept, y_kept, warnings = PlotManager.filter_nonpositive_pairs(x, y, True, True)
        assert len(warnings) == 2
        assert len(x_kept) == 4085
        assert len(y_kept) == 4085

    def test_every_kept_point_is_plotable_on_a_log_axis(self, reference_data):
        x, y = reference_data
        x_kept, y_kept, _ = PlotManager.filter_nonpositive_pairs(x, y, True, True)
        assert (x_kept > 0).all()
        assert (y_kept > 0).all()

    def test_normalized_series_reports_raw_minimum(self, reference_data):
        # The warning describes the file, and its count stays correct after the
        # normalize/scale step that follows it
        x, y = reference_data
        x_kept, y_kept, warnings = PlotManager.filter_nonpositive_pairs(
            x, y, False, True)
        normalized = y_kept / y.max()
        assert warnings == [REFERENCE_Y_WARNING]
        assert (normalized <= 1.0).all()


class TestApplyLogAxes:
    def test_defaults_leave_both_axes_linear(self):
        ax = make_axes()
        PlotManager.apply_log_axes(ax, False, False)
        assert ax.get_xscale() == "linear"
        assert ax.get_yscale() == "linear"

    def test_only_the_requested_axis_becomes_log(self):
        ax = make_axes()
        PlotManager.apply_log_axes(ax, False, True)
        assert ax.get_xscale() == "linear"
        assert ax.get_yscale() == "log"

        ax = make_axes()
        PlotManager.apply_log_axes(ax, True, False)
        assert ax.get_xscale() == "log"
        assert ax.get_yscale() == "linear"

    def test_major_ticks_use_mathtext_notation(self):
        ax = make_axes()
        PlotManager.apply_log_axes(ax, True, True)
        assert isinstance(ax.xaxis.get_major_formatter(), LogFormatterMathtext)
        assert isinstance(ax.yaxis.get_major_formatter(), LogFormatterMathtext)

    def test_minor_ticks_are_silenced(self):
        """Matplotlib's default labels every minor tick; this is the guard."""
        # Check the premise first: a stock log axis really does label its minor
        # ticks, which is the clutter the override below exists to prevent
        stock = make_axes()
        stock.set_yscale("log")
        assert type(stock.yaxis.get_minor_formatter()).__name__ == \
            "LogFormatterSciNotation"

        ax = make_axes()
        PlotManager.apply_log_axes(ax, True, True)
        assert isinstance(ax.xaxis.get_minor_formatter(), NullFormatter)
        assert isinstance(ax.yaxis.get_minor_formatter(), NullFormatter)

    def test_minor_gridlines_only_when_grid_and_log(self, grid_calls):
        ax = make_axes()
        PlotManager.apply_log_axes(ax, True, False, grid_enabled=True)
        assert any(kwargs.get("which") == "minor" for _, kwargs in grid_calls)

    def test_no_minor_gridlines_when_grid_disabled(self, grid_calls):
        ax = make_axes()
        PlotManager.apply_log_axes(ax, True, True, grid_enabled=False)
        assert not any(kwargs.get("which") == "minor" for _, kwargs in grid_calls)

    def test_no_minor_gridlines_when_nothing_is_log(self, grid_calls):
        ax = make_axes()
        PlotManager.apply_log_axes(ax, False, False, grid_enabled=True)
        assert not any(kwargs.get("which") == "minor" for _, kwargs in grid_calls)


class TestValidateAxisLimits:
    """validate_axis_limits is called with raw entry text and never raises."""

    @staticmethod
    def call(use_x=False, x_min="", x_max="", use_y=False, y_min="", y_max="",
             log_x=False, log_y=False):
        return GraphingApp.validate_axis_limits(
            use_x, x_min, x_max, use_y, y_min, y_max, log_x, log_y)

    def test_disabled_axes_have_no_limits(self):
        assert self.call() == (None, None, None)

    def test_blank_bounds_stay_autoscaled(self):
        x_limits, y_limits, error = self.call(use_x=True, x_max="4095")
        assert error is None
        assert x_limits == (None, 4095.0)
        assert y_limits is None

    def test_both_bounds_parsed(self):
        _, y_limits, error = self.call(use_y=True, y_min="0", y_max="0.01")
        assert error is None
        assert y_limits == (0.0, 0.01)

    def test_min_not_below_max_is_rejected_with_the_legacy_message(self):
        assert self.call(use_x=True, x_min="10", x_max="5")[2] == \
            "X min must be less than X max"
        assert self.call(use_y=True, y_min="2", y_max="2")[2] == \
            "Y min must be less than Y max"

    def test_unparseable_input_returns_a_message_instead_of_raising(self):
        assert self.call(use_x=True, x_min="abc")[2] == "X Min must be a number"
        assert self.call(use_y=True, y_max="")[2] is None  # blank is fine
        assert self.call(use_y=True, y_max="not a number")[2] == "Y Max must be a number"

    def test_whitespace_only_counts_as_blank(self):
        x_limits, _, error = self.call(use_x=True, x_min="   ", x_max="4095")
        assert error is None
        assert x_limits == (None, 4095.0)

    @pytest.mark.parametrize("bad", ["0", "-1", "-0.5", "0.0"])
    def test_log_axis_rejects_a_non_positive_x_bound(self, bad):
        error = self.call(use_x=True, x_min=bad, log_x=True)[2]
        assert error == "X Min must be positive when Log X is enabled"

    @pytest.mark.parametrize("bad", ["0", "-2"])
    def test_log_axis_rejects_a_non_positive_y_max(self, bad):
        error = self.call(use_y=True, y_max=bad, log_y=True)[2]
        assert error == "Y Max must be positive when Log Y is enabled"

    def test_log_axis_accepts_positive_bounds(self):
        x_limits, y_limits, error = self.call(
            use_x=True, x_min="1", x_max="4095",
            use_y=True, y_min="1e-06", y_max="0.02",
            log_x=True, log_y=True)
        assert error is None
        assert x_limits == (1.0, 4095.0)
        assert y_limits == (1e-06, 0.02)

    def test_log_axis_still_allows_an_open_low_end(self):
        # A blank min is allowed: the axis autoscales to the first positive value
        x_limits, _, error = self.call(use_x=True, x_max="4095", log_x=True)
        assert error is None
        assert x_limits == (None, 4095.0)

    def test_non_positive_bound_is_fine_without_log(self):
        _, y_limits, error = self.call(use_y=True, y_min="-1", y_max="1")
        assert error is None
        assert y_limits == (-1.0, 1.0)

    def test_x_is_validated_before_y(self):
        error = self.call(use_x=True, x_min="0", use_y=True, y_max="oops", log_x=True)[2]
        assert error == "X Min must be positive when Log X is enabled"


class TestPresetCompatibility:
    """Presets saved before log axes existed must still load."""

    LEGACY_PRESET = {
        "x_label": "DAC",
        "y_label": "Laser Power",
        "title": "Test Graph",
        "scale_factor_x": 1.0,
        "scale_factor_y": 1.0,
        "normalize_x": False,
        "normalize_y": False,
        "header_rows": 0,
        "x_column_index": 0,
        "y_column_index": 1,
        "separator": ",",
        # legacy format: a raw Matplotlib symbol rather than a display name
        "line_style": "--",
        "marker_style": "Square",
        "line_width": 1.0,
        "grid_enabled": True,
    }

    @pytest.fixture
    def preset_file(self, monkeypatch, tmp_path):
        target = tmp_path / "presets.json"
        monkeypatch.setattr(plot_manager, "DEFAULT_PRESET_FILE", str(target))
        return target

    def test_legacy_preset_has_no_log_keys_and_defaults_to_off(self, preset_file):
        manager = PlotManager()
        saved, message = manager.save_preset("Legacy", dict(self.LEGACY_PRESET))
        assert saved, message

        loaded, settings = manager.load_preset("Legacy")
        assert loaded, settings
        assert "log_x" not in settings and "log_y" not in settings
        assert settings.get("log_x", DEFAULT_LOG_X) is False
        assert settings.get("log_y", DEFAULT_LOG_Y) is False

    def test_new_preset_round_trips_the_log_keys(self, preset_file):
        manager = PlotManager()
        settings = dict(self.LEGACY_PRESET, log_x=True, log_y=False)
        saved, message = manager.save_preset("WithLog", settings)
        assert saved, message

        loaded, stored = manager.load_preset("WithLog")
        assert loaded, stored
        assert stored["log_x"] is True
        assert stored["log_y"] is False

    def test_log_keys_reach_the_file(self, preset_file):
        manager = PlotManager()
        manager.save_preset("Flip", dict(self.LEGACY_PRESET, log_x=False, log_y=True))
        with open(preset_file) as handle:
            assert json.load(handle)["Flip"]["log_y"] is True

    def test_the_shipped_repo_preset_still_loads(self):
        """The preset committed to the repo must survive without log keys."""
        target = Path(__file__).resolve().parents[1] / "graph_presets.json"
        if not target.exists():
            pytest.skip("graph_presets.json is not present in the repo")
        with open(target) as handle:
            presets = json.load(handle)
        assert "Test_Preset" in presets
        stored = presets["Test_Preset"]
        assert "log_x" not in stored
        assert stored.get("log_x", DEFAULT_LOG_X) is False

"""
Shared pytest setup.

app/ is a flat layout: its modules import each other by bare name
(``from settings import ...``), so the directory itself goes on sys.path.
pyproject's ``pythonpath`` option covers the normal ``pytest`` run; the insert
below additionally makes a direct ``python -m pytest tests/test_x.py`` work.
"""

import sys
from pathlib import Path

import matplotlib
import pytest

# plot_manager imports pyplot at module level. Force the headless backend
# before any test module can import it, so the suite can never open a window.
matplotlib.use("Agg")

REPO_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = REPO_ROOT / "app"
EXAMPLES_DIR = REPO_ROOT / "examples"

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

REFERENCE_CSV = "00_Reference_Laser_Power_Curve.csv"
TEST_CSV = "01_Test_Laser_Power_Curve.csv"


@pytest.fixture(scope="session")
def examples_dir():
    """Path to the shipped example CSVs."""
    return EXAMPLES_DIR


@pytest.fixture(scope="session")
def reference_csv(examples_dir):
    """Laser power curve with 10 of 4096 Y values <= 0."""
    return examples_dir / REFERENCE_CSV


@pytest.fixture(scope="session")
def test_csv(examples_dir):
    """Laser power curve with 16 of 4096 Y values <= 0."""
    return examples_dir / TEST_CSV

"""
MEA Electrode Position Extractor

A Python package for extracting electrode positions from GDS (GDSII) files
containing MEA (Microelectrode Array) layouts.
"""

from .extractor import (
    get_electrodes,
    adjust_electrode_positions,
    write_json,
    create_dots_confirmation,
)
from .utils import (
    add_labels,
    get_center,
    get_area_of_bounding_box,
    remove_outliers,
    draw_simulator_grid,
    draw_dish,
)

__version__ = "1.0.0"
__all__ = [
    "get_electrodes",
    "adjust_electrode_positions",
    "write_json",
    "create_dots_confirmation",
    "add_labels",
    "get_center",
    "get_area_of_bounding_box",
    "remove_outliers",
    "draw_simulator_grid",
    "draw_dish",
]


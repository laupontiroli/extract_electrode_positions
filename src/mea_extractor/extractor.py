"""
Core extraction logic for MEA electrode positions from GDS files.
"""

import gdspy
import json
import numpy as np
from pathlib import Path
from .utils import (
    add_labels,
    get_center,
    remove_outliers,
    draw_simulator_grid,
    draw_dish,
)


# Default configuration constants
DEFAULT_SIMULATOR_GRID_SIZE = (4000, 4000)  # in micrometers (4 mm x 4 mm)
DEFAULT_DISTANCE_BETWEEN_ELECTRODES = 180
DEFAULT_ELECTRODE_DIAMETER = 30  # in micrometers


def adjust_electrode_positions(
    electrode_positions, 
    distance_between_electrodes=DEFAULT_DISTANCE_BETWEEN_ELECTRODES,
    simulator_grid_size=DEFAULT_SIMULATOR_GRID_SIZE
):
    """
    Rescale and translate electrode positions so that:
    1. Distances between nearest neighbors match DISTANCE_BETWEEN_ELECTRODES (edge-to-edge).
    2. The MEA is centered in the simulator grid.
    
    Args:
        electrode_positions: Set or list of (x, y) tuples
        distance_between_electrodes: Desired spacing between electrode centers
        simulator_grid_size: Tuple of (width, height) for the simulator grid
        
    Returns:
        List of adjusted (x, y) tuples
    """
    electrode_positions = np.array(list(electrode_positions), dtype=float)

    # --- Step 1: Normalize (make mean-centered) ---
    mean_x, mean_y = electrode_positions.mean(axis=0)
    centered = electrode_positions - np.array([mean_x, mean_y])

    # --- Step 2: Compute nearest-neighbor distance ---
    nearest_dists = []
    for i in range(len(centered)):
        dists_i = [
            np.linalg.norm(centered[i] - centered[j]) 
            for j in range(len(centered)) if i != j
        ]
        nearest_dists.append(min(dists_i))
    avg_spacing = np.median(nearest_dists)

    # --- Step 3: Desired spacing = distance between centers = gap + diameter ---
    desired_spacing = distance_between_electrodes

    # --- Step 4: Scale so spacing matches desired spacing ---
    scale_factor = desired_spacing / avg_spacing
    scaled = centered * scale_factor

    # --- Step 5: Shift so MEA is centered in simulator grid ---
    target_center = np.array(simulator_grid_size) / 2
    adjusted = scaled + target_center

    return [tuple(p) for p in adjusted]


def write_json(
    electrode_positions, 
    clean_filename, 
    output_dir="./electrode_positions",
    simulator_grid_size=DEFAULT_SIMULATOR_GRID_SIZE,
    distance_between_electrodes=DEFAULT_DISTANCE_BETWEEN_ELECTRODES,
    electrode_diameter=DEFAULT_ELECTRODE_DIAMETER,
    stimulus=None
):
    """
    Write electrode positions to JSON and create visualization GDS file.
    
    Args:
        electrode_positions: Set or list of (x, y) tuples
        clean_filename: Filename without extension (e.g., 'MEA512')
        output_dir: Directory to write output files to
        simulator_grid_size: Tuple of (width, height) for the simulator grid
        distance_between_electrodes: Desired spacing between electrode centers
        electrode_diameter: Diameter of electrodes in micrometers
        stimulus: Optional stimulus electrode positions (currently unused)
    """
    adjusted_positions = adjust_electrode_positions(
        electrode_positions,
        distance_between_electrodes=distance_between_electrodes,
        simulator_grid_size=simulator_grid_size
    )

    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create new gds file for visualization
    new_lib = gdspy.GdsLibrary()
    new_cell = gdspy.Cell('Electrode_Positions')
    electrode_positions_with_labels = add_labels(adjusted_positions)
    for label, x, y in electrode_positions_with_labels:
        dot = gdspy.Round(
            (x, y),
            radius=electrode_diameter / 2,
            inner_radius=0, 
            number_of_points=60, 
            layer=2
        )
        new_cell.add(dot)

    min_x, min_y, max_x, max_y = draw_simulator_grid(new_cell, simulator_grid_size)
    draw_dish(
        radius=min(simulator_grid_size) / 2, 
        MEA=new_cell,
        simulator_grid_size=simulator_grid_size
    )
    new_lib.add(new_cell)
    new_lib.write_gds(output_path / f'electrode_positions_{clean_filename}.gds')

    # Write JSON
    json_path = output_path / f'electrode_positions_{clean_filename}.json'
    with open(json_path, 'w') as f:
        json.dump({
            "electrode_coordinates": [
                [i, x, y, 100.0] for i, x, y in electrode_positions_with_labels
            ],
            "bounding_box": [[min_x, min_y], [max_x, max_y]]
        }, f, indent=2)


def get_electrodes(
    file_name, 
    target_layer=2,
    output_dir="./electrode_positions",
    simulator_grid_size=DEFAULT_SIMULATOR_GRID_SIZE,
    distance_between_electrodes=DEFAULT_DISTANCE_BETWEEN_ELECTRODES,
    electrode_diameter=DEFAULT_ELECTRODE_DIAMETER
):
    """
    Extract electrode positions from a GDS file.
    
    Args:
        file_name: Path to the input GDS file
        target_layer: Layer number to extract electrodes from (default: 2)
        output_dir: Directory to write output files to
        simulator_grid_size: Tuple of (width, height) for the simulator grid
        distance_between_electrodes: Desired spacing between electrode centers
        electrode_diameter: Diameter of electrodes in micrometers
        
    Returns:
        Tuple of (electrode_positions, MEA_cell, gds_library, clean_filename)
        
    Raises:
        ValueError: If no cell containing 'MEA' is found in the GDS file
    """
    lib = gdspy.GdsLibrary(infile=file_name)
    keys = list(lib.cells.keys())
    mea_key = next((k for k in keys if 'MEA' in k), None)
    if mea_key is None:
        raise ValueError("No cell containing 'MEA' found in GDS file.")
    MEA = lib.cells[mea_key]

    clean_filename = Path(file_name).stem
    quant_electrodes = int(clean_filename.split('_')[0][3:])

    polygons = MEA.polygons
    polygons_filtered = [p for p in polygons if p.layers[0] == target_layer]

    bounding_boxes_electrodes = [p.get_bounding_box() for p in polygons_filtered]
    electrode_positions = remove_outliers(bounding_boxes_electrodes)
    electrode_positions = [get_center(bb) for bb in electrode_positions]

    # deduplicate with rounding tolerance
    electrode_positions = {(round(x, 3), round(y, 3)) for x, y in electrode_positions}
    
    # Optional validation (currently commented out)
    # if len(electrode_positions) != quant_electrodes:
    #     raise ValueError(
    #         f'Number of electrodes in GDS ({len(electrode_positions)}) '
    #         f'does not match expected ({quant_electrodes}).'
    #     )

    write_json(
        electrode_positions, 
        clean_filename,
        output_dir=output_dir,
        simulator_grid_size=simulator_grid_size,
        distance_between_electrodes=distance_between_electrodes,
        electrode_diameter=electrode_diameter
    )
    return electrode_positions, MEA, lib, clean_filename


def create_dots_confirmation(
    electrode_positions, 
    MEA, 
    lib, 
    clean_filename,
    output_dir="./electrode_positions",
    simulator_grid_size=DEFAULT_SIMULATOR_GRID_SIZE,
    distance_between_electrodes=DEFAULT_DISTANCE_BETWEEN_ELECTRODES
):
    """
    Create a confirmation GDS file with dots at electrode positions.
    
    Args:
        electrode_positions: Set or list of (x, y) tuples
        MEA: gdspy.Cell object containing the original MEA layout
        lib: gdspy.GdsLibrary object
        clean_filename: Filename without extension
        output_dir: Directory to write output files to
        simulator_grid_size: Tuple of (width, height) for the simulator grid
        distance_between_electrodes: Desired spacing between electrode centers
    """
    adjusted_positions = adjust_electrode_positions(
        electrode_positions,
        distance_between_electrodes=distance_between_electrodes,
        simulator_grid_size=simulator_grid_size
    )

    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # last 4 electrodes are assumed to be stimulus electrodes (if applicable)
    if len(adjusted_positions) > 4:
        stimulus_electrodes = adjusted_positions[-4:]
        normal_electrodes = adjusted_positions[:-4]
    else:
        stimulus_electrodes = []
        normal_electrodes = adjusted_positions

    for pos in stimulus_electrodes:
        box = gdspy.Rectangle(
            (pos[0] - 10, pos[1] - 10),
            (pos[0] + 10, pos[1] + 10), 
            layer=0
        )
        MEA.add(box)
    for pos in normal_electrodes:
        dot = gdspy.Round(
            pos, 
            radius=3, 
            inner_radius=0,
            number_of_points=16, 
            layer=0
        )
        MEA.add(dot)
    lib.write_gds(output_path / f'first_with_dots_{clean_filename}.gds')


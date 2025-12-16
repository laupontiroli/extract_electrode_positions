"""
Utility functions for MEA electrode extraction.
"""

import numpy as np
import gdspy


def add_labels(electrode_positions):
    """
    Add labels to electrode positions.
    
    Order = left-to-right, bottom-to-top based on coordinates.
    
    Args:
        electrode_positions: List of (x, y) tuples
        
    Returns:
        List of (index, x, y) tuples
    """
    # sort by y first (ascending), then x
    sorted_positions = sorted(electrode_positions, key=lambda p: (p[1], p[0]))
    positions_with_labels = [(i, x, y) for i, (x, y) in enumerate(sorted_positions)]
    return positions_with_labels


def get_center(bounding_box):
    """
    Calculate the center point of a bounding box.
    
    Args:
        bounding_box: Bounding box in the form [[x_min, y_min], [x_max, y_max]]
        
    Returns:
        Tuple of (center_x, center_y)
    """
    return ((bounding_box[0][0] + bounding_box[1][0]) / 2,
            (bounding_box[0][1] + bounding_box[1][1]) / 2)


def get_area_of_bounding_box(bounding_box):
    """
    Calculate the area of a bounding box.
    
    Args:
        bounding_box: Bounding box in the form [[x_min, y_min], [x_max, y_max]], 
                     or None if empty
        
    Returns:
        Area of the bounding box (width * height), or 0 if bounding_box is None
    """
    if bounding_box is None:
        return 0
    width = bounding_box[1][0] - bounding_box[0][0]
    height = bounding_box[1][1] - bounding_box[0][1]
    return width * height


def remove_outliers(electrode_positions):
    """
    Filter out electrodes with atypical dimensions based on statistical analysis.
    
    Keeps only electrodes with the most common width and height.
    
    Args:
        electrode_positions: List of bounding boxes in the form 
                           [[x_min, y_min], [x_max, y_max]]
        
    Returns:
        Filtered list of bounding boxes
        
    Raises:
        ValueError: If no bounding boxes match the most common dimensions
    """
    metrics = {}
    for bounding_box in electrode_positions:
        width = bounding_box[1][0] - bounding_box[0][0]
        height = bounding_box[1][1] - bounding_box[0][1]
        if (width, height) in metrics:
            metrics[(width, height)] += 1
        else:
            metrics[(width, height)] = 1
    most_common = max(metrics, key=metrics.get)
    filtered_bounding_boxes = [
        bb for bb in electrode_positions 
        if (bb[1][0] - bb[0][0], bb[1][1] - bb[0][1]) == most_common
    ]
    if len(filtered_bounding_boxes) == 0:
        raise ValueError('No bounding boxes found with the most common width and height.')
    return filtered_bounding_boxes


def draw_simulator_grid(MEA, simulator_grid_size=(4000, 4000)):
    """
    Draw the simulator grid bounding box.
    
    Args:
        MEA: gdspy.Cell object to add the grid to
        simulator_grid_size: Tuple of (width, height) in micrometers
        
    Returns:
        Tuple of (min_x, min_y, max_x, max_y)
    """
    min_x = 0
    max_x = simulator_grid_size[0]
    min_y = 0
    max_y = simulator_grid_size[1]
    box = gdspy.Rectangle((min_x, min_y), (max_x, max_y), layer=0)
    MEA.add(box)
    return min_x, min_y, max_x, max_y


def draw_dish(radius, MEA, simulator_grid_size=(4000, 4000)):
    """
    Draw a circular dish in the center of the simulator grid.
    
    Args:
        radius: Radius of the dish in micrometers
        MEA: gdspy.Cell object to add the dish to
        simulator_grid_size: Tuple of (width, height) in micrometers
    """
    center_x = simulator_grid_size[0] / 2
    center_y = simulator_grid_size[1] / 2
    dish = gdspy.Round(
        (center_x, center_y), 
        radius=radius, 
        layer=1,
        inner_radius=0, 
        number_of_points=120
    )
    MEA.add(dish)


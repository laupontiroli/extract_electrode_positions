import gdspy
import json
import numpy as np

FILE_NAME = 'MEA512.gds'

SIMULATOR_GRID_SIZE = (4000, 4000)  # in micrometers (4 mm x 4 mm)
DISTANCE_BETWEEN_ELECTRODES = 180
ELECTRODE_DIAMETER = 30  # in micrometers

def add_labels(electrode_positions): 
    '''
    Add labels to electrode positions.
    Order = left-to-right, bottom-to-top based on coordinates.
    '''
    # sort by y first (ascending), then x
    sorted_positions = sorted(electrode_positions, key=lambda p: (p[1], p[0]))
    positions_with_labels = [(i, x, y) for i, (x, y) in enumerate(sorted_positions)]
    return positions_with_labels

def adjust_electrode_positions(electrode_positions, stimulus=None):
    """
    Rescale and translate electrode positions so that:
    1. Distances between nearest neighbors match DISTANCE_BETWEEN_ELECTRODES (edge-to-edge).
    2. The MEA is centered in the simulator grid.
    """
    electrode_positions = np.array(list(electrode_positions), dtype=float)

    # --- Step 1: Normalize (make mean-centered) ---
    mean_x, mean_y = electrode_positions.mean(axis=0)
    centered = electrode_positions - np.array([mean_x, mean_y])

    # --- Step 2: Compute nearest-neighbor distance ---
    nearest_dists = []
    for i in range(len(centered)):
        dists_i = [np.linalg.norm(centered[i] - centered[j]) for j in range(len(centered)) if i != j]
        nearest_dists.append(min(dists_i))
    avg_spacing = np.median(nearest_dists)

    # --- Step 3: Desired spacing = distance between centers = gap + diameter ---
    desired_spacing = DISTANCE_BETWEEN_ELECTRODES

    # --- Step 4: Scale so spacing matches desired spacing ---
    scale_factor = desired_spacing / avg_spacing
    scaled = centered * scale_factor

    # --- Step 5: Shift so MEA is centered in simulator grid ---
    target_center = np.array(SIMULATOR_GRID_SIZE) / 2
    adjusted = scaled + target_center

    return [tuple(p) for p in adjusted]


def remove_outliers(electrode_positions):
    metrics = {}
    for bouding_box in electrode_positions:
        width = bouding_box[1][0] - bouding_box[0][0]
        height = bouding_box[1][1] - bouding_box[0][1]
        if (width, height) in metrics:
            metrics[(width, height)] += 1
        else:
            metrics[(width, height)] = 1
    most_common = max(metrics, key=metrics.get)
    filtered_bounding_boxes = [bb for bb in electrode_positions
                               if (bb[1][0] - bb[0][0], bb[1][1] - bb[0][1]) == most_common]
    if len(filtered_bounding_boxes) == 0:
        raise ValueError('No bounding boxes found with the most common width and height.')
    return filtered_bounding_boxes


def draw_simulator_grid(MEA):
    min_x = 0
    max_x = SIMULATOR_GRID_SIZE[0]
    min_y = 0
    max_y = SIMULATOR_GRID_SIZE[1]
    box = gdspy.Rectangle((min_x, min_y), (max_x, max_y), layer=0)
    MEA.add(box)
    return min_x, min_y, max_x, max_y


def draw_dish(radius, MEA):
    center_x = SIMULATOR_GRID_SIZE[0] / 2
    center_y = SIMULATOR_GRID_SIZE[1] / 2
    dish = gdspy.Round((center_x, center_y), radius=radius, layer=1,inner_radius=0, number_of_points=120)
    MEA.add(dish)



def write_json(electrode_positions, clean_filename, stimulus=None):
    adjusted_positions = adjust_electrode_positions(electrode_positions)

    # Create new gds file for visualization
    new_lib = gdspy.GdsLibrary()
    new_cell = gdspy.Cell('Electrode_Positions')
    electrode_positions_with_labels = add_labels(adjusted_positions)
    for label, x, y in electrode_positions_with_labels:
        dot = gdspy.Round((x, y),
                          radius=ELECTRODE_DIAMETER / 2,
                          inner_radius=0, number_of_points=60, layer=2)
        new_cell.add(dot)

    min_x, min_y, max_x, max_y = draw_simulator_grid(new_cell)
    draw_dish(radius=min(SIMULATOR_GRID_SIZE) / 2, MEA=new_cell)
    new_lib.add(new_cell)
    new_lib.write_gds(f'electrode_positions_{clean_filename}.gds')
    
    # Write JSON
    with open(f'electrode_positions_{clean_filename}.json', 'w') as f:
        json.dump({
            "electrode_coordinates": [
                [i, x, y, 100.0] for i, x, y in electrode_positions_with_labels
            ],
            "bounding_box": [[min_x, min_y], [max_x, max_y]]
        }, f, indent=2)


def get_center(bouding_box):
    return ((bouding_box[0][0] + bouding_box[1][0]) / 2,
            (bouding_box[0][1] + bouding_box[1][1]) / 2)


def get_area_of_bouding_box(bounding_box):
    if bounding_box is None:
        return 0
    width = bounding_box[1][0] - bounding_box[0][0]
    height = bounding_box[1][1] - bounding_box[0][1]
    return width * height


def get_electrodes(FILE_NAME, target_layer=2):
    lib = gdspy.GdsLibrary(infile=FILE_NAME)
    keys = list(lib.cells.keys())
    mea_key = next((k for k in keys if 'MEA' in k), None)
    if mea_key is None:
        raise ValueError("No cell containing 'MEA' found in GDS file.")
    MEA = lib.cells[mea_key]

    clean_filename = FILE_NAME.split('.')[0]
    quant_electrodes = int(clean_filename.split('_')[0][3:])

    polygons = MEA.polygons
    polygons_filtered = [p for p in polygons if p.layers[0] == target_layer]

    bounding_boxes_electrodes = [p.get_bounding_box() for p in polygons_filtered]
    electrode_positions = remove_outliers(bounding_boxes_electrodes)
    electrode_positions = [get_center(bb) for bb in electrode_positions]

    # deduplicate with rounding tolerance
    electrode_positions = {(round(x, 3), round(y, 3)) for x, y in electrode_positions}
    
    # if len(electrode_positions) != quant_electrodes:
    #     raise ValueError(
    #         f'Number of electrodes in GDS ({len(electrode_positions)}) '
    #         f'does not match expected ({quant_electrodes}).'
    #     )

    write_json(electrode_positions, clean_filename)
    return electrode_positions, MEA, lib, clean_filename


def create_dots_confirmation(electrode_positions, MEA, lib, clean_filename):
    adjusted_positions = adjust_electrode_positions(electrode_positions)

    # last 4 electrodes are assumed to be stimulus electrodes (if applicable)
    if len(adjusted_positions) > 4:
        stimulus_electrodes = adjusted_positions[-4:]
        normal_electrodes = adjusted_positions[:-4]
    else:
        stimulus_electrodes = []
        normal_electrodes = adjusted_positions

    for pos in stimulus_electrodes:
        box = gdspy.Rectangle((pos[0] - 10, pos[1] - 10),
                              (pos[0] + 10, pos[1] + 10), layer=0)
        MEA.add(box)
    for pos in normal_electrodes:
        dot = gdspy.Round(pos, radius=3, inner_radius=0,
                          number_of_points=16, layer=0)
        MEA.add(dot)
    lib.write_gds(f'first_with_dots_{clean_filename}.gds')


if __name__ == '__main__':
    electrode_positions, MEA, lib, clean_filename = get_electrodes(FILE_NAME)
    create_dots_confirmation(electrode_positions, MEA, lib, clean_filename)
    print(f'Electrode positions saved to electrode_positions_{FILE_NAME.split(".")[0]}.json')

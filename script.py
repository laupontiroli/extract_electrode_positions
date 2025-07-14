import gdspy
import json

FILE_NAME = 'MEA512.gds'

def adjust_electrode_positions(electrode_positions):
    '''
    Function to adjust the electrode positions relative to the simulator grid.
    '''
    min_x = min(bb[0] for bb in electrode_positions) - 200
    min_y = min(bb[1] for bb in electrode_positions) - 200
    # min_x and min_y are the coordinates of the bottom left corner of the bounding box
    adjusted_positions = []
    for bb in electrode_positions:
        # adjust the position of the electrode to the bottom left corner of the bounding box
        adjusted_x = bb[0] - min_x
        adjusted_y = bb[1] - min_y
        adjusted_positions.append((adjusted_x, adjusted_y))
    return adjusted_positions
        
def remove_outliers(electrode_positions):
    metrics = {}
    for bouding_box in electrode_positions:
        # get the width and height of the bounding box
        width = bouding_box[1][0] - bouding_box[0][0]
        height = bouding_box[1][1] - bouding_box[0][1]
        if (width, height) in metrics:
            metrics[(width, height)] += 1
        else:
            metrics[(width, height)] = 1
    # get the most common width and height
    most_common = max(metrics, key=metrics.get)
    # exclude the bounding boxes that do not match the most common width and height
    filtered_bounding_boxes = [bb for bb in electrode_positions if (bb[1][0] - bb[0][0], bb[1][1] - bb[0][1]) == most_common]
    if len(filtered_bounding_boxes) == 0:
        raise ValueError('No bounding boxes found with the most common width and height.')
    return filtered_bounding_boxes



def draw_big_bounding_box(electrode_positions, MEA):
    '''
    Function to draw a big bounding box around the electrodes.
    
    Used for debugging purposes to visualize the area covered by the electrodes.
    '''
    # get the min and max x and y coordinates of the bounding boxes
    min_x = min(bb[0] for bb in electrode_positions) - 200
    max_x = max(bb[0] for bb in electrode_positions) + 200
    min_y = min(bb[1] for bb in electrode_positions) - 200
    max_y = max(bb[1] for bb in electrode_positions) + 200
    print(f'Bounding box coordinates: ({min_x}, {min_y}), ({max_x}, {max_y})')
    # create a polygon with the bounding box coordinates
    bounding_box = gdspy.Polygon([(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)], layer=3)
    
    # add the bounding box to the MEA cell
    MEA.add(bounding_box)
    return min_x, min_y, max_x, max_y

def write_json(electrode_positions, clean_filename):
    adjusted_positions = adjust_electrode_positions(electrode_positions)
    #create new gds file to visualize the electrode positions
    new_lib = gdspy.GdsLibrary()
    new_cell = gdspy.Cell('Electrode_Positions')
    for electrode in adjusted_positions:
        dot = gdspy.Round((electrode[0], electrode[1]), radius=20, inner_radius=0, number_of_points=60, layer=0)
        new_cell.add(dot)
    new_lib.add(new_cell)
    min_x, min_y, max_x, max_y = draw_big_bounding_box(adjusted_positions, new_cell)
    new_lib.write_gds(f'electrode_positions_{clean_filename}.gds')
    with open(f'electrode_positions_{clean_filename}.json', 'w') as f:
        f.write('{ "electrode_coordinates": [ \n')
        i = 0.0
        for electrode in adjusted_positions:
            if i > 0:
                f.write(',\n')
            f.write(f'[{i},{electrode[0]}, {electrode[1]},100.0]')
            i += 1.0   
        f.write('\n')
        f.write(f'],\n "bounding_box": [\n [{min_x}, {min_y}],\n [{max_x}, {max_y}]\n]\n')
        f.write('}')
        f.close()
def get_center(bouding_box):
    '''
    Function to get the center position of an electrode given its bounding box.
    '''
    # using the bounding box to get the center position of the electrode
    return ((bouding_box[0][0] + bouding_box[1][0]) / 2, (bouding_box[0][1] + bouding_box[1][1]) / 2)

def get_electrodes(FILE_NAME):
    '''
    Function to get the electrode positions from the MEA cell in the GDS file.
    '''
    lib = gdspy.GdsLibrary(infile=FILE_NAME)

    #get the cell with the name 'MEA_Standard' that contains the electrode polygons
    keys = list(lib.cells.keys())
    for key in keys:
        if 'MEA' in key:
            mea_key = key
    MEA = lib.cells[mea_key]
    clean_filename = FILE_NAME.split('.')[0]
    quant_electrodes = clean_filename.split('_')[0][3:]
    # get all polygons in the cell
    polygons = MEA.polygons

    # get polygons with 64 points, that are the electrodes

    polygons_64 = [p for p in polygons if (len(p.polygons[0]) == 64 or len(p.polygons[0]) == 60) and p.layers[0] == 2]

    #get center position of electrodes
    bouding_boxes_electrodes = [p.get_bounding_box() for p in polygons_64]
    electrode_positions = remove_outliers(bouding_boxes_electrodes)
    electrode_positions = [get_center(bb) for bb in electrode_positions]
    electrode_positions = set(electrode_positions)  # remove duplicates
    # draw a big bounding box around the electrodes
    
    if len(electrode_positions) != int(quant_electrodes):
        raise ValueError(f'Number of electrodes in the GDS file ({len(electrode_positions)}) does not match the expected number ({quant_electrodes}).')
    # # write the positions to a json file
    write_json(electrode_positions, clean_filename)
    # return the electrode positions and the MEA cell 
    return electrode_positions, MEA, lib,clean_filename

# --- confirmation ---
# add dots to the center to check the positions
def create_dots_confirmation(electrode_positions,MEA,lib,clean_filename):
    for pos in electrode_positions:
        dot = gdspy.Round(pos, radius=3, inner_radius=0, number_of_points=16, layer=0)
        MEA.add(dot)
    lib.write_gds(f'first_with_dots_{clean_filename}.gds')
    

if __name__ == '__main__':
    electrode_positions, MEA, lib, clean_filename= get_electrodes(FILE_NAME)
    create_dots_confirmation(electrode_positions,MEA,lib,clean_filename)
    print(f'Electrode positions saved to electrode_positions_{FILE_NAME.split(".")[0]}.json')

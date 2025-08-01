import gdspy
import json

FILE_NAME = 'MEA128_rec.gds'

def adjust_electrode_positions(electrode_positions, stimulus):
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

    # adjust the stimulus positions
    adjusted_stimulus = []
    for pos in stimulus:
        adjusted_x0 = pos[0][0] - min_x
        adjusted_y0 = pos[0][1] - min_y
        adjusted_x1 = pos[1][0] - min_x
        adjusted_y1 = pos[1][1] - min_y
        adjusted_stimulus.append(((adjusted_x0, adjusted_y0), (adjusted_x1, adjusted_y1)))
    return adjusted_positions,adjusted_stimulus

def resize_positions(electrode_positions, stimulus):
    # resize so that the positions are in the center of a 1800x1800 grid
    adjusted_positions = []
    for bb in electrode_positions:
        adjusted_x = bb[0] / 2 + 450
        adjusted_y = bb[1] / 2 + 100
        adjusted_positions.append((adjusted_x, adjusted_y))
    # adjust the stimulus positions
    adjusted_stimulus = []
    for pos in stimulus:
        adjusted_x0 = pos[0][0] / 2 + 450
        adjusted_y0 = pos[0][1] / 2 + 100
        adjusted_x1 = pos[1][0] / 2 + 450
        adjusted_y1 = pos[1][1] / 2 + 100
        adjusted_stimulus.append(((adjusted_x0, adjusted_y0), (adjusted_x1, adjusted_y1)))
    
    return adjusted_positions, adjusted_stimulus
 

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
    min_x = min(bb[0] for bb in electrode_positions) - 100
    max_x = max(bb[0] for bb in electrode_positions) + 100
    min_y = min(bb[1] for bb in electrode_positions) - 100
    max_y = max(bb[1] for bb in electrode_positions) + 100
    # create a polygon with the bounding box coordinates
    bounding_box = gdspy.Polygon([(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)], layer=3)
    
    # add the bounding box to the MEA cell
    MEA.add(bounding_box)
    return min_x, min_y, max_x, max_y

def write_json(electrode_positions, clean_filename,stimulus):
    adjusted_positions,adjusted_stimulus = adjust_electrode_positions(electrode_positions,stimulus)
    # resize the positions to fit the simulator grid
    adjusted_positions, adjusted_stimulus = resize_positions(adjusted_positions, adjusted_stimulus)
    #create new gds file to visualize the electrode positions
    new_lib = gdspy.GdsLibrary()
    new_cell = gdspy.Cell('Electrode_Positions')
    for electrode in adjusted_positions:
        dot = gdspy.Round((electrode[0], electrode[1]), radius=10, inner_radius=0, number_of_points=60, layer=0)
        new_cell.add(dot)
    for pos in adjusted_stimulus:
        box = gdspy.Rectangle((pos[0][0], pos[0][1]), (pos[1][0], pos[1][1]), layer=2)
        new_cell.add(box)
    new_lib.add(new_cell)
    min_x, min_y, max_x, max_y = draw_big_bounding_box(adjusted_positions, new_cell)
    new_lib.write_gds(f'electrode_positions_{clean_filename}.gds')
    adjusted_stimulus_centers = [get_center(pos) for pos in adjusted_stimulus]
    with open(f'electrode_positions_{clean_filename}.json', 'w') as f:
        f.write('{ "electrode_coordinates": [ \n')
        i = 0.0
        for electrode in adjusted_positions:
            if i > 0:
                f.write(',\n')
            f.write(f'[{i},{electrode[0]}, {electrode[1]},100.0]')
            i += 1.0  
        print(i)
        for pos in adjusted_stimulus_centers:
            print("Adding stimulus position:", pos)
            f.write(',\n')
            f.write(f'[{i},{pos[0]}, {pos[1]},100.0]')
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

def get_area_of_bouding_box(bounding_box):
    if bounding_box is None:
        return 0
    width = bounding_box[1][0] - bounding_box[0][0]
    height = bounding_box[1][1] - bounding_box[0][1]
    return width * height

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
    
    stimulus = [p for p in polygons if get_area_of_bouding_box(p.get_bounding_box()) == p.area() and p.layers[0] == 2]

    unique_stimulus = {}
    seen_bounding_boxes = set()

    for p in stimulus:
        bounding_box = tuple(map(tuple, p.get_bounding_box()))
        if bounding_box not in seen_bounding_boxes:
            seen_bounding_boxes.add(bounding_box)
            unique_stimulus[p] = bounding_box

    stimulus = list(unique_stimulus.values())
    
    
    #get center position of electrodes
    bounding_boxes_electrodes = [p.get_bounding_box() for p in polygons_64]
    electrode_positions = remove_outliers(bounding_boxes_electrodes)
    electrode_positions = [get_center(bb) for bb in electrode_positions]
    electrode_positions = set(electrode_positions)  # remove duplicates
    # draw a big bounding box around the electrodes
    
    if len(electrode_positions) != int(quant_electrodes):
        raise ValueError(f'Number of electrodes in the GDS file ({len(electrode_positions)}) does not match the expected number ({quant_electrodes}).')
    
    #add stimulus to eledtrode positions
    # # write the positions to a json file
    write_json(electrode_positions, clean_filename,stimulus)
    # return the electrode positions and the MEA cell 
    return electrode_positions, MEA, lib,clean_filename

# --- confirmation ---
# add dots to the center to check the positions
def create_dots_confirmation(electrode_positions,MEA,lib,clean_filename):
    # last 4 electodes are the stimulus electrodes 
    stimulus_electrodes = list(electrode_positions)[-4:]
    
    electrode_positions = list(electrode_positions)[:-4]
    # draw a dot in the center of each electrode
    for pos in stimulus_electrodes:
        box = gdspy.Rectangle((pos[0] - 10, pos[1] - 10), (pos[0] + 10, pos[1] + 10), layer=0)
        MEA.add(box)
    for pos in electrode_positions:
        dot = gdspy.Round(pos, radius=3, inner_radius=0, number_of_points=16, layer=0)
        MEA.add(dot)
    lib.write_gds(f'first_with_dots_{clean_filename}.gds')
    

if __name__ == '__main__':
    electrode_positions, MEA, lib, clean_filename= get_electrodes(FILE_NAME)
    create_dots_confirmation(electrode_positions,MEA,lib,clean_filename)
    print(f'Electrode positions saved to electrode_positions_{FILE_NAME.split(".")[0]}.json')

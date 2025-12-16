# Examples and Tutorials

This directory contains example code and tutorials for using the MEA Electrode Extractor.

## Contents

### `tutorial.ipynb`

A Jupyter notebook demonstrating basic usage of the MEA extraction tools. The tutorial covers:

1. **Loading GDS files**: How to open and inspect GDS files using gdspy
2. **Finding MEA cells**: Locating cells containing electrode arrays
3. **Extracting polygons**: Identifying electrode polygons by layer and shape
4. **Calculating positions**: Computing electrode center positions from bounding boxes
5. **Visualization**: Adding confirmation markers to verify extraction

## Running the Tutorial

### Prerequisites

Install Jupyter and dependencies:

```bash
pip install jupyter ipykernel
pip install -r requirements.txt
```

### Launch Jupyter

```bash
jupyter notebook examples/tutorial.ipynb
```

Or use JupyterLab:

```bash
jupyter lab examples/tutorial.ipynb
```

## Example Usage

### Basic Extraction

```python
import gdspy
from src.mea_extractor import get_electrodes

# Extract electrodes from a GDS file
electrode_positions, MEA, lib, clean_filename = get_electrodes(
    'data/input/MEA59.gds'
)

print(f"Found {len(electrode_positions)} electrodes")
```

### Custom Parameters

```python
from src.mea_extractor import get_electrodes

# Extract with custom parameters
electrode_positions, MEA, lib, clean_filename = get_electrodes(
    'data/input/MEA256.gds',
    target_layer=2,
    output_dir='./custom_output',
    simulator_grid_size=(5000, 5000),
    distance_between_electrodes=200,
    electrode_diameter=40
)
```

### Manual Processing

```python
import gdspy
from src.mea_extractor.utils import get_center, remove_outliers

# Load GDS file
lib = gdspy.GdsLibrary(infile='data/input/MEA128.gds')
MEA = lib.cells['MEA_128']

# Get polygons on layer 2
polygons = [p for p in MEA.polygons if p.layers[0] == 2]

# Get bounding boxes
bounding_boxes = [p.get_bounding_box() for p in polygons]

# Remove outliers
filtered_boxes = remove_outliers(bounding_boxes)

# Get centers
positions = [get_center(bb) for bb in filtered_boxes]

print(f"Extracted {len(positions)} electrode positions")
```

## Additional Examples

### Batch Processing

```python
from pathlib import Path
from src.mea_extractor import get_electrodes

# Process all GDS files in a directory
input_dir = Path('data/input')
output_dir = Path('results')

for gds_file in input_dir.glob('*.GDS'):
    print(f"Processing {gds_file.name}...")
    try:
        get_electrodes(
            str(gds_file),
            output_dir=str(output_dir)
        )
        print(f"  ✓ Success")
    except Exception as e:
        print(f"  ✗ Error: {e}")
```

### Reading Output JSON

```python
import json

# Read extracted positions
with open('electrode_positions/electrode_positions_MEA512.json', 'r') as f:
    data = json.load(f)

electrodes = data['electrode_coordinates']
bounding_box = data['bounding_box']

print(f"Found {len(electrodes)} electrodes")
print(f"Bounding box: {bounding_box}")

# Access individual electrode
for idx, x, y, z in electrodes:
    print(f"Electrode {idx}: ({x}, {y}, {z})")
```

## Tips

1. **Layer Selection**: Different MEA designs may use different layers. Check your GDS file structure first.

2. **Grid Size**: Adjust `simulator_grid_size` to match your simulation environment.

3. **Spacing**: The `distance_between_electrodes` parameter controls the final spacing after scaling. This should match your physical electrode spacing.

4. **Visualization**: Always check the generated `first_with_dots_*.gds` file to verify extraction accuracy.

5. **Error Handling**: The extraction may fail if:
   - No MEA cell is found (check cell names)
   - Electrodes are on a different layer (use `--layer` option)
   - File format is incorrect

## Contributing Examples

If you have useful examples or tutorials, please add them to this directory with descriptive names and README documentation.


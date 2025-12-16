# MEA Electrode Position Extractor

A Python package for automatically extracting electrode positions from GDS (GDSII) files containing MEA (Microelectrode Array) layouts and converting these positions into JSON format suitable for neural simulations.

## Overview

The MEA Electrode Extractor processes semiconductor layout files (GDS format) containing microelectrode array designs. It identifies recording electrodes and stimulation electrodes, extracts their precise coordinates, and outputs them in a standardized JSON format for use in neural simulation software.

## Features

- **Automatic electrode detection**: Identifies and extracts recording electrode positions from polygonal shapes in GDS files
- **Stimulus electrode detection**: Automatically identifies rectangular electrodes used for stimulation
- **Outlier removal**: Filters out electrodes with atypical dimensions based on statistical analysis
- **Coordinate adjustment**: Repositions and rescales coordinates to fit simulator grid (default: 4000x4000 μm)
- **Visual confirmation**: Generates GDS files with dots at electrode positions for visual verification
- **JSON export**: Saves final coordinates in structured JSON format
- **Command-line interface**: Easy-to-use CLI for batch processing
- **Python package**: Importable module for integration into other projects

## Installation

### Requirements

- Python 3.7+
- See `requirements.txt` for dependencies

### Setup

```bash
# Clone or download the repository
cd extract_electrode_positions

# Install dependencies
pip install -r requirements.txt
```

## Project Structure

```
extract_electrode_positions/
├── README.md                    # This file
├── requirements.txt              # Python dependencies
├── .gitignore                   # Git ignore rules
├── src/
│   └── mea_extractor/           # Main package
│       ├── __init__.py
│       ├── extractor.py         # Core extraction logic
│       └── utils.py             # Utility functions
├── scripts/
│   └── extract_electrodes.py   # CLI entry point
├── data/
│   └── input/                   # Input GDS files
├── electrode_positions/         # Output directory (generated files)
├── eval_mea/                    # Evaluation and mapping tools
│   ├── README.md
│   ├── eval_mea.py
│   ├── data/                    # Evaluation data files
│   └── outputs/                 # Evaluation outputs
└── examples/
    ├── README.md
    └── tutorial.ipynb           # Tutorial notebook
```

## Usage

### Command-Line Interface

The easiest way to use the tool is via the command-line interface:

```bash
python scripts/extract_electrodes.py data/input/MEA512.gds
```

#### Options

- `--output-dir`: Directory to write output files (default: `./electrode_positions`)
- `--layer`: Layer number to extract electrodes from (default: `2`)
- `--grid-size WIDTH HEIGHT`: Simulator grid size in micrometers (default: `4000 4000`)
- `--electrode-spacing`: Distance between electrode centers in micrometers (default: `180`)
- `--electrode-diameter`: Electrode diameter in micrometers (default: `30`)
- `--no-confirmation`: Skip creating confirmation GDS file

#### Example

```bash
python scripts/extract_electrodes.py data/input/MEA256.gds \
    --output-dir ./results \
    --grid-size 4000 4000 \
    --electrode-spacing 180
```

### Python API

You can also use the package as a Python module:

```python
from src.mea_extractor import get_electrodes, create_dots_confirmation

# Extract electrodes
electrode_positions, MEA, lib, clean_filename = get_electrodes(
    'data/input/MEA512.gds',
    target_layer=2,
    output_dir='./electrode_positions',
    simulator_grid_size=(4000, 4000),
    distance_between_electrodes=180,
    electrode_diameter=30
)

# Create confirmation visualization
create_dots_confirmation(
    electrode_positions,
    MEA,
    lib,
    clean_filename,
    output_dir='./electrode_positions'
)
```

## Input File Requirements

- **File format**: GDS/GDSII format
- **Naming convention**: The filename should contain the number of electrodes (e.g., `MEA59.gds` for 59 electrodes)
- **Layer requirements**:
  - Electrodes should be on layer 2 (configurable via `--layer`)
  - Recording electrodes: Polygons with consistent dimensions
  - Stimulus electrodes: Rectangular shapes (if present)
- **Cell naming**: Must contain a cell with 'MEA' in its name

## Output Files

The script generates three files in the output directory:

1. **`electrode_positions_[filename].json`**: Main output file containing:
   - Electrode coordinates in simulator format
   - Bounding box information
   - Indexed electrode positions

2. **`electrode_positions_[filename].gds`**: Visualization file showing:
   - Dots at recording electrode positions (layer 2)
   - Simulator grid bounding box (layer 0)
   - Dish outline (layer 1)

3. **`first_with_dots_[filename].gds`**: Confirmation file with:
   - Original MEA layout plus confirmation dots
   - Visual verification of detected positions

## JSON Output Format

```json
{
  "electrode_coordinates": [
    [0, 2000.5, 2000.7, 100.0],
    [1, 2180.2, 2000.3, 100.0],
    ...
  ],
  "bounding_box": [
    [0, 0],
    [4000, 4000]
  ]
}
```

Each electrode entry contains:
- `[index, x_coordinate, y_coordinate, z_coordinate]`
- Coordinates are sorted left-to-right, bottom-to-top
- Recording electrodes are listed first, followed by stimulus electrodes (if any)

## Troubleshooting

### Common Issues

1. **"No bounding boxes found with the most common width and height"**
   - Check if electrodes are on the correct layer (use `--layer` option)
   - Verify electrode shapes are consistent polygons

2. **"No cell containing 'MEA' found in GDS file"**
   - Verify GDS file contains a cell with 'MEA' in its name
   - Check cell naming convention in your GDS file

3. **Import errors**
   - Ensure you're running from the project root directory
   - Check that all dependencies are installed: `pip install -r requirements.txt`

### Debugging

- Check the generated `first_with_dots_*.gds` file to verify electrode detection
- Use the `electrode_positions_*.gds` file to confirm coordinate transformation
- Enable verbose output by modifying the script

## Customization

### Changing Default Parameters

You can modify default parameters in `src/mea_extractor/extractor.py`:

```python
DEFAULT_SIMULATOR_GRID_SIZE = (4000, 4000)
DEFAULT_DISTANCE_BETWEEN_ELECTRODES = 180
DEFAULT_ELECTRODE_DIAMETER = 30
```

### Custom Layer Assignment

Use the `--layer` command-line option or pass `target_layer` parameter in the API.

## Technical Notes

- **Coordinate system**: Uses bottom-left origin with positive X right, positive Y up
- **Units**: Coordinates are in micrometers (μm)
- **Precision**: Maintains full floating-point precision in JSON output
- **Memory usage**: Processes entire GDS file in memory; suitable for typical MEA files
- **Grid centering**: Electrodes are automatically centered in the simulator grid

## Related Tools

- **eval_mea/**: Evaluation and mapping validation tools
- **examples/**: Tutorial notebook and examples

## License

This tool is designed for research and educational purposes. Ensure compliance with your organization's data handling policies when processing proprietary GDS files.

## Contributing

When modifying the code:
1. Maintain the existing function interfaces for compatibility
2. Add appropriate error handling for edge cases
3. Update this documentation for any new features
4. Test with multiple GDS file formats before committing changes
5. Follow the existing code structure and style


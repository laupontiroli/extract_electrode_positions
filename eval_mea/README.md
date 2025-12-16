# MEA Evaluation and Mapping Tools

This directory contains tools for evaluating and validating electrode mappings between different MEA numbering systems.

## Overview

The `eval_mea.py` script compares electrode mappings from old and new numbering systems, validates them against a CSV reference, and generates visualization files for electrode positions from YAML configuration files.

## Directory Structure

```
eval_mea/
├── README.md                    # This file
├── eval_mea.py                  # Main evaluation script
├── eval_difference.py           # YAML file comparison tool
├── data/                        # Input data files
│   ├── 512_long_mea_6x.yaml    # YAML file with electrode positions
│   ├── 512_long_mea_6x_V2.yaml # V2 version of YAML file
│   ├── 6x_mapping.pages        # Mapping reference files
│   ├── longmea6x_old_device.pages
│   └── mea_map.csv             # CSV mapping reference (old -> new)
└── outputs/                     # Generated output files
    ├── duplicate_old_numbers.csv
    ├── duplicate_new_numbers.csv
    ├── unused_csv_old.csv
    ├── mismatches.csv
    ├── missing_old_entries.csv
    ├── MEA_with_electrodes.gds
    └── yaml_differences.txt     # YAML comparison report
```

## Features

1. **Mapping Validation**: Compares OLD_MAPPING and NEW_MAPPING arrays against a CSV reference
2. **Duplicate Detection**: Identifies duplicate electrode numbers in both mapping arrays
3. **Mismatch Detection**: Finds positions where mappings don't match the CSV reference
4. **Grid Filling**: Infers missing electrode positions from partial YAML data
5. **Visualization**: Generates GDS files showing electrode positions
6. **YAML Comparison**: Compares two YAML files and extracts detailed differences

## Usage

### eval_mea.py - Mapping Validation

```bash
cd eval_mea
python eval_mea.py
```

The script will:
1. Compare the hardcoded OLD_MAPPING and NEW_MAPPING arrays against `data/mea_map.csv`
2. Generate reports for duplicates, mismatches, and missing entries
3. Load electrode positions from `data/512_long_mea_6x.yaml`
4. Fill in missing positions using grid inference
5. Generate a GDS visualization file in `outputs/MEA_with_electrodes.gds`

### eval_difference.py - YAML File Comparison

Compare two YAML files to find differences:

```bash
cd eval_mea
python eval_difference.py
```

This will compare `data/512_long_mea_6x.yaml` and `data/512_long_mea_6x_V2.yaml` by default.

You can also specify custom files:

```bash
python eval_difference.py data/file1.yaml data/file2.yaml
```

The script will:
1. Load both YAML files
2. Compare all fields (description, dim, electrode_name, pitch, plane, pos)
3. For position arrays, compare each coordinate with tolerance for floating-point differences
4. Generate a detailed report in `outputs/yaml_differences.txt`

The report includes:
- Field-by-field comparison
- Position-by-position differences (shows first 50, with count of total)
- Positions that exist in one file but not the other
- Summary statistics

### Input Files

#### CSV Mapping File (`data/mea_map.csv`)

Must contain two columns:
- `old`: Old electrode number
- `new`: Expected new electrode number

Example:
```csv
old,new
1,256
2,1
3,2
...
```

#### YAML Position File (`data/512_long_mea_6x.yaml`)

Should contain a `pos` key with a list of `[x, y]` coordinates:

```yaml
pos:
  - [100.0, 200.0]
  - [180.0, 200.0]
  - [100.0, 380.0]
  ...
```

## Output Files

All output files are written to the `outputs/` directory:

- **`duplicate_old_numbers.csv`**: Electrode numbers that appear multiple times in OLD_MAPPING
- **`duplicate_new_numbers.csv`**: Electrode numbers that appear multiple times in NEW_MAPPING
- **`unused_csv_old.csv`**: Old electrode numbers in CSV that never appear in OLD_MAPPING
- **`mismatches.csv`**: Positions where NEW_MAPPING doesn't match CSV expectations
  - Columns: `row`, `col`, `old`, `expected_new`, `actual_new`
- **`missing_old_entries.csv`**: Old values in arrays that aren't in the CSV
  - Columns: `row`, `col`, `old`, `actual_new`
- **`MEA_with_electrodes.gds`**: Visualization file with electrode positions
- **`yaml_differences.txt`**: Detailed comparison report between two YAML files (from eval_difference.py)

## Functions

### `compare_mappings()`

Validates the mapping arrays against the CSV reference:
- Checks for duplicates in both arrays
- Compares each position against CSV expectations
- Reports mismatches and missing entries
- Exits with error code 1 if mismatches are found

### `get_positions_from_yaml(yaml_file)`

Extracts electrode positions from a YAML file:
- Reads the `pos` key
- Filters out invalid/null positions
- Returns list of `(x, y)` tuples

### `fill_missing_positions_compact(known, pitch=None, tol=1e-6)`

Infers missing electrode positions on a rectangular grid:
- Analyzes known positions to determine grid spacing
- Fills in missing grid points
- Returns complete list of positions

### `draw_electrodes(MEA, electrode_positions)`

Draws electrode positions as circles in a GDS cell:
- Creates circular electrodes (30 μm diameter)
- Adds them to the specified GDS cell

## Configuration

Constants defined in the script:

```python
SIMULATOR_GRID_SIZE = (4000, 4000)  # in micrometers
ELECTRODE_DIAMETER = 30  # in micrometers
```

## Troubleshooting

### CSV Not Found

If you see: `"CSV not found at ..."`

- Ensure `data/mea_map.csv` exists
- Check that the file has `old` and `new` columns

### YAML File Not Found

If you see: `"FileNotFoundError"`

- Ensure `data/512_long_mea_6x.yaml` exists
- Check file path relative to script location

### Mapping Mismatches

If mismatches are found:
1. Review `outputs/mismatches.csv` for details
2. Check if OLD_MAPPING and NEW_MAPPING arrays are correct
3. Verify CSV mapping file is up to date
4. Script will exit with error code 1 if mismatches exist

## Notes

- The OLD_MAPPING and NEW_MAPPING arrays are hardcoded in the script
- These should be updated if electrode numbering changes
- The script assumes a rectangular grid for position inference
- Grid pitch is automatically inferred if not specified

## Integration

This tool is designed to work alongside the main MEA extraction tool:
- Use the main extractor to get electrode positions from GDS files
- Use this tool to validate mappings and generate visualizations
- Output GDS files can be viewed in GDS viewers (e.g., KLayout)


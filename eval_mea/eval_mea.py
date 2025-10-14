import gdspy
import pandas as pd
import numpy as np
import sys
from pathlib import Path
import yaml

# --- paste your two mapping arrays here (from the .pages) ---
OLD_MAPPING = [
[178,  79, 177,  80, 208,  49, 207,  50],
[179,  78,  77, 180,  52, 205, 206,  51],
[181,  76,  75, 182,  54, 203, 204,  53],
[183,  74,  73, 184,  56, 201, 202,  55],
[185,  72,  71, 186,  58, 199, 200,  57],
[187,  70,  69, 188,  60, 197, 198,  59],
[189,  68,  67, 190,  62, 195, 194,  61],
[191,  66,  65, 192,  64, 255, 196,  63],
[129, 128, 127, 130,   2, 193, 256,   1],
[131, 126, 125, 132,   4, 253, 252,   3],
[133, 124, 123, 134,   6, 249, 254,   5],
[135, 122, 121, 136,   8, 251, 250,   7],
[137, 120, 119, 138,  10, 247, 246,   9],
[139, 118, 117, 140,  12, 243, 248,  11],
[141, 116, 115, 142,  14, 245, 244,  13],
[143, 114, 113, 144,  16, 241, 242,  15],
[145, 112, 111, 146,  18, 239, 240,  17],
[147, 110, 109, 148,  20, 237, 238,  19],
[149, 108, 107, 150,  22, 235, 236,  21],
[151, 106, 105, 152,  24, 233, 234,  23],
[153, 104, 103, 154,  26, 231, 232,  25],
[155, 102, 101, 156,  28, 229, 230,  27],
[157, 100,  99, 158,  30, 227, 228,  29],
[159,  98,  97, 160,  32, 225, 226,  31],
[161,  96,  95, 162,  34, 223, 224,  33],
[163,  94,  93, 164,  36, 221, 222,  35],
[165,  92,  91, 166,  38, 219, 220,  37],
[167,  90,  89, 168,  40, 217, 218,  39],
[169,  88,  87, 170,  42, 215, 216,  41],
[171,  86,  85, 172,  44, 213, 214,  43],
[173,  84,  83, 174,  46, 211, 212,  45],
[175,  82,  81, 176,  48, 209, 210,  47],
[466, 304, 303, 467, 339, 431, 432, 338],
[300, 469, 470, 465, 337, 342, 341, 428],
[302, 473, 465, 301, 429, 340, 345, 430],
[298, 471, 472, 297, 425, 344, 343, 426],
[294, 475, 476, 299, 427, 248, 247, 422],
[296, 479, 474, 295, 423, 346, 351, 424],
[292, 477, 478, 291, 419, 350, 349, 420],
[288, 482, 482, 293, 421, 354, 353, 416],
[290, 485, 480, 289, 417, 352, 357, 418],
[286, 483, 484, 285, 413, 356, 355, 414],
[282, 487, 488, 287, 415, 360, 259, 410],
[284, 491, 480, 283, 411, 358, 363, 412],
[280, 489, 490, 279, 407, 362, 361, 408],
[276, 493, 494, 281, 409, 366, 365, 404],
[278, 273, 492, 277, 405, 364, 401, 406],
[495, 275, 274, 496, 368, 402, 403, 367],
[498, 272, 271, 499, 371, 399, 400, 370],
[268, 501, 502, 497, 369, 374, 373, 398],
[270, 505, 500, 269, 397, 372, 377, 396],
[266, 503, 504, 265, 395, 376, 375, 394],
[262, 507, 508, 267, 393, 380, 379, 392],
[264, 511, 506, 263, 391, 378, 383, 390],
[260, 509, 510, 259, 389, 382, 381, 388],
[320, 449, 450, 261, 387, 322, 321, 386],
[258, 453, 512, 257, 385, 384, 325, 448],
[318, 451, 452, 317, 447, 324, 323, 446],
[314, 455, 456, 319, 445, 328, 327, 442],
[316, 459, 454, 315, 443, 326, 331, 444],
[312, 457, 458, 311, 439, 330, 329, 440],
[308, 461, 462, 313, 441, 334, 333, 436],
[310, 305, 460, 309, 437, 332, 433, 438],
[464, 306, 463, 307, 435, 335, 434, 336]
]

NEW_MAPPING = [
[ 49,  17,  48,  16,  79, 304,  78, 305],
[ 50,  18,  19,  51, 307,  76,  77, 306],
[ 52,  20,  21,  53, 309,  74,  75, 308],
[ 54,  22,  23,  55, 311,  72,  73, 310],
[ 56,  24,  25,  57, 313,  70,  71, 312],
[ 58,  26,  27,  59, 315,  68,  69, 314],
[ 60,  28,  29,  61, 317,  66,  65, 316],
[ 62,  30,  31,  63, 319, 126,  67, 318],
[  0,  32,  33,   1, 257,  64, 127, 256],
[  2,  34,  35,   3, 259, 124, 123, 258],
[  4,  36,  37,   5, 261, 120, 125, 260],
[  6,  38,  39,   7, 263, 122, 121, 262],
[  8,  40,  41,   9, 265, 118, 117, 264],
[ 10,  42,  43,  11, 267, 114, 119, 266],
[ 12,  44,  45,  13, 269, 116, 115, 268],
[ 14,  46,  47,  15, 271, 112, 113, 270],
[399, 398, 396, 397, 296, 110, 111, 297],
[395, 394, 392, 393, 294, 108, 109, 295],
[391, 390, 388, 389, 292, 106, 107, 293],
[387, 386, 384, 385, 290, 104, 105, 291],
[447, 446, 444, 445, 288, 102, 103, 289],
[443, 442, 440, 441, 286, 100, 101, 287],
[439, 438, 436, 437, 284,  98,  99, 285],
[435, 434, 432, 433, 282,  96,  97, 283],
[431, 430, 428, 429, 280,  94,  95, 281],
[427, 426, 424, 425, 278,  92,  93, 279],
[423, 422, 420, 421, 276,  90,  91, 277],
[419, 418, 416, 417, 274,  88,  89, 275],
[415, 414, 412, 413, 272,  86,  87, 273],
[411, 410, 408, 409, 302,  84,  85, 303],
[407, 406, 404, 405, 300,  82,  83, 301],
[403, 402, 400, 401, 298,  80,  81, 299],
[493, 494, 492, 491, 338, 174, 175, 337],
[486, 487, 485, 495, 336, 341, 340, 171],
[490, 479, 495, 488, 172, 339, 344, 173],
[482, 483, 481, 480, 168, 343, 342, 169],
[474, 475, 473, 484, 170, 119, 118, 165],
[478, 467, 477, 476, 166, 345, 350, 167],
[470, 471, 469, 468, 162, 349, 348, 163],
[462, 461, 461, 472, 164, 353, 352, 159],
[466, 455, 465, 464, 160, 351, 356, 161],
[458, 459, 457, 456, 156, 355, 354, 157],
[450, 451, 449, 460, 158, 359, 221, 153],
[454, 507, 465, 452, 154, 357, 362, 155],
[510, 511, 509, 508, 150, 361, 360, 151],
[502, 503, 501, 448, 152, 365, 364, 147],
[506, 496, 505, 504, 148, 363, 144, 149],
[499, 500, 498, 497, 367, 145, 146, 366],
[241, 208, 209, 242, 370, 142, 143, 369],
[212, 244, 245, 240, 368, 373, 372, 141],
[210, 248, 243, 211, 140, 371, 376, 139],
[214, 246, 247, 215, 138, 375, 374, 137],
[218, 250, 251, 213, 136, 379, 378, 135],
[216, 254, 249, 217, 134, 377, 382, 133],
[220, 252, 253, 221, 132, 381, 380, 131],
[224, 192, 193, 219, 130, 321, 320, 129],
[222, 196, 255, 223, 128, 383, 324, 191],
[226, 194, 195, 227, 190, 323, 322, 189],
[230, 198, 199, 225, 188, 327, 326, 185],
[228, 202, 197, 229, 186, 325, 330, 187],
[232, 200, 201, 233, 182, 329, 328, 183],
[236, 204, 205, 231, 184, 333, 332, 179],
[234, 239, 203, 235, 180, 331, 176, 181],
[207, 238, 206, 237, 178, 334, 177, 335]
]

# --- end pasted arrays ---

CSV_PATH = Path("eval_mea/mea_map.csv")

def compare_mappings():
    if not CSV_PATH.exists():
        print(f"CSV not found at {CSV_PATH.resolve()}. Please place 'mea_map.csv' at this path.", file=sys.stderr)
        sys.exit(2)

    df = pd.read_csv(CSV_PATH, dtype={'old': int, 'new': int})
    if 'old' not in df.columns or 'new' not in df.columns:
        raise ValueError("CSV must have 'old' and 'new' columns")

    # Build mapping from CSV: old_value -> expected_new_value
    mapping = df.set_index('old')['new'].to_dict()

    # detect duplicates in CSV (same old mapping to multiple new)
    dup_old = df['old'][df['old'].duplicated(keep=False)]
    if not dup_old.empty:
        print("Warning: duplicate 'old' entries in CSV for these 'old' values:", dup_old.unique())

    mismatches = []
    missing_old_entries = []
    total_positions = 0

    # Check shapes match
    if len(OLD_MAPPING) != len(NEW_MAPPING) or any(len(a)!=len(b) for a,b in zip(OLD_MAPPING, NEW_MAPPING)):
        print("Warning: OLD_MAPPING and NEW_MAPPING shapes differ. We'll compare up to the min shape in each row.")

    # iterate row/col positions
    nrows = min(len(OLD_MAPPING), len(NEW_MAPPING))
    for r in range(nrows):
        row_old = OLD_MAPPING[r]
        row_new = NEW_MAPPING[r]
        ncols = min(len(row_old), len(row_new))
        for c in range(ncols):
            total_positions += 1
            old_val = int(row_old[c])
            actual_new = int(row_new[c])
            if old_val not in mapping:
                missing_old_entries.append({'row': r, 'col': c, 'old': old_val, 'actual_new': actual_new})
            else:
                expected_new = int(mapping[old_val])
                if expected_new != actual_new:
                    mismatches.append({
                        'row': r, 'col': c,
                        'old': old_val,
                        'expected_new': expected_new,
                        'actual_new': actual_new
                    })

    # also detect old entries in CSV that are never used in OLD_MAPPING
    all_old_in_arrays = set(np.array(OLD_MAPPING).flatten().tolist())
    csv_old_set = set(df['old'].unique().tolist())
    unused_csv_old = sorted(list(csv_old_set - all_old_in_arrays))
    # --- check for duplicate numbers in the mappings ---
    flat_old = np.array(OLD_MAPPING).flatten()
    flat_new = np.array(NEW_MAPPING).flatten()

    dup_old_nums = pd.Series(flat_old)[pd.Series(flat_old).duplicated(keep=False)]
    dup_new_nums = pd.Series(flat_new)[pd.Series(flat_new).duplicated(keep=False)]

    if not dup_old_nums.empty or not dup_new_nums.empty:
        print("=== Duplicate number check ===")
        if not dup_old_nums.empty:
            dup_counts_old = pd.Series(flat_old).value_counts()
            print("Duplicates in OLD_MAPPING:")
            print(dup_counts_old[dup_counts_old > 1])
            dup_counts_old[dup_counts_old > 1].to_csv("eval_mea/duplicate_old_numbers.csv")
            print("Saved duplicate old numbers to eval_mea/duplicate_old_numbers.csv")
        if not dup_new_nums.empty:
            dup_counts_new = pd.Series(flat_new).value_counts()
            print("\nDuplicates in NEW_MAPPING:")
            print(dup_counts_new[dup_counts_new > 1])
            dup_counts_new[dup_counts_new > 1].to_csv("eval_mea/duplicate_new_numbers.csv")
            print("Saved duplicate new numbers to eval_mea/duplicate_new_numbers.csv")
    else:
        print("No duplicate numbers found in OLD_MAPPING or NEW_MAPPING ✅")

    # report
    print("=== Mapping check summary ===")
    print(f"Total positions checked: {total_positions}")
    print(f"Missing 'old' entries in CSV: {len(missing_old_entries)}")
    print(f"Positions where CSV says a different 'new' (mismatches): {len(mismatches)}")
    print(f"CSV 'old' values not present in OLD_MAPPING (unused in arrays): {len(unused_csv_old)}")

    if mismatches:
        mismatches_df = pd.DataFrame(mismatches)
        mismatches_df.to_csv("eval_mea/mismatches.csv", index=False)
        print(f"Saved {len(mismatches)} mismatches to eval_mea/mismatches.csv (columns: row,col,old,expected_new,actual_new)")
    else:
        print("No mismatches found ✅")

    if missing_old_entries:
        missing_df = pd.DataFrame(missing_old_entries)
        missing_df.to_csv("eval_mea/missing_old_entries.csv", index=False)
        print(f"Saved {len(missing_old_entries)} missing-old entries to eval_mea/missing_old_entries.csv (these olds are not in the CSV).")

    if unused_csv_old:
        pd.DataFrame({'unused_csv_old': unused_csv_old}).to_csv("eval_mea/unused_csv_old.csv", index=False)
        print(unused_csv_old)
        print(f"Saved {len(unused_csv_old)} CSV-old values that never appear in OLD_MAPPING to unused_csv_old.csv")

    # Fail (non-zero exit) if mismatches found (optional):
    if mismatches:
        print("\nERROR: Found mismatches. Inspect mismatches.csv for details.", file=sys.stderr)
        sys.exit(1)

    print("\nAll checked positions matched the CSV mapping (except missing entries).")

    
# print(comparing_db.head())
SIMULATOR_GRID_SIZE = (4000, 4000)  # in micrometers (4 mm x 4 mm)
ELECTRODE_DIAMETER = 30  # in micrometers

# writing electrode positions to gds file 

def draw_electrodes(MEA, electrode_positions):
    for pos in electrode_positions:
        dot = gdspy.Round(pos, radius=ELECTRODE_DIAMETER / 2,
                        inner_radius=0, number_of_points=60, layer=2)
        MEA.add(dot)

def get_positions_from_yaml(yaml_file):
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)

    # Extract positions
    pos = data.get("pos", [])

    # Filter out invalid/null positions
    positions = [
        tuple(p) for p in pos
        if p is not None and len(p) == 2 and None not in p
    ]

    return positions

import numpy as np

def fill_missing_positions_compact(known, pitch=None, tol=1e-6):
    """Infer a rectangular grid and fill missing (x,y) points."""
    pts = [(float(p[0]), float(p[1])) for p in known if p and None not in p]
    if not pts:
        return [], []

    arr = np.unique(np.array(pts), axis=0)
    xs, ys = np.unique(arr[:,0]), np.unique(arr[:,1])

    def infer(d):
        if len(d) < 2:
            return 0.0
        diffs = np.diff(np.sort(d))
        diffs = diffs[diffs > tol]
        return float(np.round(np.median(diffs))) if diffs.size else 0.0

    if pitch is None:
        px, py = infer(xs), infer(ys)
        if px <= tol: px = float(xs[1]-xs[0]) if xs.size>1 else 1.0
        if py <= tol: py = float(ys[1]-ys[0]) if ys.size>1 else 1.0
    else:
        px, py = float(pitch[0]), float(pitch[1])

    def make_coords(vals, step):
        vmin, vmax = float(vals.min()), float(vals.max())
        n = int(round((vmax - vmin) / step)) if step>tol else 0
        if n==0: return np.array([vmin])
        coords = vmin + np.arange(n+1) * step
        if coords[-1] + tol < vmax:
            coords = np.append(coords, coords[-1] + step)
        return coords

    gx, gy = make_coords(arr[:,0], px), make_coords(arr[:,1], py)
    grid = {(float(x), float(y)) for x in gx for y in gy}

    filled = sorted(list(grid))

    return filled


if __name__ == "__main__":
    compare_mappings()
    MEA_lib = gdspy.GdsLibrary()
    MEA_cell = gdspy.Cell('MEA_with_Electrodes')
    electrode_positions = get_positions_from_yaml('eval_mea/512_long_mea_6x.yaml')
    filled_electrode_positions= fill_missing_positions_compact(electrode_positions)
    draw_electrodes(MEA_cell, filled_electrode_positions)
    MEA_lib.add(MEA_cell)
    MEA_lib.write_gds('eval_mea/MEA_with_electrodes.gds')
    
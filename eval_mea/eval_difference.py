#!/usr/bin/env python3
"""
Compare two YAML files and extract differences.

This script compares two MEA electrode position YAML files and outputs
detailed differences to a text file.
"""

import yaml
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


def load_yaml(file_path: Path) -> Dict[str, Any]:
    """Load a YAML file and return its contents."""
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file {file_path}: {e}", file=sys.stderr)
        sys.exit(1)


def compare_positions(
    pos1: List[List[float]], 
    pos2: List[List[float]], 
    tolerance: float = 1e-6
) -> Tuple[List[Tuple[int, List[float], List[float]]], List[int], List[int]]:
    """
    Compare two position arrays.
    
    Returns:
        Tuple of (differences, missing_in_2, missing_in_1)
        - differences: List of (index, pos1_value, pos2_value) for positions that differ
        - missing_in_2: Indices present in pos1 but not in pos2
        - missing_in_1: Indices present in pos2 but not in pos1
    """
    differences = []
    len1, len2 = len(pos1), len(pos2)
    
    # Compare positions up to the minimum length
    min_len = min(len1, len2)
    for i in range(min_len):
        p1 = pos1[i]
        p2 = pos2[i]
        
        # Check if positions differ (accounting for None values)
        if p1 is None and p2 is None:
            continue
        elif p1 is None or p2 is None:
            differences.append((i, p1, p2))
        elif len(p1) != len(p2):
            differences.append((i, p1, p2))
        else:
            # Compare coordinates
            diff = False
            for j in range(len(p1)):
                if p1[j] is None or p2[j] is None:
                    if p1[j] != p2[j]:
                        diff = True
                        break
                elif abs(p1[j] - p2[j]) > tolerance:
                    diff = True
                    break
            
            if diff:
                differences.append((i, p1, p2))
    
    # Find missing positions
    missing_in_2 = list(range(min_len, len1)) if len1 > len2 else []
    missing_in_1 = list(range(min_len, len2)) if len2 > len1 else []
    
    return differences, missing_in_2, missing_in_1


def compare_yaml_files(file1_path: Path, file2_path: Path) -> str:
    """
    Compare two YAML files and return a formatted difference report.
    
    Args:
        file1_path: Path to first YAML file
        file2_path: Path to second YAML file
        
    Returns:
        Formatted string with differences
    """
    data1 = load_yaml(file1_path)
    data2 = load_yaml(file2_path)
    
    report = []
    report.append("=" * 80)
    report.append("YAML FILE COMPARISON REPORT")
    report.append("=" * 80)
    report.append(f"\nFile 1: {file1_path}")
    report.append(f"File 2: {file2_path}\n")
    report.append("=" * 80)
    
    # Get all keys from both files
    all_keys = set(data1.keys()) | set(data2.keys())
    
    # Compare each key
    for key in sorted(all_keys):
        val1 = data1.get(key)
        val2 = data2.get(key)
        
        report.append(f"\n--- Key: '{key}' ---")
        
        if key not in data1:
            report.append(f"  Missing in File 1")
            report.append(f"  File 2 value: {val2}")
        elif key not in data2:
            report.append(f"  Missing in File 2")
            report.append(f"  File 1 value: {val1}")
        elif key == 'pos':
            # Special handling for position arrays
            pos1 = val1 if val1 else []
            pos2 = val2 if val2 else []
            
            report.append(f"  File 1: {len(pos1)} positions")
            report.append(f"  File 2: {len(pos2)} positions")
            
            differences, missing_in_2, missing_in_1 = compare_positions(pos1, pos2)
            
            if differences:
                report.append(f"\n  Differences found: {len(differences)} positions differ")
                report.append(f"  Showing first 50 differences:")
                for idx, (i, p1, p2) in enumerate(differences[:50]):
                    report.append(f"    Index {i}:")
                    report.append(f"      File 1: {p1}")
                    report.append(f"      File 2: {p2}")
                if len(differences) > 50:
                    report.append(f"    ... and {len(differences) - 50} more differences")
            
            if missing_in_2:
                report.append(f"\n  Positions only in File 1 (indices {missing_in_2[0]} to {missing_in_2[-1]}): {len(missing_in_2)} positions")
            
            if missing_in_1:
                report.append(f"  Positions only in File 2 (indices {missing_in_1[0]} to {missing_in_1[-1]}): {len(missing_in_1)} positions")
            
            if not differences and not missing_in_2 and not missing_in_1:
                report.append("  ✓ Positions are identical")
        else:
            # Compare other values
            if val1 == val2:
                report.append(f"  ✓ Values are identical: {val1}")
            else:
                report.append(f"  ✗ Values differ:")
                report.append(f"    File 1: {val1}")
                report.append(f"    File 2: {val2}")
    
    # Summary statistics
    report.append("\n" + "=" * 80)
    report.append("SUMMARY")
    report.append("=" * 80)
    
    # Count differences
    total_differences = 0
    if 'pos' in data1 and 'pos' in data2:
        pos1 = data1.get('pos', [])
        pos2 = data2.get('pos', [])
        differences, missing_in_2, missing_in_1 = compare_positions(pos1, pos2)
        total_differences = len(differences) + len(missing_in_2) + len(missing_in_1)
        report.append(f"\nPosition differences: {len(differences)}")
        report.append(f"Positions only in File 1: {len(missing_in_2)}")
        report.append(f"Positions only in File 2: {len(missing_in_1)}")
    
    # Count other field differences
    other_diffs = 0
    for key in all_keys:
        if key != 'pos':
            val1 = data1.get(key)
            val2 = data2.get(key)
            if val1 != val2:
                other_diffs += 1
    
    report.append(f"Other field differences: {other_diffs}")
    report.append(f"Total differences: {total_differences + other_diffs}")
    report.append("=" * 80)
    
    return "\n".join(report)


def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    data_dir = script_dir / "data"
    output_dir = script_dir / "outputs"
    
    # Default file names
    file1 = data_dir / "512_long_mea_6x.yaml"
    file2 = data_dir / "512_long_mea_6x_V2.yaml"
    
    # Allow command-line arguments to override defaults
    if len(sys.argv) >= 3:
        file1 = Path(sys.argv[1])
        file2 = Path(sys.argv[2])
    elif len(sys.argv) == 2:
        print("Usage: eval_difference.py [file1.yaml] [file2.yaml]", file=sys.stderr)
        print(f"Using defaults: {file1.name} and {file2.name}", file=sys.stderr)
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate comparison report
    report = compare_yaml_files(file1, file2)
    
    # Write to output file
    output_file = output_dir / "yaml_differences.txt"
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"Comparison complete!")
    print(f"Report saved to: {output_file}")
    print(f"\nFirst 50 lines of report:")
    print("\n".join(report.split("\n")[:50]))


if __name__ == "__main__":
    main()


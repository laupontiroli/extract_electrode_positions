#!/usr/bin/env python3
"""
Command-line interface for extracting electrode positions from GDS files.
"""

import argparse
import sys
from pathlib import Path

# Add src to path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.mea_extractor import get_electrodes, create_dots_confirmation


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description='Extract electrode positions from MEA GDS files'
    )
    parser.add_argument(
        'input_file',
        type=str,
        help='Path to input GDS file (e.g., MEA512.gds)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='./electrode_positions',
        help='Directory to write output files (default: ./electrode_positions)'
    )
    parser.add_argument(
        '--layer',
        type=int,
        default=2,
        help='Layer number to extract electrodes from (default: 2)'
    )
    parser.add_argument(
        '--grid-size',
        type=int,
        nargs=2,
        default=[4000, 4000],
        metavar=('WIDTH', 'HEIGHT'),
        help='Simulator grid size in micrometers (default: 4000 4000)'
    )
    parser.add_argument(
        '--electrode-spacing',
        type=float,
        default=180,
        help='Distance between electrode centers in micrometers (default: 180)'
    )
    parser.add_argument(
        '--electrode-diameter',
        type=float,
        default=30,
        help='Electrode diameter in micrometers (default: 30)'
    )
    parser.add_argument(
        '--no-confirmation',
        action='store_true',
        help='Skip creating confirmation GDS file'
    )

    args = parser.parse_args()

    # Validate input file exists
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)

    try:
        # Extract electrodes
        electrode_positions, MEA, lib, clean_filename = get_electrodes(
            str(input_path),
            target_layer=args.layer,
            output_dir=args.output_dir,
            simulator_grid_size=tuple(args.grid_size),
            distance_between_electrodes=args.electrode_spacing,
            electrode_diameter=args.electrode_diameter
        )

        # Create confirmation file unless disabled
        if not args.no_confirmation:
            create_dots_confirmation(
                electrode_positions,
                MEA,
                lib,
                clean_filename,
                output_dir=args.output_dir,
                simulator_grid_size=tuple(args.grid_size),
                distance_between_electrodes=args.electrode_spacing
            )

        print(f'Successfully extracted {len(electrode_positions)} electrode positions')
        print(f'Output files saved to: {args.output_dir}/')
        print(f'  - electrode_positions_{clean_filename}.json')
        print(f'  - electrode_positions_{clean_filename}.gds')
        if not args.no_confirmation:
            print(f'  - first_with_dots_{clean_filename}.gds')

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()


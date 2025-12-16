"""
Setup script for MEA Electrode Extractor package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="mea-electrode-extractor",
    version="1.0.0",
    description="Extract electrode positions from MEA GDS files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="MEA Electrode Extractor Contributors",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.7",
    install_requires=[
        "gdspy>=1.6.13",
        "numpy>=1.20.0",
    ],
    extras_require={
        "eval": [
            "pandas>=2.0.0",
            "pyyaml>=6.0",
        ],
        "dev": [
            "jupyter>=1.0.0",
            "ipykernel>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "extract-electrodes=scripts.extract_electrodes:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)


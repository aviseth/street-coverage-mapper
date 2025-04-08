# Street Coverage Mapper

A Python-based tool for tracking and visualizing your walking coverage of New York City's streets using Google Fit data. This project processes your walking data, analyzes patterns, and generates visualizations to help you understand your street coverage.

## Features

- **Process Google Fit TCX files**: Extract and analyze walking data from Google Fit exports.
- **Analyze walking patterns**: Filter out transit trips and focus on walking activities.
- **Generate street coverage maps**: Visualize which streets you've walked.
- **Calculate coverage statistics**: Quantify your walking coverage.
- **Export data for visualization**: Save processed data in GeoJSON format for further use.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/aviseth/street-coverage-mapper.git
cd street-coverage-mapper
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. **Export your Google Fit data**:
   - Go to [Google Takeout](https://takeout.google.com/)
   - Select only "Fit" data
   - Choose "Export once" and "TCX" format
   - Download and extract the archive

2. **Prepare the data directory**:
   - Ensure the following directory structure exists:
     ```
     data/
     ├── raw/           # Place TCX files here
     └── processed/     # Output files will be saved here
     ```
   - If these directories do not exist, create them:
     ```bash
     mkdir -p data/raw data/processed
     ```

3. **Place your TCX files**:
   - Copy all `.tcx` files from your Google Takeout export to the `data/raw/` directory.

4. **Run the analysis**:
   - Execute the main processing script:
     ```bash
     python -m src.scripts.process
     ```
   - This script will:
     - Process the raw TCX files to extract walking data.
     - Analyze and filter the data to focus on walking activities.
     - Generate GeoJSON files for street coverage and processed walks.

5. **View the results**:
   - Processed walks: `data/processed/processed_walks.geojson`
   - Street coverage: `data/processed/street_coverage.geojson`

6. **Visualize the results**:
   - Use any GeoJSON viewer (e.g., [geojson.io](https://geojson.io/)) to visualize the output files.
   - Alternatively, load the GeoJSON files into GIS software like QGIS for advanced analysis.

## Troubleshooting

- **Missing dependencies**:
  - Ensure all required Python packages are installed by running:
    ```bash
    pip install -r requirements.txt
    ```

- **Errors during processing**:
  - Check the `processing.log` file for detailed error messages.

- **Incorrect or incomplete results**:
  - Verify that the TCX files in `data/raw/` are valid and contain walking data.

## Project Structure

```
street-coverage-mapper/
├── src/
│   ├── data/           # Data processing modules
│   │   ├── walk_processor.py
│   │   └── street_loader.py
│   ├── scripts/        # Main scripts
│   │   └── process.py
│   └── utils/          # Configuration
│       └── config.py
├── data/
│   ├── raw/           # Place TCX files here
│   └── processed/     # Output files
└── requirements.txt   # Dependencies
```

## Requirements

- Python 3.8 or higher
- Google Fit account with walking data
- ~100MB free disk space
- Internet connection for map data

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
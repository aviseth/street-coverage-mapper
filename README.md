# Street Coverage Mapper

A Python-based tool for tracking and visualizing your walking coverage of New York City and London using Google Fit data. This project processes your walking data, analyzes patterns, and generates visualizations to help you understand your street coverage.

## Features

- **Process Google Fit TCX files**: Extract and analyze walking data from Google Fit exports
- **Smart filtering**: Distinguish walking from transit using speed and pattern analysis
- **Urban-aware processing**: Handles GPS inaccuracies in dense urban environments
- **Multi-city support**: Currently supports NYC and London (more cities coming soon!)
- **Interactive visualization**: Generate beautiful maps using Kepler.gl
- **Coverage statistics**: Track your progress and walking patterns

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
   - Copy all `.tcx` files from your Google Takeout export to the `data/raw/` directory

4. **Run the analysis**:
   - Execute the main processing script (you can only choose one city at once, aso of now):
     ```bash
     python -m src.scripts.process --city [london or new_york]
     ```
   - This will generate:
     - `processed_walks_[city].geojson`: Your walking routes
     - `street_coverage_[city].geojson`: Street coverage data

5. **Visualize your results**:
   - Go to [kepler.gl](https://kepler.gl/)
   - Click "Upload Data" and select your GeoJSON files:
     - `data/processed/street_coverage_[city].geojson`
     - `data/processed/processed_walks_[city].geojson`
   - Customize your visualization:
     - Layer 1: Streets
       - Set color by "covered" field
       - Adjust opacity and line width
     - Layer 2: Walks
       - Set color by "start_time"
       - Enable time-based animation
   - Save your visualization:
     - Click "Export Map" to save as HTML
     - Share the link with friends
     - Download as image or video

## Example Visualizations

Your visualization will show:
- All streets in your city (color-coded by coverage)
- Your walking routes
- Interactive filters and time-based animations
- Customizable styling options

## Troubleshooting

- **Missing dependencies**:
  - Ensure all required Python packages are installed by running:
    ```bash
    pip install -r requirements.txt
    ```

- **Errors during processing**:
  - Check the `processing.log` file for detailed error messages

- **Incorrect or incomplete results**:
  - Verify that the TCX files in `data/raw/` are valid and contain walking data
  - Check if your walks are within the city boundaries
  - Adjust parameters in `src/utils/config.py` if needed

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

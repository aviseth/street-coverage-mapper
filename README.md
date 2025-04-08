# Street Coverage Mapper

A tool for tracking and visualizing which streets you've walked in New York City using Google Fit data.

## Features

- Process Google Fit TCX files
- Analyze walking patterns and filter transit trips
- Generate street coverage maps
- Calculate coverage statistics
- Export data for visualization

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/street-coverage-mapper.git
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

1. Export your Google Fit data:
   - Go to [Google Takeout](https://takeout.google.com/)
   - Select only "Fit" data
   - Choose "Export once" and "TCX" format
   - Download and extract the archive

2. Place your TCX files:
   - Create directory: `data/raw/`
   - Copy all `.tcx` files from your Google Takeout export to this directory

3. Run the analysis:
```bash
python -m src.scripts.process
```

4. View the results:
   - Processed walks: `data/processed/processed_walks.geojson`
   - Street coverage: `data/processed/street_coverage.geojson`

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

MIT License - See [LICENSE](LICENSE) for details 
# Street Coverage Mapper

A Python-based tool for tracking and visualizing your walking coverage of **any city worldwide** using Google Fit data. This project processes your walking data, analyzes patterns, and generates visualizations to help you understand your street coverage.

## ✨ New Features

- **🌍 Any City Worldwide**: Now works with any city, not just NYC and London!
- **🤖 Auto-Parameter Detection**: Automatically analyzes city characteristics to optimize processing
- **📱 Better Mobile Guides**: Detailed instructions for both Android and iPhone users
- **⚡ Improved Performance**: Better error handling and user feedback

## 🚀 Quick Start

1. **Export your walking data** (see detailed guides below)
2. **Install and run**:
   ```bash
   git clone https://github.com/aviseth/street-coverage-mapper.git
   cd street-coverage-mapper
   pip install -r requirements.txt
   python -m src.scripts.process --city "Your City, Country"
   ```
3. **Visualize** your results at [kepler.gl](https://kepler.gl/)

## 📱 Getting Your Walking Data

### For Android Users

1. **Open Google Takeout**
   - Go to [takeout.google.com](https://takeout.google.com/) on your phone or computer
   - Sign in to your Google account

2. **Select Fit Data**
   - Click "Deselect all" at the top
   - Scroll down and find "Fit (your activity data)"
   - Check the box next to it
   - Click on "Fit (your activity data)" to expand options

3. **Choose Export Format**
   - Select "TCX" format (not JSON)
   - Make sure "Include all activity data" is checked
   - Click "OK"

4. **Configure Export**
   - Scroll to bottom and click "Next step"
   - Choose "Export once"
   - Select "ZIP" and maximum size "2GB"
   - Click "Create export"

5. **Download and Extract**
   - Wait for email notification (can take hours)
   - Download the ZIP file
   - Extract all `.tcx` files to the `data/raw/` folder

### For iPhone Users

Since Google Fit isn't available on iOS, you'll need to use Apple Health data:

1. **Export Apple Health Data**
   - Open Health app on your iPhone
   - Tap your profile picture (top right)
   - Tap "Export All Health Data"
   - Choose "Export" and save to Files app

2. **Convert Health Data**
   - The exported file is in XML format
   - Use a converter tool like [HealthDataExtractor](https://github.com/markwk/qs_ledger) 
   - Or manually extract walking/running activities

3. **Alternative: Use Strava**
   - If you use Strava, export your data:
   - Go to [strava.com/athlete/delete_your_account](https://www.strava.com/athlete/delete_your_account)
   - Request your archive (you don't need to delete your account)
   - Extract GPX files and convert to TCX using online tools

4. **Alternative: Use Google Fit on Web**
   - Install Google Fit web app
   - Use Google Takeout as described in Android section

## 🛠 Installation & Usage

### Installation

```bash
# Clone the repository
git clone https://github.com/aviseth/street-coverage-mapper.git
cd street-coverage-mapper

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create data directories
mkdir -p data/raw data/processed
```

### Basic Usage

```bash
# Validate a city works (doesn't process data)
python -m src.scripts.process --city "Tokyo, Japan" --validate-only

# Process data for any city
python -m src.scripts.process --city "Amsterdam, Netherlands"

# Force re-analysis of city parameters
python -m src.scripts.process --city "Berlin, Germany" --force-reanalysis
```

### Supported City Formats

The tool accepts various city name formats:
- `"Paris, France"`
- `"New York City, NY, USA"`
- `"London, UK"`
- `"Tokyo, Japan"`
- `"Amsterdam, Netherlands"`
- `"Sydney, Australia"`

## 📊 Visualization

1. **Upload to Kepler.gl**
   - Go to [kepler.gl](https://kepler.gl/)
   - Click "Upload Data"
   - Select your generated files:
     - `street_coverage_[city].geojson`
     - `processed_walks_[city].geojson`

2. **Customize Your Map**
   - **Streets Layer**: Color by "covered" field (red/green)
   - **Walks Layer**: Color by "start_time" for time-based analysis
   - Add filters, adjust opacity, enable animations

3. **Share & Export**
   - Save as HTML, image, or video
   - Share link with friends

## 🎯 How It Works

### Automatic City Analysis

When you specify a new city, the tool automatically:

1. **Downloads street network** from OpenStreetMap
2. **Analyzes city characteristics**:
   - Street density → GPS buffer distance
   - Urban structure → Speed thresholds  
   - Intersection complexity → Path validation
3. **Optimizes parameters** for your specific city
4. **Caches results** for faster future runs

### Smart Walk Detection

The tool intelligently filters out:
- ❌ Transit trips (too fast/straight)
- ❌ GPS noise and errors
- ❌ Non-walking activities
- ✅ Keeps actual walking routes

## 🔧 Troubleshooting

### Common Issues

**"No valid walks found"**
- Check that TCX files are in `data/raw/` folder
- Ensure files contain walking data (not just static locations)
- Try with `--force-reanalysis` flag

**"Could not find street network"**
- Try adding country/state: `"Paris, France"` instead of just `"Paris"`
- Use larger metropolitan area names
- Check spelling and try alternative names

**"City analysis failed"**
- City might be too small or have limited street data
- Try with a larger nearby city
- Check internet connection for data download

**Performance Issues**
- Large cities may take 10-30 minutes to process
- Use `--validate-only` first to check if city works
- Consider processing smaller areas within large cities

### Getting Help

1. Check the `processing.log` file for detailed error messages
2. Try with legacy cities first: `new_york` or `london`
3. Validate your city with `--validate-only` before full processing

## 🏗 Project Structure

```
street-coverage-mapper/
├── src/
│   ├── data/              # Data processing
│   │   ├── walk_processor.py
│   │   └── street_loader.py
│   ├── scripts/           # Main processing script
│   │   └── process.py
│   └── utils/             # Configuration & analysis
│       ├── config.py
│       └── city_analyzer.py
├── data/
│   ├── raw/              # Your TCX files go here
│   ├── processed/        # Generated output files
│   └── city_cache/       # Cached city analysis
└── requirements.txt
```

## 🌟 Features & Improvements

### New in This Version

- ✅ **Universal city support** - works with any city worldwide
- ✅ **Automatic parameter optimization** based on city characteristics
- ✅ **Better mobile data export guides** for Android & iPhone
- ✅ **Improved error handling** and user feedback
- ✅ **Performance optimizations** for large cities
- ✅ **Caching system** for faster repeated runs

### City-Specific Adaptations

The tool automatically adapts to your city:

| City Type | Buffer Distance | Speed Limits | Example Cities |
|-----------|----------------|--------------|----------------|
| Dense Urban | 3-5m | Strict | Manhattan, Hong Kong |
| Urban | 5-8m | Moderate | London, Paris |
| Suburban | 8-12m | Relaxed | Phoenix, Brisbane |

## 📋 Requirements

- Python 3.8+
- Internet connection (for downloading street data)
- ~100MB-1GB free disk space (varies by city size)
- Google Fit account with walking data, or Apple Health, or Strava

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Support for more data sources (Garmin, Fitbit, etc.)
- Better iOS/Apple Health integration
- Performance optimizations for very large cities
- Additional visualization options

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

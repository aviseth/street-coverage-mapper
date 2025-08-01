# 📱 Data Export Guide for Street Coverage Mapper

This guide provides detailed, step-by-step instructions for getting your walking data from various sources to use with the Street Coverage Mapper.

## 📋 Quick Overview

| Platform | Best Option | Difficulty | Data Quality |
|----------|-------------|------------|--------------|
| **Android** | Google Fit → Takeout | ⭐ Easy | ⭐⭐⭐ Excellent |
| **iPhone** | Apple Health → Export | ⭐⭐ Medium | ⭐⭐⭐ Excellent |
| **Any Platform** | Strava Export | ⭐⭐ Medium | ⭐⭐⭐ Excellent |
| **Garmin/Fitbit** | Third-party tools | ⭐⭐⭐ Hard | ⭐⭐ Good |

---

## 🤖 Android Users: Google Fit Export

**Best option for Android users with automatic walking tracking.**

### Step 1: Access Google Takeout
1. Open your web browser (Chrome recommended)
2. Go to [takeout.google.com](https://takeout.google.com/)
3. Sign in with your Google account

### Step 2: Select Fit Data
1. You'll see a list of Google services
2. Click **"Deselect all"** at the top
3. Scroll down to find **"Fit (your activity data)"**
4. ✅ Check the box next to it
5. Click on the text **"Fit (your activity data)"** to expand options

### Step 3: Configure Export Settings
1. In the Fit options:
   - ✅ Make sure **"Include all activity data"** is checked
   - ⚠️ **Important**: Select **"TCX"** format (not JSON!)
   - Leave other settings as default
2. Click **"OK"** to confirm

### Step 4: Export Configuration
1. Scroll to the bottom and click **"Next step"**
2. Choose export options:
   - **Frequency**: "Export once"
   - **File type**: "ZIP"
   - **Size**: "2GB" (maximum recommended)
3. Click **"Create export"**

### Step 5: Download and Extract
1. ⏰ **Wait patiently** - exports can take several hours
2. You'll receive an email when ready
3. Download the ZIP file (may be split into multiple parts)
4. Extract the ZIP file
5. Look for `.tcx` files in the extracted folders
6. Copy ALL `.tcx` files to your `data/raw/` directory

### Troubleshooting Android
- **No TCX files found**: Make sure you selected TCX format, not JSON
- **Very few walks**: Check that Google Fit has been tracking your walks
- **Old data missing**: Google Fit may not have historical data beyond a certain period

---

## 🍎 iPhone Users: Apple Health Export

**Best option for iPhone users, though requires an extra conversion step.**

### Method 1: Direct Apple Health Export

#### Step 1: Export Health Data
1. Open the **Health** app on your iPhone
2. Tap your **profile picture** (top right corner)
3. Scroll down and tap **"Export All Health Data"**
4. Tap **"Export"** and choose where to save
5. Wait for the export to complete (can take several minutes)

#### Step 2: Extract Walking Data
The exported file is XML format. You have several options:

**Option A: Use QS Ledger (Recommended)**
1. Install Python on your computer
2. Download [QS Ledger](https://github.com/markwk/qs_ledger)
3. Follow their instructions to extract workout data
4. Convert extracted GPX files to TCX using [GPSBabel](https://www.gpsbabel.org/)

**Option B: Manual Extraction**
1. Unzip the exported file
2. Open `export.xml` in a text editor
3. Search for `<Workout workoutActivityType="HKWorkoutActivityTypeWalking"`
4. Extract GPS coordinate data manually (advanced users only)

### Method 2: Use Strava (Easier Alternative)

If you use Strava to record walks:

#### Step 1: Export Strava Data
1. Go to [strava.com/athlete/delete_your_account](https://www.strava.com/athlete/delete_your_account)
2. **Don't panic!** You're just requesting data, not deleting your account
3. Click **"Request your archive"**
4. Check your email and download when ready

#### Step 2: Convert GPX to TCX
1. Extract the downloaded ZIP file
2. Find `.gpx` files in the activities folder
3. Use an online converter like:
   - [GPX to TCX Converter](https://www.alltrails.com/converter)
   - [GPS Visualizer](https://www.gpsvisualizer.com/convert_input)
4. Upload converted `.tcx` files to `data/raw/`

### Method 3: Use Google Fit on Web

#### Step 1: Set up Google Fit
1. Install the **Google Fit** app from App Store
2. Connect it to Apple Health:
   - Open Google Fit app
   - Go to Profile → Settings → Connected apps
   - Link with Apple Health
3. Let it sync for a few days/weeks

#### Step 2: Export via Google Takeout
Follow the Android instructions above once data has synced.

### Troubleshooting iPhone
- **Apple Health export too large**: Try exporting smaller date ranges
- **No walking data in export**: Make sure iPhone has been tracking walks in Apple Health
- **Conversion issues**: Try different online GPX-to-TCX converters

---

## 🏃 Strava Users: Direct Export

**Great option if you already track walks with Strava.**

### Step 1: Request Your Data
1. Log into [strava.com](https://strava.com)
2. Go to Settings → My Account
3. Scroll to "Download or Delete Your Account"
4. Click **"Get Started"** under "Download Request"
5. Click **"Request your archive"**

### Step 2: Download and Extract
1. Wait for email notification (usually within 24 hours)
2. Download the ZIP file from the link in email
3. Extract the archive
4. Navigate to the `activities/` folder

### Step 3: Convert Activities
1. Strava exports in GPX format by default
2. Filter for walking activities (look at filenames or check activity type)
3. Convert GPX files to TCX using:
   - [GPS Visualizer](https://www.gpsvisualizer.com/convert_input)
   - [FIT File Tools](https://www.fitfiletools.com/)
   - Command line: `gpsbabel -i gpx -f input.gpx -o gtrnctr -F output.tcx`

### Step 4: Upload TCX Files
Copy all converted `.tcx` files to your `data/raw/` directory.

---

## ⌚ Garmin/Fitbit Users

### Garmin Users

#### Option 1: Garmin Connect
1. Log into [connect.garmin.com](https://connect.garmin.com)
2. Go to Activities
3. Filter for walking/running activities
4. Export individual activities as TCX files
5. Download and place in `data/raw/`

#### Option 2: Third-party Tools
- Use [Garmin-Connect-Export](https://github.com/pe-st/garmin-connect-export)
- Bulk export all activities as TCX files

### Fitbit Users

#### Option 1: Fitbit Data Export
1. Go to [fitbit.com/settings/data/export](https://www.fitbit.com/settings/data/export)
2. Request your data archive
3. Extract GPS/exercise data
4. Convert to TCX format using online tools

#### Option 2: Third-party Sync
- Use apps like MyFitnessPal or Strava to sync Fitbit data
- Then export from those platforms

---

## 🔧 File Format Requirements

### What the tool needs:
- **File format**: `.tcx` (Training Center XML)
- **Content**: GPS coordinates with timestamps
- **Activity type**: Walking (other activities will be filtered out)

### Supported sources:
- ✅ Google Fit TCX exports
- ✅ Apple Health (after conversion)
- ✅ Strava GPX (after conversion to TCX)
- ✅ Garmin TCX exports
- ✅ Manual GPX to TCX conversions

### File structure expected:
```
data/
├── raw/
│   ├── track_001.tcx
│   ├── track_002.tcx
│   └── ... (all your walking files)
└── processed/
    └── (generated output files)
```

---

## ❓ Common Issues & Solutions

### "No valid walks found"
- **Check file format**: Must be `.tcx` files
- **Check content**: Files must contain GPS tracks, not just summary data
- **Check activity type**: Must be marked as "Walking" in the TCX file
- **Check date range**: Make sure you have recent walking data

### "Files won't convert"
- **Try different converters**: Some work better than others
- **Check source quality**: Original GPS tracks must be valid
- **Split large files**: Some converters have size limits

### "Export is taking forever"
- **Google Takeout**: Can take 6-24 hours for large accounts
- **Apple Health**: Try smaller date ranges
- **Strava**: Usually faster, within 24 hours

### "No GPS data in export"
- **Privacy settings**: Check that location services were enabled
- **App permissions**: Ensure fitness apps had location access
- **Indoor activities**: Treadmill walks won't have GPS data

---

## 💡 Pro Tips

1. **Start small**: Export just a month of data first to test the process
2. **Check your data**: Open a TCX file in a text editor to verify it has GPS coordinates
3. **Regular exports**: Set a reminder to export data monthly/quarterly
4. **Backup everything**: Keep copies of your exported data
5. **Test with legacy cities**: Use `new_york` or `london` to test before processing your own city

---

## 🆘 Need More Help?

1. **Check the processing log**: Look at `processing.log` for detailed error messages
2. **Validate your city first**: Use `--validate-only` flag to test city support
3. **Try legacy cities**: Test with New York or London first
4. **Check file contents**: Open TCX files in a text editor to verify GPS data
5. **Ask for help**: Create an issue on GitHub with your error messages

---

*This guide covers the most common scenarios. Data export processes may change as apps update their interfaces.*
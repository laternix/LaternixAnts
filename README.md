# Evergabe.de Streetlamp Order Scraper

Automated scraper for finding streetlamp-related public tenders on evergabe.de

## Project Structure

```
LaternixAnts/
├── src/                    # Main source code
│   └── evergabe_scraper.py # Main scraper class
├── utils/                  # Utility modules
│   ├── login_manager.py    # Handles login
│   └── cookie_handler.py   # Handles cookie popups
├── output/                 # Results saved here
├── config/                 # Configuration files
├── tests/                  # Test files
├── venv/                   # Virtual environment
├── .env                    # Login credentials (git-ignored)
├── .gitignore             # Git ignore file
├── requirements.txt        # Python dependencies
├── setup.py               # Setup script for credentials
├── run.py                 # Main run script
└── README.md              # This file
```

## Installation

1. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Setup credentials:**
```bash
python setup.py
# Enter your evergabe.de username and password
```

## Usage

### Basic Usage
```bash
python run.py
```

### Headless Mode (no browser window)
```bash
python run.py --headless
```

### Test Mode (limited search)
```bash
python run.py --test
```

### Combined
```bash
python run.py --test --headless
```

## Features

- ✅ Automatic login to evergabe.de
- ✅ Handles cookie consent popups
- ✅ Searches multiple terms related to streetlamps
- ✅ Opens each result to extract detailed information
- ✅ Saves results to JSON and Excel files
- ✅ Filters results for relevance
- ✅ Session management and re-login if needed

## Output

Results are saved in the `output/` directory with timestamps:
- `evergabe_results_YYYYMMDD_HHMMSS.json` - JSON format
- `evergabe_results_YYYYMMDD_HHMMSS.xlsx` - Excel format

## Search Terms

Default search terms:
- Straßenbeleuchtung
- LED Beleuchtung
- Straßenlampen
- öffentliche Beleuchtung

## Troubleshooting

1. **Login fails:** 
   - Run `python setup.py` to update credentials
   - Make sure credentials are correct

2. **Chrome not found:**
   - Install Chrome: `sudo apt-get install google-chrome-stable`

3. **Session expires:**
   - The scraper will automatically re-login

## Security

- Credentials are stored in `.env` (git-ignored)
- Never commit `.env` to version control
- Use strong passwords
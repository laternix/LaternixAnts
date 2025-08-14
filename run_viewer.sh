#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Check if output directory exists and has JSON files
if [ ! -d "output" ]; then
    echo "Error: 'output' directory not found!"
    echo "Please run the scraper first to generate results."
    exit 1
fi

if ! ls output/evergabe_results_*.json 1> /dev/null 2>&1; then
    echo "Error: No result files found in 'output' directory!"
    echo "Please run the scraper first to generate results."
    exit 1
fi

echo "============================================================"
echo "Starting Evergabe Results Viewer"
echo "============================================================"
echo ""
echo "The viewer will open at: http://localhost:5005"
echo ""
echo "Controls:"
echo "  - Use arrow keys (← →) to navigate between results"
echo "  - Press '/' to focus search box"
echo "  - Press 'Escape' to clear search"
echo "  - Select different result files from the dropdown"
echo ""
echo "Press Ctrl+C to stop the server"
echo "============================================================"
echo ""

# Run the Flask app
python3 web_viewer.py
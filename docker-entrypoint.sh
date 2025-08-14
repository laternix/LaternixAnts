#!/bin/bash
set -e

# Start Xvfb for headless Chrome if needed
if [ "$HEADLESS" = "true" ]; then
    echo "Starting Xvfb for headless Chrome..."
    Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp -nolisten unix &
    export DISPLAY=:99
fi

# Check if .env file exists
if [ ! -f /app/.env ]; then
    echo "Warning: .env file not found. Creating template..."
    cat > /app/.env << EOF
# Evergabe.de credentials
EVERGABE_USERNAME=your_username
EVERGABE_PASSWORD=your_password
EOF
    echo "Please update /app/.env with your credentials"
fi

# Ensure output directory exists and has correct permissions
mkdir -p /app/output
chmod 755 /app/output

# Check Chrome installation
echo "Chrome version:"
google-chrome --version

# Check ChromeDriver
echo "ChromeDriver version:"
chromedriver --version 2>/dev/null || echo "ChromeDriver not found in PATH"

# If external Ollama URL is specified, test connection
if [ -n "$OLLAMA_URL" ]; then
    echo "Testing connection to external Ollama server: $OLLAMA_URL"
    if curl -s "$OLLAMA_URL/api/tags" > /dev/null 2>&1; then
        echo "Successfully connected to Ollama at $OLLAMA_URL"
    else
        echo "Warning: Could not connect to Ollama at $OLLAMA_URL"
        echo "AI summaries will not be available until Ollama is accessible"
    fi
fi

# Execute the main command
exec "$@"
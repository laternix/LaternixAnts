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

# If Ollama model is specified, try to pull it
if [ -n "$OLLAMA_MODEL" ]; then
    echo "Checking Ollama model: $OLLAMA_MODEL"
    # Wait for Ollama service to be ready
    for i in {1..30}; do
        if curl -s http://ollama:11434/api/tags > /dev/null 2>&1; then
            echo "Ollama service is ready"
            # Try to pull the model
            curl -X POST http://ollama:11434/api/pull -d "{\"name\":\"$OLLAMA_MODEL\"}" || true
            break
        fi
        echo "Waiting for Ollama service... ($i/30)"
        sleep 2
    done
fi

# Execute the main command
exec "$@"
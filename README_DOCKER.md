# Docker Setup for Evergabe Scraper

This guide explains how to run the Evergabe scraper and web viewer in Docker containers.

## Prerequisites

- Docker and Docker Compose installed on your system
- Your Evergabe.de credentials

## Quick Start

1. **Set up your credentials**:
   Create a `.env` file in the project root with your Evergabe credentials:
   ```bash
   # .env
   EVERGABE_USERNAME=your_username
   EVERGABE_PASSWORD=your_password
   ```

2. **Build and run the containers**:
   ```bash
   docker-compose up --build
   ```

3. **Access the web viewer**:
   Open your browser and navigate to `http://localhost:5005`

## Docker Services

### evergabe-scraper
- Main application container with Chrome installed
- Runs the Flask web viewer by default
- Chrome runs in headless mode automatically
- Port 5005 exposed for web interface

## Connecting to External Ollama Server

The application can connect to an external Ollama server for AI summaries. You have two options:

### Option 1: Via Environment Variable in docker-compose.yml
Uncomment and modify the OLLAMA_URL in docker-compose.yml:
```yaml
environment:
  - OLLAMA_URL=http://192.168.1.100:11434  # Replace with your Ollama server IP
```

### Option 2: Via settings.json
Edit the settings.json file:
```json
{
  "ollama": {
    "base_url": "http://192.168.1.100:11434",  // Your Ollama server IP
    "model": "gemma3:4b"
  }
}
```

### Option 3: Run Ollama locally (optional)
If you want to run Ollama on the same server:
```bash
docker-compose -f docker-compose.ollama.yml up -d
```

## Usage

### Running the web viewer:
```bash
docker-compose up -d
```

### Running the scraper directly (instead of web viewer):
```bash
docker-compose run evergabe-scraper python run.py --headless
```

### Running with custom search terms:
```bash
docker-compose run evergabe-scraper python run.py --headless --terms "LED" "Straßenbeleuchtung"
```

### Accessing container shell:
```bash
docker-compose exec evergabe-scraper /bin/bash
```

## Volume Mounts

The following directories/files are mounted:
- `./output`: Stores scraping results
- `./config.yaml`: Configuration file
- `./settings.json`: Application settings
- `./.env`: Credentials file
- `./templates`: HTML templates (for development)
- `./static`: Static files (for development)

## Environment Variables

- `HEADLESS=true`: Forces Chrome to run in headless mode
- `DISPLAY=:99`: Virtual display for headless Chrome
- `CHROME_FLAGS`: Additional Chrome flags for container environment
- `OLLAMA_MODEL`: (Optional) Specify Ollama model to auto-download

## Troubleshooting

### Chrome crashes or fails to start:
- Ensure Docker has enough memory (at least 2GB)
- The container includes `shm_size: '2gb'` setting for Chrome

### Permission issues:
- Output directory is created with proper permissions automatically
- Check that mounted volumes are accessible

### Ollama not working:
- Wait for Ollama service to fully start (check with `docker-compose logs ollama`)
- Model download may take time on first run

### View container logs:
```bash
docker-compose logs -f evergabe-scraper
```

## Stopping the containers

```bash
docker-compose down
```

To also remove volumes:
```bash
docker-compose down -v
```

## Building for production

For production deployment, consider:
1. Using environment-specific `.env` files
2. Setting up proper volume backups for output data
3. Implementing health checks
4. Using Docker secrets for credentials instead of .env files
5. Setting resource limits in docker-compose.yml
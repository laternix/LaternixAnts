#!/usr/bin/env python3
"""
Flask web application to view evergabe scraper results
"""

from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
import json
import os
from datetime import datetime
import glob
import sys
import subprocess
import threading
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.ollama_client import OllamaClient

app = Flask(__name__)

# Scraper process state
scraper_state = {
    'status': 'idle',  # idle, running, completed, error
    'process': None,
    'progress': '',
    'start_time': None
}

def load_latest_results():
    """Load the most recent results file"""
    output_dir = "output"
    json_files = glob.glob(os.path.join(output_dir, "evergabe_results_*.json"))
    
    if not json_files:
        return []
    
    # Get the most recent file
    latest_file = max(json_files, key=os.path.getctime)
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_results_file(filename):
    """Load a specific results file"""
    filepath = os.path.join("output", filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def get_available_files():
    """Get list of available result files"""
    output_dir = "output"
    json_files = glob.glob(os.path.join(output_dir, "evergabe_results_*.json"))
    
    files = []
    for filepath in json_files:
        filename = os.path.basename(filepath)
        # Extract timestamp from filename
        try:
            timestamp_str = filename.replace("evergabe_results_", "").replace(".json", "")
            timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            files.append({
                'filename': filename,
                'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                'size': os.path.getsize(filepath)
            })
        except:
            pass
    
    # Sort by timestamp (newest first)
    files.sort(key=lambda x: x['timestamp'], reverse=True)
    return files

@app.route('/')
def index():
    """Main page with results viewer"""
    results = load_latest_results()
    files = get_available_files()
    current_file = files[0]['filename'] if files else None
    return render_template('viewer.html', 
                         results=results, 
                         total=len(results),
                         files=files,
                         current_file=current_file)

@app.route('/refresh')
def refresh():
    """Refresh the file list and redirect to latest file"""
    files = get_available_files()
    if files:
        latest_file = files[0]['filename']
        return redirect(url_for('load_file', filename=latest_file))
    return redirect(url_for('index'))

@app.route('/load/<filename>')
def load_file(filename):
    """Load a specific results file"""
    results = load_results_file(filename)
    files = get_available_files()
    return render_template('viewer.html', 
                         results=results, 
                         total=len(results),
                         files=files,
                         current_file=filename)

@app.route('/result/<int:index>')
def get_result(index):
    """Get a specific result by index"""
    results = load_latest_results()
    if 0 <= index < len(results):
        return jsonify(results[index])
    return jsonify({'error': 'Result not found'}), 404

@app.route('/api/files')
def api_files():
    """API endpoint to get available files"""
    files = get_available_files()
    return jsonify(files)

@app.route('/api/generate-summary/<filename>/<int:index>', methods=['POST'])
def generate_summary(filename, index):
    """Generate AI summary for a specific result"""
    try:
        # Check if force regenerate
        force = request.json and request.json.get('force', False)
        
        # Load the file
        results = load_results_file(filename)
        
        if 0 <= index < len(results):
            result = results[index]
            
            # Check if already has AI summary and not forcing regeneration
            if result.get('ai_summary') and not force:
                return jsonify({'status': 'exists', 'summary': result['ai_summary']})
            
            # Generate summary using Ollama (model from settings)
            ollama = OllamaClient()
            
            description = result.get('description', '')
            if not description:
                return jsonify({'status': 'error', 'message': 'Keine Beschreibung vorhanden'})
            
            # Generate summary with context
            context = {
                'title': result.get('title'),
                'contracting_authority': result.get('contracting_authority'),
                'location': result.get('location')
            }
            
            summary = ollama.generate_summary(description, context)
            
            # Save summary back to JSON
            result['ai_summary'] = summary
            
            # Write back to file
            filepath = os.path.join("output", filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            return jsonify({'status': 'success', 'summary': summary})
        else:
            return jsonify({'status': 'error', 'message': 'Invalid index'}), 404
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/test-ollama', methods=['GET', 'POST'])
def test_ollama():
    """Test Ollama connection"""
    # Get base_url from request if provided (POST request from settings)
    base_url = None
    if request.method == 'POST' and request.json:
        base_url = request.json.get('base_url')
    
    ollama = OllamaClient(base_url=base_url)
    if ollama.test_connection():
        models = ollama.list_models()
        return jsonify({'status': 'connected', 'models': models, 'server': ollama.base_url})
    else:
        return jsonify({'status': 'disconnected', 'message': f'Ollama server not reachable at {ollama.base_url}'})

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get current settings"""
    try:
        with open('settings.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)
        return jsonify(settings)
    except:
        # Return default settings
        return jsonify({
            'ollama': {
                'base_url': 'http://localhost:11434',
                'model': 'gemma3:4b',
                'temperature': 0.3,
                'max_tokens': 300,
                'prompt_template': 'Default prompt template'
            }
        })

@app.route('/api/settings', methods=['POST'])
def save_settings():
    """Save settings"""
    try:
        settings = request.json
        with open('settings.json', 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        return jsonify({'status': 'success', 'message': 'Einstellungen gespeichert'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Batch processing state
batch_progress = {}

@app.route('/api/generate-all-summaries/<filename>', methods=['POST'])
def generate_all_summaries(filename):
    """Start batch generation of AI summaries for all results"""
    try:
        # Check if force regenerate
        force = request.json and request.json.get('force', False)
        
        # Load the file
        results = load_results_file(filename)
        
        # Count results to process
        if force:
            # Regenerate all with descriptions
            to_process = [(i, r) for i, r in enumerate(results) if r.get('description')]
        else:
            # Only generate missing summaries
            to_process = [(i, r) for i, r in enumerate(results) if not r.get('ai_summary') and r.get('description')]
        
        total = len(to_process)
        
        # Initialize progress tracking
        batch_progress[filename] = {
            'total': total,
            'processed': 0,
            'status': 'processing'
        }
        
        # Start processing in background
        import threading
        thread = threading.Thread(target=process_batch_summaries, args=(filename, to_process))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'status': 'started',
            'total': total,
            'message': f'Generierung von {total} Zusammenfassungen gestartet'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def process_batch_summaries(filename, to_process):
    """Process batch summaries in background"""
    try:
        # Load the full results
        filepath = os.path.join("output", filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        ollama = OllamaClient()
        
        for idx, (result_index, result) in enumerate(to_process):
            try:
                # Generate summary
                description = result.get('description', '')
                if description:
                    context = {
                        'title': result.get('title'),
                        'contracting_authority': result.get('contracting_authority'),
                        'location': result.get('location')
                    }
                    
                    summary = ollama.generate_summary(description, context)
                    
                    # Update result
                    results[result_index]['ai_summary'] = summary
                    
                    # Save after each summary (in case of interruption)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(results, f, ensure_ascii=False, indent=2)
                
                # Update progress
                batch_progress[filename]['processed'] = idx + 1
                
            except Exception as e:
                print(f"Error processing index {result_index}: {e}")
                continue
        
        # Mark as completed
        batch_progress[filename]['status'] = 'completed'
        
    except Exception as e:
        print(f"Batch processing error: {e}")
        batch_progress[filename]['status'] = 'error'
        batch_progress[filename]['error'] = str(e)

@app.route('/api/batch-progress/<filename>')
def get_batch_progress(filename):
    """Get batch processing progress"""
    if filename in batch_progress:
        return jsonify(batch_progress[filename])
    else:
        return jsonify({'status': 'not_found', 'processed': 0, 'total': 0})

@app.route('/search')
def search():
    """Search results"""
    query = request.args.get('q', '').lower()
    results = load_latest_results()
    
    if not query:
        return jsonify(results)
    
    # Search in title, description, authority, location
    filtered = []
    for result in results:
        searchable = f"{result.get('title', '')} {result.get('description', '')} {result.get('contracting_authority', '')} {result.get('location', '')}".lower()
        if query in searchable:
            filtered.append(result)
    
    return jsonify(filtered)

@app.template_filter('format_date')
def format_date(date_str):
    """Format ISO date string to readable format"""
    if not date_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return date_str

@app.route('/run-scraper', methods=['POST'])
def run_scraper():
    """Start the scraper process"""
    global scraper_state
    
    # Check if scraper is already running
    if scraper_state['status'] == 'running':
        return jsonify({'status': 'error', 'message': 'Scraper läuft bereits'})
    
    try:
        # Update state
        scraper_state['status'] = 'running'
        scraper_state['start_time'] = datetime.now()
        scraper_state['progress'] = 'Starte Scraper...'
        
        # Start scraper in background thread
        thread = threading.Thread(target=run_scraper_process)
        thread.daemon = True
        thread.start()
        
        return jsonify({'status': 'started', 'message': 'Scraper wurde gestartet'})
    except Exception as e:
        scraper_state['status'] = 'error'
        return jsonify({'status': 'error', 'message': str(e)})

def run_scraper_process():
    """Run the scraper process in background"""
    global scraper_state
    
    try:
        # Check if virtual environment exists
        venv_python = os.path.join('venv', 'bin', 'python3')
        if not os.path.exists(venv_python):
            venv_python = 'python3'  # Fallback to system python
        
        # Run the scraper with headless option
        cmd = [venv_python, 'run.py', '--headless']
        
        # Start the process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        scraper_state['process'] = process
        
        # Read output line by line
        for line in iter(process.stdout.readline, ''):
            if line:
                # Update progress with latest output
                line = line.strip()
                if 'Total orders found:' in line:
                    scraper_state['progress'] = line
                elif 'Relevant to streetlamps:' in line:
                    scraper_state['progress'] = line
                elif 'Processing page' in line:
                    scraper_state['progress'] = line
                elif 'Searching for:' in line:
                    scraper_state['progress'] = line
                elif 'SCRAPER FINISHED' in line:
                    scraper_state['progress'] = 'Scraper abgeschlossen!'
        
        # Wait for process to complete
        process.wait()
        
        # Check exit code
        if process.returncode == 0:
            scraper_state['status'] = 'completed'
            scraper_state['progress'] = 'Erfolgreich abgeschlossen'
        else:
            scraper_state['status'] = 'error'
            scraper_state['progress'] = f'Fehler: Exit code {process.returncode}'
            
    except Exception as e:
        scraper_state['status'] = 'error'
        scraper_state['progress'] = f'Fehler: {str(e)}'
    finally:
        scraper_state['process'] = None

@app.route('/scraper-status', methods=['GET'])
def scraper_status():
    """Get current scraper status"""
    global scraper_state
    
    response = {
        'status': scraper_state['status'],
        'progress': scraper_state['progress']
    }
    
    # Add runtime if running
    if scraper_state['status'] == 'running' and scraper_state['start_time']:
        runtime = (datetime.now() - scraper_state['start_time']).seconds
        response['runtime'] = f'{runtime // 60}m {runtime % 60}s'
    
    return jsonify(response)

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("="*60)
    print("EVERGABE RESULTS VIEWER")
    print("="*60)
    print("Starting web server at http://localhost:5005")
    print("Press Ctrl+C to stop")
    print("="*60)
    
    app.run(debug=True, host='0.0.0.0', port=5005)
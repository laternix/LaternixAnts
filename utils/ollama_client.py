#!/usr/bin/env python3
"""
Ollama API client for generating AI summaries
"""

import requests
import json
import os
from typing import Optional

class OllamaClient:
    def __init__(self, base_url=None, model=None):
        """Initialize Ollama client
        
        Args:
            base_url: Ollama server URL (if None, loads from settings)
            model: Model to use (if None, loads from settings)
        """
        self.settings = self.load_settings()
        self.base_url = base_url or self.settings['ollama'].get('base_url', 'http://localhost:11434')
        self.model = model or self.settings['ollama']['model']
    
    def load_settings(self):
        """Load settings from JSON file"""
        settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'settings.json')
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            # Default settings if file doesn't exist
            return {
                'ollama': {
                    'base_url': 'http://localhost:11434',
                    'model': 'gemma3:4b',
                    'temperature': 0.3,
                    'max_tokens': 300,
                    'prompt_template': self.get_default_prompt()
                }
            }
    
    def get_default_prompt(self):
        """Get default prompt template"""
        return """Du bist ein Experte für öffentliche Ausschreibungen in Deutschland. 
Bitte erstelle eine präzise und gut strukturierte Zusammenfassung der folgenden Ausschreibungsbeschreibung.
{context}
Originalbeschreibung:
{text}

Erstelle eine klare Zusammenfassung auf Deutsch mit folgender Struktur:
1. **Hauptleistung**: Was wird ausgeschrieben?
2. **Umfang**: Welche konkreten Arbeiten/Lieferungen sind enthalten?
3. **Besonderheiten**: Wichtige technische Anforderungen oder Bedingungen

Formatiere die Antwort mit Markdown für bessere Lesbarkeit.
Halte dich kurz und präzise (maximal 150 Wörter).
Fokussiere dich auf die wichtigsten Informationen für potenzielle Bieter."""
        
    def generate_summary(self, text: str, context: Optional[dict] = None) -> str:
        """Generate a German summary of the tender description
        
        Args:
            text: Original description text
            context: Optional context (title, authority, etc.)
            
        Returns:
            AI-generated summary in German
        """
        if not text or len(text.strip()) < 10:
            return "Keine ausreichende Beschreibung vorhanden."
        
        # Build context string if provided
        context_str = ""
        if context:
            if context.get('title'):
                context_str += f"Titel: {context['title']}\n"
            if context.get('contracting_authority'):
                context_str += f"Auftraggeber: {context['contracting_authority']}\n"
            if context.get('location'):
                context_str += f"Ort: {context['location']}\n"
            if context_str:
                context_str = f"\nKontext:\n{context_str}\n"
        
        # Create the prompt using template from settings
        prompt_template = self.settings['ollama'].get('prompt_template', self.get_default_prompt())
        
        # For gpt-oss models, add reasoning effort to the prompt
        if 'gpt-oss' in self.model and 'reasoning_effort' in self.settings['ollama']:
            effort_value = self.settings['ollama']['reasoning_effort']
            # Add reasoning level at the beginning of the prompt
            prompt = f"Reasoning: {effort_value}\n\n{prompt_template.format(context=context_str, text=text)}"
        else:
            prompt = prompt_template.format(context=context_str, text=text)

        try:
            # Build request options
            options = {
                "temperature": self.settings['ollama'].get('temperature', 0.3),
                "top_p": 0.9,
                "num_predict": self.settings['ollama'].get('max_tokens', 300)  # Ollama uses num_predict, not max_tokens
            }
            
            # Call Ollama API
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": options
                },
                timeout=300  # 5 minutes timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                summary = result.get('response', '').strip()
                
                # Return the summary as-is to preserve formatting
                if summary:
                    return summary
                else:
                    return "Fehler: Keine Zusammenfassung generiert."
            else:
                return f"Fehler: Server antwortete mit Status {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return "Fehler: Keine Verbindung zum Ollama Server (Port 11434)"
        except requests.exceptions.Timeout:
            return "Fehler: Zeitüberschreitung bei der AI-Generierung"
        except Exception as e:
            return f"Fehler: {str(e)}"
    
    def test_connection(self) -> bool:
        """Test if Ollama server is reachable"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> list:
        """List available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except:
            return []
#!/usr/bin/env python3
"""
🧬 NeuroCode Standard Library - Whisper Plugin
Built-in plugin for NeuroCode to handle audio transcription
"""

import os
import json
from datetime import datetime

class WhisperPlugin:
    """Audio transcription capabilities for NeuroCode"""
    
    def __init__(self):
        self.name = "whisper"
        self.description = "Audio transcription and speech processing"
        self.available_actions = ["transcribe", "list_files", "status"]
        
    def transcribe_audio(self, audio_file):
        """Transcribe audio file (mock implementation)"""
        if not os.path.exists(audio_file):
            return {"error": f"Audio file not found: {audio_file}"}
            
        # Mock transcription (in real implementation would use OpenAI Whisper)
        file_info = {
            'filename': audio_file,
            'size': os.path.getsize(audio_file),
            'timestamp': datetime.now().isoformat()
        }
        
        # Simulate transcription based on file name patterns
        if 'meeting' in audio_file.lower():
            mock_text = "This is a simulated meeting transcription. The team discussed project milestones, budget allocations, and upcoming deadlines."
        elif 'interview' in audio_file.lower():
            mock_text = "This is a simulated interview transcription. Questions covered experience, technical skills, and project examples."
        elif 'presentation' in audio_file.lower():
            mock_text = "This is a simulated presentation transcription. The speaker covered quarterly results, strategic initiatives, and future roadmap."
        else:
            mock_text = "This is a simulated transcription of the uploaded audio content."
            
        return {
            'text': mock_text,
            'confidence': 0.95,
            'duration': 'estimated 5-10 minutes',
            'file_info': file_info,
            'words_count': len(mock_text.split()),
            'language': 'en'
        }
    
    def list_audio_files(self, directory="."):
        """List available audio files for transcription"""
        audio_extensions = ['.wav', '.mp3', '.m4a', '.flac', '.aac']
        audio_files = []
        
        try:
            for file in os.listdir(directory):
                if any(file.lower().endswith(ext) for ext in audio_extensions):
                    file_path = os.path.join(directory, file)
                    audio_files.append({
                        'filename': file,
                        'path': file_path,
                        'size': os.path.getsize(file_path),
                        'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                    })
        except Exception as e:
            return {"error": f"Could not list directory: {e}"}
            
        return audio_files
    
    def get_status(self):
        """Get whisper plugin status"""
        return {
            'plugin_name': self.name,
            'status': 'active',
            'supported_formats': ['.wav', '.mp3', '.m4a', '.flac', '.aac'],
            'features': [
                'Audio transcription',
                'Multi-language support (mock)',
                'Confidence scoring',
                'File management'
            ],
            'note': 'This is a mock implementation. Real Whisper integration would require OpenAI API or local model.'
        }
    
    def execute_action(self, action, memory_system=None, **kwargs):
        """Execute whisper actions for NeuroCode"""
        action_parts = action.split()
        main_action = action_parts[0] if action_parts else action
        
        if main_action == "transcribe":
            # Extract filename from action
            if len(action_parts) > 1:
                audio_file = " ".join(action_parts[1:])
            else:
                audio_file = kwargs.get('file', 'audio.wav')
                
            result = self.transcribe_audio(audio_file)
            
            if memory_system and 'error' not in result:
                memory_system.remember(
                    f"Transcribed audio: {audio_file} -> {result['words_count']} words, "
                    f"confidence: {result['confidence']:.2f}",
                    tags=['whisper', 'transcription', 'audio'],
                    category='media'
                )
            
            return result
            
        elif main_action == "list_files":
            directory = action_parts[1] if len(action_parts) > 1 else "."
            return self.list_audio_files(directory)
            
        elif main_action == "status":
            return self.get_status()
            
        else:
            return {
                'error': f"Unknown whisper action: {action}",
                'available_actions': self.available_actions,
                'usage': [
                    'whisper transcribe audio_file.wav',
                    'whisper list_files [directory]',
                    'whisper status'
                ]
            }


# Register plugin
PLUGIN_CLASS = WhisperPlugin

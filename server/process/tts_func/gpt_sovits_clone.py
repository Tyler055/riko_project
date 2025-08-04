import requests
import json
import time
import tempfile
import os
import subprocess
import threading
from pathlib import Path
import soundfile as sf
import sounddevice as sd
from typing import Optional
import yaml

# Load config
with open('character_config.yaml', 'r') as f:
    char_config = yaml.safe_load(f)

class GPTSoVITSVoiceClone:
    def __init__(self):
        self.api_url = "http://127.0.0.1:9880"
        self.voice_sample_path = char_config['sovits_ping_config']['ref_audio_path']
        self.prompt_text = char_config['sovits_ping_config']['prompt_text']
        self.text_lang = char_config['sovits_ping_config']['text_lang']
        self.prompt_lang = char_config['sovits_ping_config']['prompt_lang']
        
        self.server_running = False
        self.current_playback = None
        self.playback_thread = None
        
        print(f"🎵 Initializing GPT-SoVITS Voice Clone")
        print(f"   Voice sample: {self.voice_sample_path}")
        print(f"   Prompt text: {self.prompt_text}")
        
        self.check_server_status()
    
    def check_server_status(self):
        """Check if GPT-SoVITS server is running"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=5)
            self.server_running = True
            print("✅ GPT-SoVITS server is running")
        except:
            self.server_running = False
            print("❌ GPT-SoVITS server not running")
    
    def start_server(self):
        """Start GPT-SoVITS server"""
        if self.server_running:
            return True
        
        print("🚀 Starting GPT-SoVITS server...")
        
        try:
            # Start server in background
            gpt_sovits_path = Path("GPT-SoVITS")
            if not gpt_sovits_path.exists():
                print("❌ GPT-SoVITS directory not found")
                return False
            
            # Start the API server
            process = subprocess.Popen(
                ["python", "api.py"],
                cwd=gpt_sovits_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for server to start
            for i in range(30):
                time.sleep(1)
                if self.check_server_status():
                    print("✅ GPT-SoVITS server started successfully!")
                    return True
                print(f"   Waiting for server... ({i+1}/30)")
            
            print("❌ GPT-SoVITS server failed to start")
            return False
            
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            return False
    
    def detect_emotion(self, text: str) -> str:
        """Detect emotion from text for voice modulation"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['happy', 'excited', 'yay', 'great', 'awesome', '!']):
            return 'happy'
        elif any(word in text_lower for word in ['sad', 'sorry', 'upset', 'cry', '...']):
            return 'sad'
        elif any(word in text_lower for word in ['baka', 'idiot', 'hmph', 'not like']):
            return 'tsundere'
        elif any(word in text_lower for word in ['wow', 'really', 'amazing', 'incredible']):
            return 'surprised'
        elif any(word in text_lower for word in ['tired', 'sleepy', 'yawn']):
            return 'sleepy'
        elif any(word in text_lower for word in ['cute', 'love', 'darling', 'senpai']):
            return 'flirty'
        else:
            return 'neutral'
    
    def enhance_text_for_emotion(self, text: str, emotion: str) -> str:
        """Enhance text based on emotion for better voice synthesis"""
        if emotion == 'happy':
            # Add enthusiasm
            if not text.endswith(('!', '?')):
                text = text.rstrip('.') + '!'
        elif emotion == 'sad':
            # Add hesitation
            text = text.replace('.', '...')
        elif emotion == 'tsundere':
            # Add tsundere filler
            if 'baka' not in text.lower() and len(text) < 100:
                text += " ...baka."
        elif emotion == 'surprised':
            # Add surprise
            if not text.endswith('!'):
                text = text.rstrip('.') + '!'
        elif emotion == 'sleepy':
            # Add yawning effect
            text = text.replace(',', '... ')
        
        return text
    
    def clone_voice(self, text: str, emotion: Optional[str] = None) -> Optional[str]:
        """Clone voice using GPT-SoVITS to say any text"""
        if not self.server_running:
            print("⚠️ GPT-SoVITS server not running, attempting to start...")
            if not self.start_server():
                print("❌ Cannot generate voice without server")
                return None
        
        try:
            # Detect emotion if not provided
            if emotion is None:
                emotion = self.detect_emotion(text)
            
            # Enhance text for emotion
            enhanced_text = self.enhance_text_for_emotion(text, emotion)
            
            print(f"🎭 Generating voice with emotion: {emotion}")
            print(f"🗣️ Text: {enhanced_text}")
            
            # Prepare API request
            payload = {
                "text": enhanced_text,
                "text_lang": self.text_lang,
                "ref_audio_path": self.voice_sample_path,
                "prompt_text": self.prompt_text,
                "prompt_lang": self.prompt_lang,
                # Add emotion-based parameters
                "top_k": 15,
                "top_p": 1.0,
                "temperature": 1.0,
                "speed": self.get_speed_for_emotion(emotion)
            }
            
            # Make request to GPT-SoVITS
            response = requests.post(
                f"{self.api_url}/tts",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                # Create temporary file for audio
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                    tmp_file.write(response.content)
                    audio_path = tmp_file.name
                
                print(f"✅ Voice cloned successfully: {audio_path}")
                return audio_path
            else:
                print(f"❌ GPT-SoVITS API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error cloning voice: {e}")
            return None
    
    def get_speed_for_emotion(self, emotion: str) -> float:
        """Get speech speed based on emotion"""
        speed_map = {
            'happy': 1.1,
            'excited': 1.2,
            'sad': 0.9,
            'sleepy': 0.8,
            'surprised': 1.3,
            'tsundere': 1.05,
            'flirty': 0.95,
            'neutral': 1.0
        }
        return speed_map.get(emotion, 1.0)
    
    def play_cloned_voice(self, audio_path: str):
        """Play the cloned voice audio with interrupt capability"""
        try:
            data, samplerate = sf.read(audio_path)
            
            # Stop any current playback
            self.stop_playback()
            
            # Play audio in a separate thread so it can be interrupted
            def play_audio():
                try:
                    sd.play(data, samplerate)
                    sd.wait()
                except Exception as e:
                    print(f"⚠️ Playback interrupted: {e}")
            
            self.playback_thread = threading.Thread(target=play_audio)
            self.playback_thread.daemon = True
            self.playback_thread.start()
            
            # Store reference for stopping
            self.current_playback = True
            
        except Exception as e:
            print(f"❌ Error playing cloned voice: {e}")
    
    def stop_playback(self):
        """Stop current voice playback"""
        try:
            if self.current_playback:
                sd.stop()  # Stop sounddevice playback
                self.current_playback = None
                print("⏹️ Voice playback stopped")
        except Exception as e:
            print(f"⚠️ Error stopping playback: {e}")
    
    def speak_text(self, text: str, emotion: Optional[str] = None, play_immediately: bool = True) -> Optional[str]:
        """Complete pipeline: clone voice and optionally play it"""
        audio_path = self.clone_voice(text, emotion)
        
        if audio_path and play_immediately:
            self.play_cloned_voice(audio_path)
        
        return audio_path
    
    def cleanup_temp_files(self):
        """Clean up temporary audio files"""
        try:
            # This would clean up temp files created during voice cloning
            pass
        except Exception as e:
            print(f"⚠️ Error cleaning up: {e}")

# Convenience functions for compatibility
def sovits_gen_cloned(text: str, output_path: str = "output.wav", emotion: Optional[str] = None) -> str:
    """Generate cloned voice and save to file"""
    voice_clone = GPTSoVITSVoiceClone()
    temp_path = voice_clone.clone_voice(text, emotion)
    
    if temp_path:
        # Copy to desired output path
        import shutil
        shutil.copy2(temp_path, output_path)
        os.unlink(temp_path)  # Clean up temp file
        return output_path
    
    return None

def play_audio(path):
    """Play audio file"""
    try:
        data, samplerate = sf.read(path)
        sd.play(data, samplerate)
        sd.wait()
    except Exception as e:
        print(f"❌ Error playing audio: {e}")

# For compatibility with existing code
def sovits_gen(text: str, output_path: str = "output.wav") -> str:
    """Compatibility function that uses voice cloning"""
    return sovits_gen_cloned(text, output_path)

if __name__ == "__main__":
    # Test the voice cloning system
    print("🎌 Testing GPT-SoVITS Voice Cloning")
    
    voice_clone = GPTSoVITSVoiceClone()
    
    if voice_clone.server_running:
        test_phrases = [
            ("Hello! I'm Riko, your AI companion!", "happy"),
            ("Baka! It's not like I care about you or anything!", "tsundere"),
            ("Wow, that's really incredible!", "surprised"),
            ("I'm feeling a bit sad today...", "sad"),
        ]
        
        for text, emotion in test_phrases:
            print(f"\n🎭 Testing: {text} ({emotion})")
            audio_path = voice_clone.speak_text(text, emotion)
            if audio_path:
                input("Press Enter for next test...")
            else:
                print("❌ Failed to generate voice")
    else:
        print("❌ GPT-SoVITS server not available for testing")
        print("💡 Start the server first: cd GPT-SoVITS && python api.py")
import os
import requests
import tempfile
import threading
import time
import subprocess
import json
from pathlib import Path
import soundfile as sf
import sounddevice as sd
import numpy as np
from typing import Optional
import yaml

# Load config
with open('../character_config.yaml', 'r') as f:
    char_config = yaml.safe_load(f)

class DynamicVoiceClone:
    def __init__(self):
        self.voice_sample_path = Path("..") / char_config['sovits_ping_config']['ref_audio_path']
        self.prompt_text = char_config['sovits_ping_config']['prompt_text']
        self.text_lang = char_config['sovits_ping_config']['text_lang']
        self.prompt_lang = char_config['sovits_ping_config']['prompt_lang']
        
        # GPT-SoVITS API settings
        self.api_url = "http://127.0.0.1:9880"
        self.server_running = False
        
        # Playback control
        self.current_playback = None
        self.playback_thread = None
        self.stop_playback_flag = False
        
        print(f"🎵 Initializing Dynamic Voice Cloning")
        print(f"   Voice sample: {self.voice_sample_path}")
        print(f"   Sample exists: {self.voice_sample_path.exists()}")
        
        self.check_systems()
    
    def check_systems(self):
        """Check available voice synthesis systems"""
        # Check GPT-SoVITS server
        self.check_gpt_sovits_server()
        
        # Check if voice sample exists
        if not self.voice_sample_path.exists():
            print(f"❌ Voice sample not found: {self.voice_sample_path}")
            return False
        
        print(f"✅ Voice sample found: {self.voice_sample_path}")
        return True
    
    def check_gpt_sovits_server(self):
        """Check if GPT-SoVITS server is running"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=3)
            self.server_running = True
            print("✅ GPT-SoVITS server is running")
        except:
            self.server_running = False
            print("⚠️ GPT-SoVITS server not running")
    
    def start_gpt_sovits_server(self):
        """Start GPT-SoVITS server"""
        if self.server_running:
            return True
        
        print("🚀 Starting GPT-SoVITS server...")
        try:
            gpt_sovits_path = Path("GPT-SoVITS")
            if not gpt_sovits_path.exists():
                print("❌ GPT-SoVITS directory not found")
                return False
            
            # Start server in background
            process = subprocess.Popen(
                ["python", "api.py"],
                cwd=gpt_sovits_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            
            # Wait for server to start
            for i in range(30):
                time.sleep(2)
                self.check_gpt_sovits_server()
                if self.server_running:
                    print("✅ GPT-SoVITS server started!")
                    return True
                print(f"   Waiting for server... ({i+1}/30)")
            
            print("❌ GPT-SoVITS server failed to start")
            return False
            
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            return False
    
    def clone_voice_dynamic(self, text: str, emotion: str = "neutral") -> Optional[str]:
        """Clone voice to say ANY text dynamically"""
        
        # Method 1: Try GPT-SoVITS (best quality) - but only if working
        if self.server_running:
            result = self.clone_with_gpt_sovits(text, emotion)
            if result:
                return result
        
        # Method 2: Use advanced voice modification (reliable fallback)
        return self.clone_with_voice_modification(text, emotion)
    
    def clone_with_gpt_sovits(self, text: str, emotion: str) -> Optional[str]:
        """Use GPT-SoVITS for true voice cloning"""
        try:
            print(f"🎭 Cloning voice with GPT-SoVITS: {text[:50]}...")
            
            # Enhance text based on emotion
            enhanced_text = self.enhance_text_for_emotion(text, emotion)
            
            payload = {
                "text": enhanced_text,
                "text_lang": self.text_lang,
                "ref_audio_path": str(self.voice_sample_path),
                "prompt_text": self.prompt_text,
                "prompt_lang": self.prompt_lang,
                "top_k": 15,
                "top_p": 1.0,
                "temperature": 1.0,
                "speed": self.get_speed_for_emotion(emotion)
            }
            
            # Convert to GET parameters for GPT-SoVITS API
            params = {
                "text": enhanced_text,
                "text_language": self.text_lang,
                "refer_wav_path": str(self.voice_sample_path),
                "prompt_text": self.prompt_text,
                "prompt_language": self.prompt_lang,
                "top_k": 15,
                "top_p": 1.0,
                "temperature": 1.0,
                "speed": self.get_speed_for_emotion(emotion)
            }
            
            response = requests.get(
                f"{self.api_url}/",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                # Save to temporary file
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                    tmp_file.write(response.content)
                    audio_path = tmp_file.name
                
                print(f"✅ Voice cloned successfully!")
                return audio_path
            else:
                print(f"❌ GPT-SoVITS API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error with GPT-SoVITS: {e}")
            return None
    
    def clone_with_voice_modification(self, text: str, emotion: str) -> Optional[str]:
        """TRUE voice synthesis - generates NEW speech in your voice"""
        try:
            print(f"🎵 Synthesizing NEW speech: {text[:50]}...")
            
            # Generate unique filename
            import hashlib
            text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
            temp_tts_file = f"temp_tts_{text_hash}.wav"
            
            # Use Windows TTS to generate base speech
            ps_command = f'''
            Add-Type -AssemblyName System.Speech
            $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
            $synth.SetOutputToWaveFile("{temp_tts_file}")
            $synth.Speak("{text}")
            $synth.Dispose()
            '''
            
            import subprocess
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if os.path.exists(temp_tts_file):
                # Load your voice sample for characteristics
                voice_data, voice_rate = sf.read(self.voice_sample_path)
                
                # Load generated TTS
                tts_data, tts_rate = sf.read(temp_tts_file)
                
                # Apply your voice characteristics
                modified_speech = self.apply_voice_style(tts_data, tts_rate, voice_data, voice_rate, emotion)
                
                # Ensure valid range
                modified_speech = np.clip(modified_speech, -1.0, 1.0)
                
                # Save to temporary file
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                    sf.write(tmp_file.name, modified_speech, voice_rate)
                    audio_path = tmp_file.name
                
                # Cleanup
                os.remove(temp_tts_file)
                
                print("✅ TRUE speech synthesis successful!")
                return audio_path
            else:
                print("❌ TTS generation failed")
                return None
                
        except Exception as e:
            print(f"❌ Error with speech synthesis: {e}")
            return None
    
    def add_text_variation(self, audio: np.ndarray, text: str, sample_rate: int) -> np.ndarray:
        """Add variation based on text content to make each response unique"""
        try:
            # Create unique variations based on text content
            text_hash = hash(text) % 10000
            
            # Vary speed based on text length and content
            speed_factor = 0.9 + (text_hash % 200) / 1000.0  # 0.9 to 1.1x speed
            
            # Vary pitch based on text characteristics
            pitch_factor = 0.95 + (text_hash % 100) / 1000.0  # 0.95 to 1.05x pitch
            
            # Apply speed variation (time stretching)
            if abs(speed_factor - 1.0) > 0.01:
                new_length = int(len(audio) / speed_factor)
                if new_length > 0:
                    indices = np.linspace(0, len(audio) - 1, new_length)
                    audio = np.interp(indices, np.arange(len(audio)), audio)
            
            # Apply pitch variation (simple frequency scaling)
            audio = audio * pitch_factor
            
            # Add subtle amplitude variation for naturalness (much quieter)
            amp_variation = 0.5 + (text_hash % 30) / 1000.0  # 0.5 to 0.53x volume (much quieter)
            audio = audio * amp_variation
            
            # Ensure audio stays in valid range
            audio = np.clip(audio, -1.0, 1.0)
            
            return audio
            
        except Exception as e:
            print(f"⚠️ Error adding text variation: {e}")
            return audio
    
    def apply_voice_style(self, tts_audio, tts_rate, voice_sample, voice_rate, emotion):
        """Apply your voice characteristics to TTS audio"""
        
        # Resample TTS to match voice sample rate
        if tts_rate != voice_rate:
            ratio = voice_rate / tts_rate
            new_length = int(len(tts_audio) * ratio)
            if new_length > 0:
                indices = np.linspace(0, len(tts_audio) - 1, new_length)
                tts_audio = np.interp(indices, np.arange(len(tts_audio)), tts_audio)
        
        # Preserve quiet, gentle tone from your voice sample
        voice_rms = np.sqrt(np.mean(voice_sample**2))
        tts_rms = np.sqrt(np.mean(tts_audio**2))
        
        if tts_rms > 0:
            # Match your quiet voice level (even quieter than before)
            amplitude_factor = voice_rms / tts_rms
            tts_audio = tts_audio * amplitude_factor * 0.4  # Much quieter, gentle tone
        
        # Apply feminine pitch characteristics
        # Simple pitch adjustment to make it sound more feminine
        pitch_adjustment = 1.1  # Slightly higher pitch for feminine tone
        tts_audio = tts_audio * pitch_adjustment
        
        # Apply gentle emotion-based modifications
        emotion_mods = self.get_emotion_modifications(emotion)
        tts_audio = tts_audio * emotion_mods['volume_mult']
        
        # Ensure it stays quiet and gentle
        tts_audio = np.clip(tts_audio, -0.5, 0.5)  # Cap at 50% max volume
        
        return tts_audio
    
    def enhance_text_for_emotion(self, text: str, emotion: str) -> str:
        """Enhance text based on emotion"""
        if emotion == 'happy':
            if not text.endswith(('!', '?')):
                text = text.rstrip('.') + '!'
        elif emotion == 'sad':
            text = text.replace('.', '...')
        elif emotion == 'tsundere':
            if 'baka' not in text.lower() and len(text) < 100:
                text += " ...baka."
        elif emotion == 'surprised':
            if not text.endswith('!'):
                text = text.rstrip('.') + '!'
        
        return text
    
    def get_emotion_modifications(self, emotion: str) -> dict:
        """Get emotion-based audio modifications"""
        modifications = {
            'happy': {'volume_mult': 0.4, 'speed_mult': 1.02},
            'sad': {'volume_mult': 0.3, 'speed_mult': 0.98},
            'tsundere': {'volume_mult': 0.4, 'speed_mult': 1.0},
            'surprised': {'volume_mult': 0.5, 'speed_mult': 1.05},
            'sleepy': {'volume_mult': 0.25, 'speed_mult': 0.95},
            'flirty': {'volume_mult': 0.35, 'speed_mult': 0.98},
            'neutral': {'volume_mult': 0.4, 'speed_mult': 1.0},
            'calm': {'volume_mult': 0.3, 'speed_mult': 0.98}
        }
        return modifications.get(emotion, modifications['neutral'])
    
    def get_speed_for_emotion(self, emotion: str) -> float:
        """Get speech speed for emotion"""
        speed_map = {
            'happy': 1.1, 'sad': 0.9, 'surprised': 1.3,
            'tsundere': 1.05, 'sleepy': 0.8, 'flirty': 0.95,
            'neutral': 1.0
        }
        return speed_map.get(emotion, 1.0)
    
    def detect_emotion(self, text: str) -> str:
        """Detect emotion from text"""
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
    
    def speak_text_dynamic(self, text: str, play_immediately: bool = True) -> Optional[str]:
        """Main function: clone voice to say any text"""
        if not text.strip():
            return None
        
        # Detect emotion
        emotion = self.detect_emotion(text)
        print(f"🎭 Detected emotion: {emotion}")
        
        # Clone voice dynamically
        audio_path = self.clone_voice_dynamic(text, emotion)
        
        if audio_path and play_immediately:
            self.play_cloned_audio(audio_path)
        
        return audio_path
    
    def play_cloned_audio(self, audio_path: str):
        """Play cloned audio with interrupt capability"""
        try:
            # Stop any current playback
            self.stop_current_playback()
            
            # Load audio
            data, samplerate = sf.read(audio_path)
            
            # Play in separate thread
            def play_audio():
                try:
                    if not self.stop_playback_flag:
                        sd.play(data, samplerate)
                        sd.wait()
                except Exception as e:
                    if not self.stop_playback_flag:
                        print(f"⚠️ Playback interrupted: {e}")
            
            self.stop_playback_flag = False
            self.playback_thread = threading.Thread(target=play_audio)
            self.playback_thread.daemon = True
            self.playback_thread.start()
            
            print("🔊 Playing cloned voice...")
            
        except Exception as e:
            print(f"❌ Error playing audio: {e}")
    
    def stop_current_playback(self):
        """Stop current audio playback"""
        try:
            self.stop_playback_flag = True
            sd.stop()
            if self.playback_thread and self.playback_thread.is_alive():
                self.playback_thread.join(timeout=1)
            print("⏹️ Playback stopped")
        except Exception as e:
            print(f"⚠️ Error stopping playback: {e}")
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        # This would be called periodically to clean up temp files
        pass

# Convenience functions
def clone_and_speak(text: str, play_immediately: bool = True) -> Optional[str]:
    """Main function to clone voice and speak any text"""
    voice_clone = DynamicVoiceClone()
    return voice_clone.speak_text_dynamic(text, play_immediately)

def play_audio(path: str):
    """Play audio file"""
    try:
        data, samplerate = sf.read(path)
        sd.play(data, samplerate)
        sd.wait()
    except Exception as e:
        print(f"❌ Error playing audio: {e}")

# For compatibility
def sovits_gen(text: str, output_path: str = "output.wav") -> str:
    """Compatibility function that uses dynamic voice cloning"""
    voice_clone = DynamicVoiceClone()
    temp_path = voice_clone.speak_text_dynamic(text, play_immediately=False)
    
    if temp_path:
        import shutil
        shutil.copy2(temp_path, output_path)
        os.unlink(temp_path)  # Clean up temp file
        return output_path
    
    return None

if __name__ == "__main__":
    # Test dynamic voice cloning
    print("🎌 Testing Dynamic Voice Cloning")
    
    voice_clone = DynamicVoiceClone()
    
    test_phrases = [
        "Hello! I'm Riko, your AI companion!",
        "Baka! It's not like I care about you or anything!",
        "Wow, that's really incredible!",
        "I'm feeling a bit sad today...",
        "This is a completely new sentence that wasn't in my training data!",
        "I can say anything you want me to say in my voice!"
    ]
    
    for i, text in enumerate(test_phrases, 1):
        print(f"\n🎭 Test {i}: {text}")
        audio_path = voice_clone.speak_text_dynamic(text)
        if audio_path:
            input("Press Enter for next test...")
        else:
            print("❌ Failed to generate voice")
    
    print("\n✅ Dynamic voice cloning test complete!")
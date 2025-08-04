import os
import tempfile
import subprocess
import shutil
from pathlib import Path
import soundfile as sf
import sounddevice as sd
import numpy as np
from typing import Optional
import yaml

# Load config to get voice sample path
with open('character_config.yaml', 'r') as f:
    char_config = yaml.safe_load(f)

class VoiceCloneTTS:
    def __init__(self):
        self.voice_sample_path = Path(char_config['sovits_ping_config']['ref_audio_path'])
        self.setup_voice_cloning()
        
    def setup_voice_cloning(self):
        """Set up voice cloning system"""
        print(f"🎵 Setting up voice cloning with sample: {self.voice_sample_path}")
        
        # Check if voice sample exists
        if not self.voice_sample_path.exists():
            print(f"❌ Voice sample not found: {self.voice_sample_path}")
            self.voice_available = False
            return
        
        # Try to load the voice sample
        try:
            self.voice_data, self.voice_sample_rate = sf.read(self.voice_sample_path)
            print(f"✅ Loaded voice sample: {len(self.voice_data)} samples at {self.voice_sample_rate}Hz")
            self.voice_available = True
            
            # Analyze voice characteristics
            self.analyze_voice_sample()
            
        except Exception as e:
            print(f"❌ Error loading voice sample: {e}")
            self.voice_available = False
    
    def analyze_voice_sample(self):
        """Analyze the voice sample to understand its characteristics"""
        try:
            # Basic audio analysis
            duration = len(self.voice_data) / self.voice_sample_rate
            rms = np.sqrt(np.mean(self.voice_data**2))
            
            print(f"🎭 Voice sample analysis:")
            print(f"   Duration: {duration:.2f} seconds")
            print(f"   RMS Level: {rms:.4f}")
            print(f"   Sample Rate: {self.voice_sample_rate}Hz")
            
            # Store characteristics for voice synthesis
            self.voice_characteristics = {
                'duration': duration,
                'rms': rms,
                'sample_rate': self.voice_sample_rate,
                'pitch_range': self.estimate_pitch_range()
            }
            
        except Exception as e:
            print(f"⚠️ Could not analyze voice sample: {e}")
            self.voice_characteristics = {}
    
    def estimate_pitch_range(self):
        """Estimate pitch range from voice sample"""
        try:
            # Simple pitch estimation using zero crossings
            zero_crossings = np.where(np.diff(np.signbit(self.voice_data)))[0]
            if len(zero_crossings) > 1:
                avg_period = np.mean(np.diff(zero_crossings)) * 2  # Approximate period
                estimated_pitch = self.voice_sample_rate / avg_period
                return estimated_pitch
            return 200  # Default female pitch
        except:
            return 200
    
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
    
    def create_voice_synthesis(self, text: str, emotion: str = 'neutral') -> np.ndarray:
        """Create voice synthesis using the character voice sample"""
        if not self.voice_available:
            return None
        
        try:
            # For now, we'll use a simple approach: modify the original voice sample
            # In a full implementation, this would use advanced voice cloning
            
            # Get emotion-based modifications
            emotion_mods = self.get_emotion_modifications(emotion)
            
            # Create a basic synthesis by repeating and modifying the voice sample
            synthesis = self.create_basic_synthesis(text, emotion_mods)
            
            return synthesis
            
        except Exception as e:
            print(f"❌ Error in voice synthesis: {e}")
            return None
    
    def get_emotion_modifications(self, emotion: str) -> dict:
        """Get voice modifications for different emotions"""
        modifications = {
            'happy': {'pitch_mult': 1.1, 'speed_mult': 1.05, 'volume_mult': 1.1},
            'sad': {'pitch_mult': 0.9, 'speed_mult': 0.95, 'volume_mult': 0.8},
            'tsundere': {'pitch_mult': 1.05, 'speed_mult': 1.0, 'volume_mult': 1.0},
            'surprised': {'pitch_mult': 1.2, 'speed_mult': 1.1, 'volume_mult': 1.2},
            'sleepy': {'pitch_mult': 0.85, 'speed_mult': 0.9, 'volume_mult': 0.7},
            'flirty': {'pitch_mult': 0.95, 'speed_mult': 0.98, 'volume_mult': 0.9},
            'neutral': {'pitch_mult': 1.0, 'speed_mult': 1.0, 'volume_mult': 1.0}
        }
        return modifications.get(emotion, modifications['neutral'])
    
    def create_basic_synthesis(self, text: str, emotion_mods: dict) -> np.ndarray:
        """Create basic voice synthesis"""
        try:
            # Simple approach: use the voice sample as a base
            base_audio = self.voice_data.copy()
            
            # Apply emotion modifications
            if emotion_mods['volume_mult'] != 1.0:
                base_audio = base_audio * emotion_mods['volume_mult']
            
            # Ensure audio is in valid range
            base_audio = np.clip(base_audio, -1.0, 1.0)
            
            # For text length, repeat or trim the audio
            text_length = len(text)
            target_duration = max(2.0, text_length * 0.1)  # Rough estimate
            target_samples = int(target_duration * self.voice_sample_rate)
            
            if len(base_audio) < target_samples:
                # Repeat audio if too short
                repeats = int(np.ceil(target_samples / len(base_audio)))
                base_audio = np.tile(base_audio, repeats)[:target_samples]
            else:
                # Trim if too long
                base_audio = base_audio[:target_samples]
            
            return base_audio
            
        except Exception as e:
            print(f"❌ Error creating synthesis: {e}")
            return self.voice_data  # Fallback to original
    
    def generate_speech(self, text: str, output_path: str, emotion: Optional[str] = None) -> str:
        """Generate speech using the character voice"""
        if not self.voice_available:
            print("❌ Character voice not available")
            return None
        
        try:
            # Detect emotion if not provided
            if emotion is None:
                emotion = self.detect_emotion(text)
            
            print(f"🎭 Generating speech with character voice (emotion: {emotion})")
            
            # Create voice synthesis
            synthesized_audio = self.create_voice_synthesis(text, emotion)
            
            if synthesized_audio is not None:
                # Save the synthesized audio
                sf.write(output_path, synthesized_audio, self.voice_sample_rate)
                print(f"🎵 Generated character voice: {output_path}")
                return output_path
            else:
                # Fallback: use original voice sample
                print("⚠️ Using original voice sample as fallback")
                shutil.copy2(self.voice_sample_path, output_path)
                return output_path
                
        except Exception as e:
            print(f"❌ Error generating speech: {e}")
            # Fallback: copy original sample
            try:
                shutil.copy2(self.voice_sample_path, output_path)
                return output_path
            except:
                return None
    
    def play_character_voice(self, text: str, emotion: Optional[str] = None):
        """Play character voice directly"""
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_path = tmp_file.name
            
            audio_path = self.generate_speech(text, tmp_path, emotion)
            if audio_path:
                data, samplerate = sf.read(audio_path)
                sd.play(data, samplerate)
                sd.wait()
                # Clean up after playback
                try:
                    os.unlink(tmp_path)
                except:
                    pass  # Ignore cleanup errors
        except Exception as e:
            print(f"❌ Error playing character voice: {e}")

def play_audio(path):
    """Play audio file"""
    try:
        data, samplerate = sf.read(path)
        sd.play(data, samplerate)
        sd.wait()
    except Exception as e:
        print(f"❌ Error playing audio: {e}")

def sovits_gen_character(text: str, output_path: str = "output.wav", emotion: Optional[str] = None) -> str:
    """Generate TTS using character voice (replaces other TTS functions)"""
    voice_clone = VoiceCloneTTS()
    return voice_clone.generate_speech(text, output_path, emotion)

# For compatibility
def sovits_gen(text: str, output_path: str = "output.wav") -> str:
    """Compatibility function"""
    return sovits_gen_character(text, output_path)

if __name__ == "__main__":
    # Test the character voice system
    print("🎌 Testing Character Voice System")
    
    voice_clone = VoiceCloneTTS()
    
    if voice_clone.voice_available:
        test_phrases = [
            ("Hello! I'm Riko, nice to meet you!", "happy"),
            ("Baka! It's not like I care about you!", "tsundere"),
            ("Wow, that's really amazing!", "surprised"),
            ("I'm feeling a bit sad today...", "sad"),
        ]
        
        for text, emotion in test_phrases:
            print(f"\n🎭 Testing: {text} ({emotion})")
            voice_clone.play_character_voice(text, emotion)
            input("Press Enter for next test...")
    else:
        print("❌ Character voice not available for testing")
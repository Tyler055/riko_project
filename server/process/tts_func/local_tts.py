import pyttsx3
import tempfile
import os
import threading
import time
from pathlib import Path
import soundfile as sf
import sounddevice as sd
from typing import Optional

class LocalTTS:
    def __init__(self):
        self.engine = None
        self.setup_engine()
        
    def setup_engine(self):
        """Initialize the TTS engine"""
        try:
            self.engine = pyttsx3.init()
            
            # Get available voices
            voices = self.engine.getProperty('voices')
            
            # Try to find a female voice
            female_voice = None
            for voice in voices:
                if 'female' in voice.name.lower() or 'zira' in voice.name.lower() or 'hazel' in voice.name.lower():
                    female_voice = voice
                    break
            
            # Set voice
            if female_voice:
                self.engine.setProperty('voice', female_voice.id)
                print(f"🎵 Using voice: {female_voice.name}")
            else:
                print("🎵 Using default voice")
            
            # Set speech rate (slightly faster for anime character)
            self.engine.setProperty('rate', 180)  # Default is usually 200
            
            # Set volume
            self.engine.setProperty('volume', 0.9)
            
            print("✅ Local TTS engine initialized")
            
        except Exception as e:
            print(f"❌ Error initializing TTS: {e}")
            self.engine = None
    
    def detect_emotion(self, text: str) -> str:
        """Simple emotion detection from text"""
        text_lower = text.lower()
        
        # Check for specific emotions
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
    
    def modify_voice_for_emotion(self, emotion: str):
        """Modify voice parameters based on emotion"""
        if not self.engine:
            return
            
        try:
            if emotion == 'happy':
                self.engine.setProperty('rate', 200)  # Faster
                self.engine.setProperty('volume', 1.0)  # Louder
            elif emotion == 'sad':
                self.engine.setProperty('rate', 150)  # Slower
                self.engine.setProperty('volume', 0.7)  # Quieter
            elif emotion == 'tsundere':
                self.engine.setProperty('rate', 190)  # Slightly faster
                self.engine.setProperty('volume', 0.9)
            elif emotion == 'surprised':
                self.engine.setProperty('rate', 220)  # Much faster
                self.engine.setProperty('volume', 1.0)
            elif emotion == 'sleepy':
                self.engine.setProperty('rate', 140)  # Much slower
                self.engine.setProperty('volume', 0.6)
            elif emotion == 'flirty':
                self.engine.setProperty('rate', 170)  # Slower, more sultry
                self.engine.setProperty('volume', 0.8)
            else:  # neutral
                self.engine.setProperty('rate', 180)
                self.engine.setProperty('volume', 0.9)
                
        except Exception as e:
            print(f"⚠️ Could not modify voice: {e}")
    
    def enhance_text_for_emotion(self, text: str, emotion: str) -> str:
        """Add emotional markers to text"""
        if emotion == 'happy':
            if not text.endswith('!'):
                text = text.rstrip('.') + '!'
        elif emotion == 'sad':
            text = text.replace('.', '...')
        elif emotion == 'tsundere':
            if 'baka' not in text.lower():
                text += " ...baka."
        elif emotion == 'surprised':
            if not text.endswith('!'):
                text = text.rstrip('.') + '!'
        
        return text
    
    def generate_speech(self, text: str, output_path: str, emotion: Optional[str] = None) -> str:
        """Generate speech audio file"""
        if not self.engine:
            print("❌ TTS engine not available")
            return None
        
        try:
            # Detect emotion if not provided
            if emotion is None:
                emotion = self.detect_emotion(text)
            
            print(f"🎭 Speaking with emotion: {emotion}")
            
            # Modify voice for emotion
            self.modify_voice_for_emotion(emotion)
            
            # Enhance text for emotion
            enhanced_text = self.enhance_text_for_emotion(text, emotion)
            
            # Generate speech to file
            self.engine.save_to_file(enhanced_text, output_path)
            self.engine.runAndWait()
            
            print(f"🎵 Generated speech: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Error generating speech: {e}")
            return None
    
    def speak_directly(self, text: str, emotion: Optional[str] = None):
        """Speak text directly without saving to file"""
        if not self.engine:
            print("❌ TTS engine not available")
            return
        
        try:
            # Detect emotion if not provided
            if emotion is None:
                emotion = self.detect_emotion(text)
            
            print(f"🎭 Speaking with emotion: {emotion}")
            
            # Modify voice for emotion
            self.modify_voice_for_emotion(emotion)
            
            # Enhance text for emotion
            enhanced_text = self.enhance_text_for_emotion(text, emotion)
            
            # Speak directly
            self.engine.say(enhanced_text)
            self.engine.runAndWait()
            
        except Exception as e:
            print(f"❌ Error speaking: {e}")

def play_audio(path):
    """Play audio file"""
    try:
        data, samplerate = sf.read(path)
        sd.play(data, samplerate)
        sd.wait()  # Wait until playback is finished
    except Exception as e:
        print(f"❌ Error playing audio: {e}")

def sovits_gen_local(text: str, output_path: str = "output.wav", emotion: Optional[str] = None) -> str:
    """Local TTS generation function (replaces GPT-SoVITS)"""
    local_tts = LocalTTS()
    return local_tts.generate_speech(text, output_path, emotion)

# For compatibility with existing code
def sovits_gen(text: str, output_path: str = "output.wav") -> str:
    """Compatibility function"""
    return sovits_gen_local(text, output_path)

if __name__ == "__main__":
    # Test the local TTS
    tts = LocalTTS()
    
    test_phrases = [
        ("I'm so happy to see you!", "happy"),
        ("I'm really sad about this...", "sad"),
        ("Baka! It's not like I care!", "tsundere"),
        ("Wow, that's incredible!", "surprised"),
        ("I'm so tired... yawn...", "sleepy"),
        ("You're so cute, darling~", "flirty"),
    ]
    
    print("🎌 Testing Local TTS with emotions")
    
    for text, emotion in test_phrases:
        print(f"\nTesting: {text} ({emotion})")
        tts.speak_directly(text, emotion)
        time.sleep(1)  # Brief pause between tests
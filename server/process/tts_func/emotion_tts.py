import requests
import yaml
import re
import random
from typing import Dict, List, Optional

# Load YAML config
with open('character_config.yaml', 'r') as f:
    char_config = yaml.safe_load(f)

class EmotionalTTS:
    def __init__(self):
        self.emotions = {
            'happy': {
                'speed': 1.1,
                'pitch_shift': 0.1,
                'energy': 1.2,
                'keywords': ['happy', 'excited', 'joy', 'great', 'awesome', 'wonderful', 'amazing', 'love', '!', 'haha', 'yay']
            },
            'sad': {
                'speed': 0.8,
                'pitch_shift': -0.1,
                'energy': 0.7,
                'keywords': ['sad', 'sorry', 'disappointed', 'upset', 'cry', 'terrible', 'awful', 'bad', 'wrong']
            },
            'angry': {
                'speed': 1.2,
                'pitch_shift': 0.05,
                'energy': 1.4,
                'keywords': ['angry', 'mad', 'furious', 'annoyed', 'stupid', 'idiot', 'hate', 'damn', 'hell']
            },
            'surprised': {
                'speed': 1.3,
                'pitch_shift': 0.2,
                'energy': 1.3,
                'keywords': ['wow', 'really', 'seriously', 'no way', 'what', 'omg', 'incredible', 'unbelievable', '?!']
            },
            'sleepy': {
                'speed': 0.7,
                'pitch_shift': -0.2,
                'energy': 0.6,
                'keywords': ['tired', 'sleepy', 'yawn', 'exhausted', 'bed', 'sleep', 'zzz']
            },
            'flirty': {
                'speed': 0.9,
                'pitch_shift': -0.05,
                'energy': 0.9,
                'keywords': ['senpai', 'cute', 'handsome', 'darling', 'sweetie', 'honey', 'kiss', 'love you']
            },
            'tsundere': {
                'speed': 1.1,
                'pitch_shift': 0.15,
                'energy': 1.1,
                'keywords': ['baka', 'idiot', 'not like', "it's not", 'whatever', 'hmph', 'stupid']
            }
        }
        
        # Anime-specific expressions that modify emotion
        self.anime_expressions = {
            'kyaa': 'surprised',
            'uwu': 'flirty', 
            'owo': 'surprised',
            'nya': 'happy',
            'ehehe': 'happy',
            'ara ara': 'flirty',
            'baka': 'tsundere',
            'senpai': 'flirty',
            'desu': 'happy',
            'kawaii': 'happy'
        }
    
    def detect_emotion(self, text: str) -> str:
        """Detect emotion from text content"""
        text_lower = text.lower()
        emotion_scores = {emotion: 0 for emotion in self.emotions}
        
        # Check for anime expressions first
        for expression, emotion in self.anime_expressions.items():
            if expression in text_lower:
                emotion_scores[emotion] += 2
        
        # Check for emotion keywords
        for emotion, config in self.emotions.items():
            for keyword in config['keywords']:
                if keyword in text_lower:
                    emotion_scores[emotion] += 1
        
        # Check punctuation patterns
        if '!' in text:
            emotion_scores['happy'] += 1
            emotion_scores['excited'] = emotion_scores.get('excited', 0) + 1
        if '?' in text:
            emotion_scores['surprised'] += 1
        if text.isupper():
            emotion_scores['angry'] += 2
        if '...' in text:
            emotion_scores['sad'] += 1
            emotion_scores['sleepy'] += 1
        
        # Return emotion with highest score, default to 'happy' for Riko's personality
        max_emotion = max(emotion_scores, key=emotion_scores.get)
        return max_emotion if emotion_scores[max_emotion] > 0 else 'happy'
    
    def modify_text_for_emotion(self, text: str, emotion: str) -> str:
        """Modify text to enhance emotional expression"""
        if emotion == 'happy':
            # Add more enthusiasm
            text = text.replace('.', '!')
            if not text.endswith(('!', '?')):
                text += '!'
        elif emotion == 'sad':
            # Add hesitation
            text = re.sub(r'\.', '...', text)
        elif emotion == 'angry':
            # Make more emphatic
            text = text.upper() if len(text) < 50 else text
        elif emotion == 'surprised':
            # Add surprise markers
            if not text.endswith('!'):
                text += '!'
        elif emotion == 'tsundere':
            # Add tsundere filler words
            tsundere_fillers = ['hmph', 'baka', "it's not like I care or anything"]
            if random.random() < 0.3:  # 30% chance
                text += f" {random.choice(tsundere_fillers)}"
        
        return text
    
    def generate_emotional_audio(self, text: str, output_path: str, emotion: Optional[str] = None) -> str:
        """Generate TTS with emotional parameters"""
        
        # Auto-detect emotion if not provided
        if emotion is None:
            emotion = self.detect_emotion(text)
        
        print(f"🎭 Detected emotion: {emotion}")
        
        # Modify text for emotion
        modified_text = self.modify_text_for_emotion(text, emotion)
        
        # Get emotion parameters
        emotion_config = self.emotions.get(emotion, self.emotions['happy'])
        
        # Prepare TTS request with emotional parameters
        url = "http://127.0.0.1:9880/tts"
        
        payload = {
            "text": modified_text,
            "text_lang": char_config['sovits_ping_config']['text_lang'],
            "ref_audio_path": char_config['sovits_ping_config']['ref_audio_path'],
            "prompt_text": char_config['sovits_ping_config']['prompt_text'],
            "prompt_lang": char_config['sovits_ping_config']['prompt_lang'],
            # Emotional parameters (if GPT-SoVITS supports them)
            "speed": emotion_config.get('speed', 1.0),
            "pitch": emotion_config.get('pitch_shift', 0.0),
            "energy": emotion_config.get('energy', 1.0)
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            # Save the response audio
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            print(f"🎵 Generated emotional audio: {emotion}")
            return output_path
            
        except Exception as e:
            print(f"❌ Error in emotional TTS: {e}")
            # Fallback to regular TTS
            return self.fallback_tts(text, output_path)
    
    def fallback_tts(self, text: str, output_path: str) -> str:
        """Fallback to regular TTS if emotional TTS fails"""
        url = "http://127.0.0.1:9880/tts"
        
        payload = {
            "text": text,
            "text_lang": char_config['sovits_ping_config']['text_lang'],
            "ref_audio_path": char_config['sovits_ping_config']['ref_audio_path'],
            "prompt_text": char_config['sovits_ping_config']['prompt_text'],
            "prompt_lang": char_config['sovits_ping_config']['prompt_lang']
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            return output_path
            
        except Exception as e:
            print(f"❌ Fallback TTS also failed: {e}")
            return None

# Convenience function to replace the original sovits_gen
def sovits_gen_emotional(text: str, output_path: str = "output.wav", emotion: Optional[str] = None) -> str:
    """Enhanced TTS generation with emotion detection"""
    emotional_tts = EmotionalTTS()
    return emotional_tts.generate_emotional_audio(text, output_path, emotion)

if __name__ == "__main__":
    # Test emotional TTS
    emotional_tts = EmotionalTTS()
    
    test_phrases = [
        "I'm so happy to see you, senpai!",
        "I'm really sad about this...",
        "What?! That's incredible!",
        "Baka! It's not like I care about you or anything!",
        "I'm so tired... yawn...",
        "You're so cute, darling~"
    ]
    
    for i, phrase in enumerate(test_phrases):
        emotion = emotional_tts.detect_emotion(phrase)
        print(f"Text: {phrase}")
        print(f"Detected emotion: {emotion}")
        print("---")
#!/usr/bin/env python3
"""
Offline Chat - Local AI without internet or API keys
"""

from faster_whisper import WhisperModel
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from server.process.asr_func.asr_push_to_talk import record_and_transcribe
from pathlib import Path
import uuid

def check_local_ai():
    """Check if local AI is available"""
    try:
        from server.process.llm_funcs.local_ai import LocalAI
        return True
    except ImportError:
        return False

def offline_response(text):
    """Generate response using local AI or fallback"""
    try:
        from server.process.llm_funcs.local_ai import LocalAI
        ai = LocalAI()
        return ai.get_response(text)
    except:
        # Simple fallback responses
        responses = {
            'hello': "Hello there! I'm Riko, your offline AI companion!",
            'how are you': "I'm doing great! Thanks for asking, senpai!",
            'what is your name': "I'm Riko, your snarky anime AI assistant!",
            'goodbye': "See you later, senpai! Take care!",
        }
        
        text_lower = text.lower()
        for key, response in responses.items():
            if key in text_lower:
                return response
        
        return "That's interesting! Tell me more about that, senpai!"

def offline_voice_gen(text, output_path):
    """Generate voice using available TTS"""
    try:
        # Try dynamic voice cloning first
        from server.process.tts_func.dynamic_voice_clone import DynamicVoiceClone
        voice_clone = DynamicVoiceClone()
        return voice_clone.generate_speech(text, output_path)
    except:
        try:
            # Fallback to regular TTS
            from server.process.tts_func.sovits_ping import sovits_gen
            return sovits_gen(text, output_path)
        except:
            print("⚠️ Voice synthesis not available in offline mode")
            return None

def main():
    """Main offline chat loop"""
    print('\n========= Offline Riko Chat =========')
    print('🤖 Local AI - No internet required!')
    print('🔒 Complete privacy - everything stays local')
    
    if not check_local_ai():
        print('⚠️ Local AI not configured - using simple responses')
    
    print('Press Ctrl+C to exit\n')
    
    # Initialize Whisper model
    whisper_model = WhisperModel("base.en", device="cpu", compute_type="float32")
    
    while True:
        try:
            # Record and transcribe user input
            conversation_recording = Path("audio") / "conversation.wav"
            conversation_recording.parent.mkdir(parents=True, exist_ok=True)
            
            user_text = record_and_transcribe(whisper_model, conversation_recording)
            if not user_text.strip():
                continue
            
            print(f"👤 You: {user_text}")
            
            # Get offline response
            response = offline_response(user_text)
            print(f"🎌 Riko: {response}")
            
            # Generate and play audio if available
            uid = uuid.uuid4().hex
            output_path = Path("audio") / f"output_{uid}.wav"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if offline_voice_gen(response, output_path):
                try:
                    from server.process.tts_func.sovits_ping import play_audio
                    play_audio(output_path)
                except:
                    print("🔇 Audio playback not available")
            
            # Cleanup
            for fp in Path("audio").glob("*.wav"):
                if fp.is_file():
                    fp.unlink()
                    
        except KeyboardInterrupt:
            print("\n👋 Chat ended")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
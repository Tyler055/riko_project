#!/usr/bin/env python3
"""
Enhanced Voice Chat - Voice chat with emotional synthesis
"""

from faster_whisper import WhisperModel
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from server.process.asr_func.asr_push_to_talk import record_and_transcribe
from server.process.llm_funcs.llm_scr import llm_response
from pathlib import Path
import uuid
import argparse

def detect_emotion(text):
    """Simple emotion detection from text"""
    text_lower = text.lower()
    
    # Emotion keywords
    if any(word in text_lower for word in ['happy', 'joy', 'excited', 'great', 'awesome', 'love']):
        return 'happy'
    elif any(word in text_lower for word in ['sad', 'cry', 'depressed', 'down', 'upset']):
        return 'sad'
    elif any(word in text_lower for word in ['angry', 'mad', 'furious', 'hate', 'annoyed']):
        return 'angry'
    elif any(word in text_lower for word in ['surprised', 'wow', 'amazing', 'incredible']):
        return 'surprised'
    elif any(word in text_lower for word in ['tired', 'sleepy', 'exhausted', 'yawn']):
        return 'sleepy'
    elif any(word in text_lower for word in ['baka', 'stupid', 'idiot']) or '!' in text:
        return 'tsundere'
    elif any(word in text_lower for word in ['ara', 'cute', 'sweet', 'dear']):
        return 'flirty'
    else:
        return 'happy'  # default

def enhanced_sovits_gen(text, output_path, emotion='happy'):
    """Generate audio with emotional parameters"""
    try:
        # Import here to avoid issues if not available
        from server.process.tts_func.emotion_tts import sovits_gen_emotional
        return sovits_gen_emotional(text, output_path, emotion)
    except ImportError:
        # Fallback to basic generation
        from server.process.tts_func.sovits_ping import sovits_gen
        return sovits_gen(text, output_path)

def main():
    """Main enhanced chat loop"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', default='push_to_talk', choices=['push_to_talk', 'live', 'text'])
    args = parser.parse_args()
    
    print('\n========= Enhanced Riko Chat =========')
    print('🎭 Voice chat with emotional synthesis')
    print(f'📱 Mode: {args.mode}')
    print('Press Ctrl+C to exit\n')
    
    if args.mode == 'text':
        # Text mode for testing
        while True:
            try:
                user_text = input("👤 You: ")
                if not user_text.strip():
                    continue
                
                response = llm_response(user_text)
                emotion = detect_emotion(response)
                
                print(f"🎌 Riko ({emotion}): {response}")
                
                # Generate audio
                uid = uuid.uuid4().hex
                output_path = Path("audio") / f"output_{uid}.wav"
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                enhanced_sovits_gen(response, output_path, emotion)
                
                # Play audio
                from server.process.tts_func.sovits_ping import play_audio
                play_audio(output_path)
                
                # Cleanup
                output_path.unlink(missing_ok=True)
                
            except KeyboardInterrupt:
                print("\n👋 Chat ended")
                break
    else:
        # Voice mode (push-to-talk or live)
        whisper_model = WhisperModel("base.en", device="cpu", compute_type="float32")
        
        while True:
            try:
                conversation_recording = Path("audio") / "conversation.wav"
                conversation_recording.parent.mkdir(parents=True, exist_ok=True)
                
                user_text = record_and_transcribe(whisper_model, conversation_recording)
                if not user_text.strip():
                    continue
                
                print(f"👤 You: {user_text}")
                
                response = llm_response(user_text)
                emotion = detect_emotion(response)
                
                print(f"🎌 Riko ({emotion}): {response}")
                
                # Generate and play audio
                uid = uuid.uuid4().hex
                output_path = Path("audio") / f"output_{uid}.wav"
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                enhanced_sovits_gen(response, output_path, emotion)
                
                from server.process.tts_func.sovits_ping import play_audio
                play_audio(output_path)
                
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
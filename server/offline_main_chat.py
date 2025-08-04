from faster_whisper import WhisperModel
from process.asr_func.asr_push_to_talk import record_and_transcribe
from process.llm_funcs.local_ai import llm_response
from process.tts_func.voice_clone_tts import sovits_gen_character, play_audio
from pathlib import Path
import uuid
import time

def main():
    print('\n' + '='*60)
    print('🎌 RIKO OFFLINE AI VOICE ASSISTANT')
    print('='*60)
    print('✨ Features:')
    print('  🤖 Local AI (no internet required)')
    print('  🎵 Local voice synthesis')
    print('  🎤 Voice recognition')
    print('  🎭 Emotional responses')
    print('='*60)
    print()
    
    # Initialize Whisper model
    print("🧠 Loading speech recognition model...")
    whisper_model = WhisperModel("base.en", device="cpu", compute_type="float32")
    print("✅ Speech recognition ready!")
    
    # Test character voice
    print("🎵 Loading character voice...")
    try:
        from process.tts_func.voice_clone_tts import VoiceCloneTTS
        tts = VoiceCloneTTS()
        if tts.voice_available:
            print("✅ Character voice ready!")
        else:
            print("⚠️ Character voice not available, will use text-only mode")
    except Exception as e:
        print(f"⚠️ Character voice error: {e}")
        tts = None
    
    print("\n🎌 Riko is ready to chat!")
    print("💡 Press Ctrl+C to exit")
    print("-" * 40)
    
    while True:
        try:
            # Record audio
            conversation_recording = Path("audio") / "conversation.wav"
            conversation_recording.parent.mkdir(parents=True, exist_ok=True)
            
            print("\n🎤 Listening...")
            user_spoken_text = record_and_transcribe(whisper_model, conversation_recording)
            
            if not user_spoken_text.strip():
                print("⚠️ No speech detected, try again")
                continue
            
            print(f"👤 You said: {user_spoken_text}")
            
            # Get AI response
            print("🤔 Riko is thinking...")
            llm_output = llm_response(user_spoken_text)
            print(f"🎌 Riko: {llm_output}")
            
            # Generate and play voice response
            if tts and tts.voice_available:
                print("🎵 Generating voice...")
                uid = uuid.uuid4().hex
                filename = f"output_{uid}.wav"
                output_wav_path = Path("audio") / filename
                
                audio_path = sovits_gen_character(llm_output, str(output_wav_path))
                
                if audio_path and Path(audio_path).exists():
                    print("🔊 Playing response...")
                    play_audio(output_wav_path)
                    
                    # Clean up audio files
                    try:
                        [fp.unlink() for fp in Path("audio").glob("*.wav") if fp.is_file()]
                    except:
                        pass
                else:
                    print("⚠️ Could not generate voice, continuing with text...")
            
            print("-" * 40)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye! Thanks for chatting with Riko!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Continuing...")

if __name__ == "__main__":
    main()
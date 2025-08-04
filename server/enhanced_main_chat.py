from faster_whisper import WhisperModel
from process.asr_func.live_microphone import LiveMicrophoneRecorder
from process.llm_funcs.llm_scr import llm_response
from process.tts_func.emotion_tts import sovits_gen_emotional
from pathlib import Path
import threading
import time
import uuid
import argparse
import sys

class EnhancedRikoChat:
    def __init__(self, mode="push_to_talk"):
        self.mode = mode
        self.whisper_model = WhisperModel("base.en", device="cpu", compute_type="float32")
        self.live_recorder = None
        self.is_running = False
        
        print(f"🎌 Enhanced Riko Chat initialized in {mode} mode")
    
    def push_to_talk_mode(self):
        """Original push-to-talk functionality with emotional TTS"""
        print('\n========= Enhanced Push-to-Talk Chat =========')
        print('🎭 Now with emotional voice synthesis!')
        print('Press Ctrl+C to exit\n')
        
        while True:
            try:
                conversation_recording = Path("audio") / "conversation.wav"
                conversation_recording.parent.mkdir(parents=True, exist_ok=True)
                
                # Record audio (original method)
                from process.asr_func.asr_push_to_talk import record_and_transcribe
                user_spoken_text = record_and_transcribe(self.whisper_model, conversation_recording)
                
                if not user_spoken_text.strip():
                    print("⚠️ No speech detected, try again")
                    continue
                
                # Get LLM response
                print("🤔 Riko is thinking...")
                llm_output = llm_response(user_spoken_text)
                
                # Generate emotional TTS
                uid = uuid.uuid4().hex
                filename = f"output_{uid}.wav"
                output_wav_path = Path("audio") / filename
                output_wav_path.parent.mkdir(parents=True, exist_ok=True)
                
                print("🎵 Generating emotional voice...")
                audio_path = sovits_gen_emotional(llm_output, str(output_wav_path))
                
                if audio_path:
                    # Play audio
                    from process.tts_func.sovits_ping import play_audio
                    play_audio(output_wav_path)
                    
                    # Clean up
                    [fp.unlink() for fp in Path("audio").glob("*.wav") if fp.is_file()]
                else:
                    print("❌ Failed to generate audio")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def live_microphone_mode(self):
        """Continuous listening with voice activity detection"""
        print('\n========= Live Microphone Mode =========')
        print('🎤 Riko is listening continuously...')
        print('🎭 Speak naturally - she\'ll detect when you start and stop!')
        print('Press Ctrl+C to exit\n')
        
        self.live_recorder = LiveMicrophoneRecorder(self.whisper_model)
        self.is_running = True
        
        # Start listening in a separate thread
        listen_thread = threading.Thread(target=self.live_recorder.start_listening)
        listen_thread.daemon = True
        listen_thread.start()
        
        try:
            while self.is_running:
                # Check for transcriptions
                if self.live_recorder.has_transcription():
                    user_text = self.live_recorder.get_transcription(timeout=0.1)
                    
                    if user_text:
                        print(f"\n👤 You said: {user_text}")
                        
                        # Process with LLM
                        print("🤔 Riko is thinking...")
                        llm_output = llm_response(user_text)
                        print(f"🎌 Riko: {llm_output}")
                        
                        # Generate emotional TTS
                        uid = uuid.uuid4().hex
                        filename = f"output_{uid}.wav"
                        output_wav_path = Path("audio") / filename
                        output_wav_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        print("🎵 Generating emotional voice...")
                        audio_path = sovits_gen_emotional(llm_output, str(output_wav_path))
                        
                        if audio_path:
                            from process.tts_func.sovits_ping import play_audio
                            play_audio(output_wav_path)
                            
                            # Clean up
                            [fp.unlink() for fp in Path("audio").glob("*.wav") if fp.is_file()]
                        
                        print("\n🎧 Listening for more...")
                
                time.sleep(0.1)  # Small delay to prevent busy waiting
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping live microphone...")
            self.is_running = False
            if self.live_recorder:
                self.live_recorder.stop_listening()
            print("👋 Goodbye!")
    
    def interactive_mode(self):
        """Text-based interactive mode for testing"""
        print('\n========= Interactive Text Mode =========')
        print('💬 Type messages to chat with Riko')
        print('🎭 Emotional TTS will be generated for her responses')
        print('Type "quit" to exit\n')
        
        while True:
            try:
                user_input = input("👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Get LLM response
                print("🤔 Riko is thinking...")
                llm_output = llm_response(user_input)
                print(f"🎌 Riko: {llm_output}")
                
                # Generate emotional TTS
                uid = uuid.uuid4().hex
                filename = f"output_{uid}.wav"
                output_wav_path = Path("audio") / filename
                output_wav_path.parent.mkdir(parents=True, exist_ok=True)
                
                print("🎵 Generating emotional voice...")
                audio_path = sovits_gen_emotional(llm_output, str(output_wav_path))
                
                if audio_path:
                    from process.tts_func.sovits_ping import play_audio
                    play_audio(output_wav_path)
                    
                    # Clean up
                    [fp.unlink() for fp in Path("audio").glob("*.wav") if fp.is_file()]
                
                print()  # Empty line for readability
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Enhanced Riko AI Chat")
    parser.add_argument(
        "--mode", 
        choices=["push_to_talk", "live", "text"], 
        default="push_to_talk",
        help="Chat mode: push_to_talk (original), live (continuous), or text (interactive)"
    )
    
    args = parser.parse_args()
    
    print("🎌 Enhanced Riko AI Voice Assistant")
    print("=" * 50)
    print("✨ New Features:")
    print("  🎭 Emotional voice synthesis")
    print("  🎤 Live microphone support")
    print("  💬 Interactive text mode")
    print("  🎵 Enhanced audio processing")
    print("=" * 50)
    
    # Check if GPT-SoVITS server is running
    import requests
    try:
        response = requests.get("http://127.0.0.1:9880", timeout=5)
        print("✅ GPT-SoVITS server is running")
    except:
        print("❌ GPT-SoVITS server not detected!")
        print("💡 Please start the GPT-SoVITS server first:")
        print("   cd riko_project/GPT-SoVITS")
        print("   python api.py")
        sys.exit(1)
    
    # Initialize and run chat
    chat = EnhancedRikoChat(mode=args.mode)
    
    if args.mode == "push_to_talk":
        chat.push_to_talk_mode()
    elif args.mode == "live":
        chat.live_microphone_mode()
    elif args.mode == "text":
        chat.interactive_mode()

if __name__ == "__main__":
    main()
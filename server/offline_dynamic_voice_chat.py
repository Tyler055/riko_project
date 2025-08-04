from faster_whisper import WhisperModel
from process.asr_func.asr_push_to_talk import record_and_transcribe
from process.llm_funcs.local_ai import llm_response  # Uses local AI, no API key needed
from process.tts_func.dynamic_voice_clone import DynamicVoiceClone
from pathlib import Path
import threading
import time

class OfflineDynamicVoiceChat:
    def __init__(self):
        self.whisper_model = None
        self.voice_clone = None
        self.is_speaking = False
        
        print('\n' + '='*70)
        print('🎌 RIKO OFFLINE DYNAMIC VOICE CLONING CHAT')
        print('='*70)
        print('✨ Features:')
        print('  🤖 Local AI (no internet or API keys required)')
        print('  🎵 TRUE voice cloning - says ANY text in your voice')
        print('  🎤 Voice recognition')
        print('  🎭 Emotional responses')
        print('  ⏹️ Interruptible speech')
        print('  💾 Conversation memory')
        print('='*70)
        print()
        
        self.setup_systems()
    
    def setup_systems(self):
        """Initialize all systems"""
        # Initialize Whisper
        print("🧠 Loading speech recognition...")
        self.whisper_model = WhisperModel("base.en", device="cpu", compute_type="float32")
        print("✅ Speech recognition ready!")
        
        # Initialize dynamic voice cloning
        print("🎵 Initializing dynamic voice cloning...")
        self.voice_clone = DynamicVoiceClone()
        
        if self.voice_clone.voice_sample_path.exists():
            print("✅ Dynamic voice cloning ready!")
        else:
            print("❌ Voice sample not found - text only mode")
    
    def listen_for_input(self) -> str:
        """Listen for voice input"""
        conversation_recording = Path("audio") / "conversation.wav"
        conversation_recording.parent.mkdir(parents=True, exist_ok=True)
        
        print("\n🎤 Listening...")
        user_spoken_text = record_and_transcribe(self.whisper_model, conversation_recording)
        
        if user_spoken_text.strip():
            print(f"👤 You said: {user_spoken_text}")
            return user_spoken_text.strip()
        else:
            print("⚠️ No speech detected")
            return ""
    
    def generate_response(self, user_input: str) -> str:
        """Generate response using local AI (no API key needed)"""
        print("🤔 Riko is thinking with local AI...")
        response = llm_response(user_input)
        print(f"🎌 Riko: {response}")
        return response
    
    def speak_response_dynamic(self, text: str):
        """Speak response using dynamic voice cloning"""
        if not self.voice_clone:
            print("⚠️ Voice cloning not available")
            return
        
        print("🎵 Cloning voice to say new text...")
        self.is_speaking = True
        
        # Generate and play voice in background
        def speak_async():
            try:
                audio_path = self.voice_clone.speak_text_dynamic(text, play_immediately=True)
                if audio_path:
                    print("🔊 Playing dynamically cloned voice...")
                    # Clean up temp file after a delay
                    threading.Timer(10.0, lambda: self.cleanup_temp_file(audio_path)).start()
                else:
                    print("❌ Failed to clone voice")
            except Exception as e:
                print(f"❌ Voice cloning error: {e}")
            finally:
                self.is_speaking = False
        
        speak_thread = threading.Thread(target=speak_async)
        speak_thread.daemon = True
        speak_thread.start()
    
    def cleanup_temp_file(self, file_path: str):
        """Clean up temporary audio file"""
        try:
            import os
            if os.path.exists(file_path):
                os.unlink(file_path)
        except:
            pass
    
    def stop_speaking(self):
        """Stop current speech"""
        if self.voice_clone and self.is_speaking:
            self.voice_clone.stop_current_playback()
            self.is_speaking = False
            print("⏹️ Speech interrupted")
    
    def run_conversation_loop(self):
        """Main conversation loop"""
        print("\n🎌 Riko is ready for offline dynamic voice chat!")
        print("💡 Commands:")
        print("   - Speak normally to chat")
        print("   - Say 'stop' or 'quiet' to interrupt speech")
        print("   - Press Ctrl+C to exit")
        print("🔋 Running completely offline - no internet or API keys needed!")
        print("-" * 50)
        
        while True:
            try:
                # Listen for input
                user_input = self.listen_for_input()
                
                if not user_input:
                    continue
                
                # Check for stop commands
                if any(word in user_input.lower() for word in ['stop', 'quiet', 'silence', 'shut up']):
                    if self.is_speaking:
                        self.stop_speaking()
                        continue
                
                # Stop any current speech before responding
                if self.is_speaking:
                    self.stop_speaking()
                    time.sleep(0.5)  # Brief pause
                
                # Generate response with local AI
                response = self.generate_response(user_input)
                
                # Speak response with dynamic voice cloning
                self.speak_response_dynamic(response)
                
                print("-" * 50)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye! Thanks for chatting with Riko!")
                self.stop_speaking()
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                print("Continuing...")

def main():
    """Main function"""
    try:
        chat = OfflineDynamicVoiceChat()
        chat.run_conversation_loop()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    main()
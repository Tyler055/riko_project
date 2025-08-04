from faster_whisper import WhisperModel
from process.asr_func.asr_push_to_talk import record_and_transcribe
from process.llm_funcs.local_ai import llm_response
from process.tts_func.gpt_sovits_clone import GPTSoVITSVoiceClone
from pathlib import Path
import uuid
import time
import threading

class EnhancedOfflineRiko:
    def __init__(self):
        self.whisper_model = None
        self.voice_clone = None
        self.is_speaking = False
        
        print('\n' + '='*60)
        print('🎌 ENHANCED RIKO OFFLINE AI VOICE ASSISTANT')
        print('='*60)
        print('✨ Features:')
        print('  🤖 Local AI (no internet required)')
        print('  🎵 True voice cloning (any text in your voice)')
        print('  🎤 Voice recognition')
        print('  🎭 Emotional responses')
        print('  ⏹️ Interruptible speech')
        print('='*60)
        print()
        
        self.setup_systems()
    
    def setup_systems(self):
        """Initialize all systems"""
        # Initialize Whisper
        print("🧠 Loading speech recognition model...")
        self.whisper_model = WhisperModel("base.en", device="cpu", compute_type="float32")
        print("✅ Speech recognition ready!")
        
        # Initialize voice cloning
        print("🎵 Initializing voice cloning system...")
        self.voice_clone = GPTSoVITSVoiceClone()
        
        if not self.voice_clone.server_running:
            print("⚠️ GPT-SoVITS server not running")
            response = input("Would you like me to start it? (y/n): ").lower().strip()
            if response == 'y':
                if self.voice_clone.start_server():
                    print("✅ Voice cloning ready!")
                else:
                    print("❌ Voice cloning not available - will use text only")
            else:
                print("💡 Voice cloning disabled - text only mode")
        else:
            print("✅ Voice cloning ready!")
    
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
        """Generate AI response"""
        print("🤔 Riko is thinking...")
        response = llm_response(user_input)
        print(f"🎌 Riko: {response}")
        return response
    
    def speak_response(self, text: str):
        """Speak response using voice cloning"""
        if not self.voice_clone or not self.voice_clone.server_running:
            print("⚠️ Voice cloning not available")
            return
        
        print("🎵 Generating cloned voice...")
        self.is_speaking = True
        
        # Generate and play voice in background
        def speak_async():
            try:
                audio_path = self.voice_clone.speak_text(text, play_immediately=True)
                if audio_path:
                    print("🔊 Playing cloned voice...")
                else:
                    print("❌ Failed to generate voice")
            except Exception as e:
                print(f"❌ Voice error: {e}")
            finally:
                self.is_speaking = False
        
        speak_thread = threading.Thread(target=speak_async)
        speak_thread.daemon = True
        speak_thread.start()
    
    def stop_speaking(self):
        """Stop current speech"""
        if self.voice_clone and self.is_speaking:
            self.voice_clone.stop_playback()
            self.is_speaking = False
            print("⏹️ Speech stopped")
    
    def run_conversation_loop(self):
        """Main conversation loop"""
        print("\n🎌 Riko is ready to chat!")
        print("💡 Commands:")
        print("   - Speak normally to chat")
        print("   - Say 'stop' to interrupt speech")
        print("   - Press Ctrl+C to exit")
        print("-" * 40)
        
        while True:
            try:
                # Listen for input
                user_input = self.listen_for_input()
                
                if not user_input:
                    continue
                
                # Check for special commands
                if 'stop' in user_input.lower() and self.is_speaking:
                    self.stop_speaking()
                    continue
                
                # Stop any current speech before responding
                if self.is_speaking:
                    self.stop_speaking()
                    time.sleep(0.5)  # Brief pause
                
                # Generate response
                response = self.generate_response(user_input)
                
                # Speak response
                self.speak_response(response)
                
                print("-" * 40)
                
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
        riko = EnhancedOfflineRiko()
        riko.run_conversation_loop()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    main()
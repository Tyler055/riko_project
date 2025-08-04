from process.llm_funcs.local_ai import llm_response
from process.tts_func.voice_clone_tts import VoiceCloneTTS
import time

def main():
    print('\n' + '='*60)
    print('🎌 RIKO OFFLINE TEXT CHAT')
    print('='*60)
    print('✨ Features:')
    print('  🤖 Local AI (no internet required)')
    print('  🎭 Emotional responses')
    print('  🎵 Optional voice synthesis')
    print('='*60)
    print()
    
    # Initialize character voice (optional)
    print("🎵 Loading character voice...")
    try:
        tts = VoiceCloneTTS()
        voice_available = tts.voice_available
        if voice_available:
            print("✅ Character voice ready!")
        else:
            print("⚠️ Character voice not available")
    except Exception as e:
        print(f"⚠️ Character voice error: {e}")
        tts = None
        voice_available = False
    
    print("\n🎌 Riko is ready to chat!")
    print("💬 Type your messages (or 'quit' to exit)")
    if voice_available:
        print("🎵 Type 'voice on/off' to toggle voice responses")
    print("-" * 40)
    
    voice_enabled = voice_available
    
    while True:
        try:
            # Get user input
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye! Thanks for chatting with Riko!")
                break
            
            if user_input.lower() == 'voice on' and voice_available:
                voice_enabled = True
                print("🎵 Voice responses enabled!")
                continue
            elif user_input.lower() == 'voice off':
                voice_enabled = False
                print("🔇 Voice responses disabled!")
                continue
            
            if not user_input:
                continue
            
            # Get AI response
            print("🤔 Riko is thinking...")
            llm_output = llm_response(user_input)
            print(f"🎌 Riko: {llm_output}")
            
            # Optional voice response
            if voice_enabled and tts and tts.voice_available:
                print("🎵 Speaking with character voice...")
                try:
                    tts.play_character_voice(llm_output)
                except Exception as e:
                    print(f"⚠️ Voice error: {e}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye! Thanks for chatting with Riko!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Continuing...")

if __name__ == "__main__":
    main()
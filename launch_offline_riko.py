#!/usr/bin/env python3
"""
Offline Riko AI Assistant Launcher
Launch different offline interfaces for the Riko AI voice assistant
"""

import subprocess
import sys
import os
import time
import requests
from pathlib import Path

def check_ollama_running():
    """Check if Ollama is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        return True
    except:
        return False

def launch_offline_interface(interface_type):
    """Launch the specified offline interface"""
    
    print(f"\n🚀 Launching {interface_type}...")
    
    try:
        if interface_type == "Offline Text Chat":
            subprocess.run([sys.executable, "server/offline_text_chat.py"])
            
        elif interface_type == "Offline Voice Chat":
            subprocess.run([sys.executable, "server/offline_main_chat.py"])
            
        elif interface_type == "Enhanced Voice Chat":
            subprocess.run([sys.executable, "server/offline_dynamic_voice_chat.py"])
            
        elif interface_type == "Setup Offline AI":
            subprocess.run([sys.executable, "setup_offline_ai.py"])
            
    except KeyboardInterrupt:
        print("\n👋 Interface closed by user")
    except Exception as e:
        print(f"❌ Error launching interface: {e}")

def show_menu():
    """Show the main menu"""
    print("\n" + "="*60)
    print("🎌 RIKO OFFLINE AI VOICE ASSISTANT")
    print("="*60)
    print("Choose your interface:")
    print()
    
    # Check Ollama status
    ollama_status = "✅ Ready" if check_ollama_running() else "❌ Not running"
    print(f"🤖 Local AI Status: {ollama_status}")
    print()
    
    print("🤖 OFFLINE INTERFACES (NO INTERNET REQUIRED!):")
    print("  1. Offline Text Chat - Chat with local AI via text")
    print("  2. Offline Voice Chat - Full voice conversation with local AI")
    print("  3. Enhanced Voice Chat - Dynamic voice cloning (offline, no API key)")
    print("  4. Setup Offline AI - Install and configure local AI system")
    print()
    print("ℹ️  TESTING:")
    print("  5. Test Local AI - Quick test of the AI system")
    print("  6. Test Character Voice - Test your custom voice sample")
    print("  7. Test Voice Cloning - Test generating any text in your voice")
    print("  8. Exit")
    print()
    print("="*60)

def test_local_ai():
    """Test the local AI system"""
    print("\n🧪 Testing Local AI...")
    
    if not check_ollama_running():
        print("❌ Ollama is not running!")
        print("💡 Please run option 3 to set up the offline AI first")
        return
    
    try:
        from server.process.llm_funcs.local_ai import LocalAI
        
        print("🤖 Initializing AI...")
        ai = LocalAI()
        
        print("💬 Sending test message...")
        response = ai.get_response("Hello! Can you introduce yourself?")
        
        print(f"\n🎌 Riko says:")
        print(f"   {response}")
        print("\n✅ Local AI is working perfectly!")
        
    except Exception as e:
        print(f"❌ Error testing AI: {e}")
        print("💡 Try running the setup first (option 3)")

def test_voice_synthesis():
    """Test the character voice system"""
    print("\n🎵 Testing Character Voice...")
    
    try:
        from server.process.tts_func.voice_clone_tts import VoiceCloneTTS
        
        print("🎤 Loading character voice...")
        tts = VoiceCloneTTS()
        
        if tts.voice_available:
            print("✅ Character voice ready!")
            
            test_text = "Hello! I'm Riko, your offline AI companion. Nice to meet you!"
            print(f"🗣️ Speaking with character voice: {test_text}")
            
            tts.play_character_voice(test_text, "happy")
            print("✅ Character voice is working!")
        else:
            print("❌ Character voice not available")
            print("💡 Make sure main_sample.wav exists in character_files/")
            
    except Exception as e:
        print(f"❌ Error testing character voice: {e}")

def test_voice_cloning():
    """Test the voice cloning system"""
    print("\n🎵 Testing Voice Cloning...")
    
    try:
        subprocess.run([sys.executable, "test_voice_cloning.py"])
    except Exception as e:
        print(f"❌ Error testing voice cloning: {e}")

def main():
    """Main launcher function"""
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    print("🎌 Welcome to Riko Offline AI Voice Assistant!")
    print(f"📁 Working directory: {project_dir}")
    
    while True:
        show_menu()
        
        try:
            choice = input("👉 Enter your choice (1-8): ").strip()
            
            if choice == "1":
                launch_offline_interface("Offline Text Chat")
            elif choice == "2":
                launch_offline_interface("Offline Voice Chat")
            elif choice == "3":
                launch_offline_interface("Enhanced Voice Chat")
            elif choice == "4":
                launch_offline_interface("Setup Offline AI")
            elif choice == "5":
                test_local_ai()
            elif choice == "6":
                test_voice_synthesis()
            elif choice == "7":
                test_voice_cloning()
            elif choice == "8":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-8.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Pause before showing menu again
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Offline AI Setup Script for Riko
This script helps you set up a completely offline AI system
"""

import subprocess
import sys
import os
import requests
import time
from pathlib import Path

def check_ollama_installed():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def check_ollama_running():
    """Check if Ollama service is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def install_ollama_windows():
    """Instructions for installing Ollama on Windows"""
    print("📥 Installing Ollama for Windows...")
    print()
    print("Please follow these steps:")
    print("1. Go to https://ollama.ai/download")
    print("2. Download 'Ollama for Windows'")
    print("3. Run the installer")
    print("4. Restart this script when done")
    print()
    input("Press Enter when you've installed Ollama...")

def start_ollama():
    """Start Ollama service"""
    print("🚀 Starting Ollama service...")
    try:
        if os.name == 'nt':  # Windows
            subprocess.Popen(['ollama', 'serve'], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:  # Linux/Mac
            subprocess.Popen(['ollama', 'serve'])
        
        # Wait for service to start
        print("⏳ Waiting for Ollama to start...")
        for i in range(30):
            if check_ollama_running():
                print("✅ Ollama is running!")
                return True
            time.sleep(1)
            print(f"   Waiting... ({i+1}/30)")
        
        print("⚠️ Ollama may not have started properly")
        return False
    except Exception as e:
        print(f"❌ Error starting Ollama: {e}")
        return False

def download_model():
    """Download the AI model"""
    print("📥 Downloading AI model (llama3.2:3b)...")
    print("💡 This is a 2GB download and may take several minutes")
    
    try:
        process = subprocess.Popen(
            ['ollama', 'pull', 'llama3.2:3b'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        for line in process.stdout:
            print(f"   {line.strip()}")
        
        process.wait()
        
        if process.returncode == 0:
            print("✅ Model downloaded successfully!")
            return True
        else:
            print("❌ Model download failed")
            return False
            
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        return False

def test_local_ai():
    """Test the local AI system"""
    print("🧪 Testing local AI system...")
    
    try:
        from server.process.llm_funcs.local_ai import LocalAI
        
        ai = LocalAI()
        response = ai.get_response("Hello, can you hear me?")
        
        print(f"🎌 Riko says: {response}")
        print("✅ Local AI is working!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing AI: {e}")
        return False

def test_local_tts():
    """Test the local TTS system"""
    print("🎵 Testing local voice synthesis...")
    
    try:
        from server.process.tts_func.local_tts import LocalTTS
        
        tts = LocalTTS()
        if tts.engine:
            print("✅ Voice synthesis is working!")
            
            # Test voice
            test_response = input("Would you like to hear a test voice? (y/n): ").lower()
            if test_response == 'y':
                tts.speak_directly("Hello! I'm Riko, your offline AI companion!")
            
            return True
        else:
            print("⚠️ Voice synthesis not available")
            return False
            
    except Exception as e:
        print(f"❌ Error testing TTS: {e}")
        return False

def main():
    print("🎌 Riko Offline AI Setup")
    print("=" * 50)
    print("This script will set up a completely offline AI system")
    print("No internet connection required after setup!")
    print("=" * 50)
    print()
    
    # Check if Ollama is installed
    if not check_ollama_installed():
        print("❌ Ollama not found")
        install_ollama_windows()
        
        # Check again
        if not check_ollama_installed():
            print("❌ Ollama still not found. Please install it manually.")
            return
    else:
        print("✅ Ollama is installed")
    
    # Check if Ollama is running
    if not check_ollama_running():
        print("⚠️ Ollama service not running")
        if not start_ollama():
            print("❌ Could not start Ollama service")
            print("💡 Try running 'ollama serve' in a separate terminal")
            return
    else:
        print("✅ Ollama service is running")
    
    # Download model
    print("\n📥 Checking AI model...")
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if 'llama3.2:3b' not in result.stdout:
            if not download_model():
                print("❌ Could not download AI model")
                return
        else:
            print("✅ AI model is already downloaded")
    except Exception as e:
        print(f"❌ Error checking model: {e}")
        return
    
    # Test systems
    print("\n🧪 Testing systems...")
    
    ai_works = test_local_ai()
    tts_works = test_local_tts()
    
    print("\n" + "=" * 50)
    print("🎉 SETUP COMPLETE!")
    print("=" * 50)
    
    if ai_works:
        print("✅ Local AI: Working")
    else:
        print("❌ Local AI: Not working")
    
    if tts_works:
        print("✅ Voice synthesis: Working")
    else:
        print("⚠️ Voice synthesis: Not available (text-only mode)")
    
    print("\n🚀 How to use:")
    print("1. Text chat: python server/offline_text_chat.py")
    print("2. Voice chat: python server/offline_main_chat.py")
    print("3. Web interface: python launch_riko.py (choose offline options)")
    
    print("\n💡 Your AI companion is now completely offline!")
    print("No internet connection or API keys required!")

if __name__ == "__main__":
    main()
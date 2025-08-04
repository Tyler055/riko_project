#!/usr/bin/env python3
"""
Riko AI Voice Assistant - Main Entry Point
A clean, unified launcher for all Riko functionality
"""

import subprocess
import sys
import os
import time
import requests
from pathlib import Path

def check_gpt_sovits_server():
    """Check if GPT-SoVITS server is running"""
    try:
        response = requests.get("http://127.0.0.1:9880", timeout=3)
        return True
    except:
        return False

def start_gpt_sovits_server():
    """Start GPT-SoVITS server"""
    print("🚀 Starting GPT-SoVITS server...")
    
    gpt_sovits_path = Path("GPT-SoVITS")
    if not gpt_sovits_path.exists():
        print("❌ GPT-SoVITS directory not found!")
        return False
    
    try:
        process = subprocess.Popen(
            [sys.executable, "api.py"],
            cwd=gpt_sovits_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print("⏳ Waiting for GPT-SoVITS server to start...")
        for i in range(30):
            if check_gpt_sovits_server():
                print("✅ GPT-SoVITS server is running!")
                return True
            time.sleep(1)
            print(f"   Waiting... ({i+1}/30)")
        
        print("❌ GPT-SoVITS server failed to start")
        return False
        
    except Exception as e:
        print(f"❌ Error starting GPT-SoVITS server: {e}")
        return False

def launch_interface(interface_type):
    """Launch the specified interface"""
    
    # Check server requirements
    if interface_type in ["Voice Chat", "Enhanced Chat", "Web Interface"]:
        if not check_gpt_sovits_server():
            print("⚠️ GPT-SoVITS server required for this mode")
            response = input("Start GPT-SoVITS server? (y/n): ").lower().strip()
            
            if response == 'y':
                if not start_gpt_sovits_server():
                    print("❌ Cannot continue without GPT-SoVITS server")
                    return
            else:
                print("💡 Please start GPT-SoVITS server manually:")
                print("   cd GPT-SoVITS && python api.py")
                return
    
    print(f"\n🚀 Launching {interface_type}...")
    
    try:
        if interface_type == "Voice Chat":
            subprocess.run([sys.executable, "core/voice_chat.py"])
        elif interface_type == "Enhanced Chat":
            subprocess.run([sys.executable, "core/enhanced_chat.py"])
        elif interface_type == "Web Interface":
            subprocess.run([sys.executable, "interfaces/web_interface.py"])
        elif interface_type == "Offline Chat":
            subprocess.run([sys.executable, "core/offline_chat.py"])
        elif interface_type == "Setup":
            subprocess.run([sys.executable, "utils/setup.py"])
            
    except KeyboardInterrupt:
        print("\n👋 Interface closed")
    except Exception as e:
        print(f"❌ Error launching interface: {e}")

def show_menu():
    """Show the main menu"""
    print("\n" + "="*50)
    print("🎌 RIKO AI VOICE ASSISTANT")
    print("="*50)
    
    # Server status
    server_status = "✅ Running" if check_gpt_sovits_server() else "❌ Stopped"
    print(f"🔧 GPT-SoVITS Server: {server_status}")
    print()
    
    print("Choose your interface:")
    print("  1. Voice Chat - Basic voice conversation")
    print("  2. Enhanced Chat - Voice with emotions")
    print("  3. Web Interface - Browser-based GUI")
    print("  4. Offline Chat - No internet required")
    print()
    print("  5. Setup - Install dependencies")
    print("  6. Start GPT-SoVITS Server")
    print("  7. Exit")
    print("="*50)

def main():
    """Main launcher function"""
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    print("🎌 Welcome to Riko AI Voice Assistant!")
    
    while True:
        show_menu()
        
        try:
            choice = input("👉 Enter your choice (1-7): ").strip()
            
            if choice == "1":
                launch_interface("Voice Chat")
            elif choice == "2":
                launch_interface("Enhanced Chat")
            elif choice == "3":
                launch_interface("Web Interface")
            elif choice == "4":
                launch_interface("Offline Chat")
            elif choice == "5":
                launch_interface("Setup")
            elif choice == "6":
                start_gpt_sovits_server()
            elif choice == "7":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-7.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
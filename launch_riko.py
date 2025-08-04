#!/usr/bin/env python3
"""
Riko AI Assistant Launcher
Launch different interfaces for the Riko AI voice assistant
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
        print("💡 Make sure GPT-SoVITS is properly installed in the project directory")
        return False
    
    try:
        # Start server in background
        process = subprocess.Popen(
            [sys.executable, "api.py"],
            cwd=gpt_sovits_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        print("⏳ Waiting for GPT-SoVITS server to start...")
        for i in range(30):  # Wait up to 30 seconds
            if check_gpt_sovits_server():
                print("✅ GPT-SoVITS server is running!")
                return True
            time.sleep(1)
            print(f"   Waiting... ({i+1}/30)")
        
        print("❌ GPT-SoVITS server failed to start within 30 seconds")
        return False
        
    except Exception as e:
        print(f"❌ Error starting GPT-SoVITS server: {e}")
        return False

def launch_interface(interface_type):
    """Launch the specified interface"""
    
    # Check if GPT-SoVITS server is running
    if not check_gpt_sovits_server():
        print("⚠️ GPT-SoVITS server not detected")
        response = input("Would you like me to start it? (y/n): ").lower().strip()
        
        if response == 'y':
            if not start_gpt_sovits_server():
                print("❌ Cannot continue without GPT-SoVITS server")
                return
        else:
            print("💡 Please start GPT-SoVITS server manually:")
            print("   cd riko_project/GPT-SoVITS")
            print("   python api.py")
            return
    else:
        print("✅ GPT-SoVITS server is running")
    
    print(f"\n🚀 Launching {interface_type}...")
    
    try:
        if interface_type == "Enhanced Chat (Push-to-Talk)":
            subprocess.run([sys.executable, "server/enhanced_main_chat.py", "--mode", "push_to_talk"])
            
        elif interface_type == "Enhanced Chat (Live Microphone)":
            subprocess.run([sys.executable, "server/enhanced_main_chat.py", "--mode", "live"])
            
        elif interface_type == "Enhanced Chat (Text Mode)":
            subprocess.run([sys.executable, "server/enhanced_main_chat.py", "--mode", "text"])
            
        elif interface_type == "Web Interface":
            subprocess.run([sys.executable, "client/web_interface.py"])
            
        elif interface_type == "VRM 3D Interface":
            subprocess.run([sys.executable, "client/vrm_interface.py"])
            
        elif interface_type == "Original Chat":
            subprocess.run([sys.executable, "server/main_chat.py"])
            
    except KeyboardInterrupt:
        print("\n👋 Interface closed by user")
    except Exception as e:
        print(f"❌ Error launching interface: {e}")

def show_menu():
    """Show the main menu"""
    print("\n" + "="*60)
    print("🎌 RIKO AI VOICE ASSISTANT LAUNCHER")
    print("="*60)
    print("Choose your interface:")
    print()
    print("📱 ENHANCED INTERFACES (NEW!):")
    print("  1. Enhanced Chat (Push-to-Talk) - Original with emotions")
    print("  2. Enhanced Chat (Live Microphone) - Continuous listening")
    print("  3. Enhanced Chat (Text Mode) - Text-based testing")
    print("  4. Web Interface - Browser-based GUI")
    print("  5. VRM 3D Interface - 3D anime character")
    print()
    print("🔧 CLASSIC:")
    print("  6. Original Chat - Basic push-to-talk")
    print()
    print("⚙️ UTILITIES:")
    print("  7. Check GPT-SoVITS Server Status")
    print("  8. Start GPT-SoVITS Server")
    print("  9. Exit")
    print()
    print("="*60)

def main():
    """Main launcher function"""
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    print("🎌 Welcome to Riko AI Voice Assistant!")
    print(f"📁 Working directory: {project_dir}")
    
    while True:
        show_menu()
        
        try:
            choice = input("👉 Enter your choice (1-9): ").strip()
            
            if choice == "1":
                launch_interface("Enhanced Chat (Push-to-Talk)")
            elif choice == "2":
                launch_interface("Enhanced Chat (Live Microphone)")
            elif choice == "3":
                launch_interface("Enhanced Chat (Text Mode)")
            elif choice == "4":
                launch_interface("Web Interface")
            elif choice == "5":
                launch_interface("VRM 3D Interface")
            elif choice == "6":
                launch_interface("Original Chat")
            elif choice == "7":
                if check_gpt_sovits_server():
                    print("✅ GPT-SoVITS server is running on http://127.0.0.1:9880")
                else:
                    print("❌ GPT-SoVITS server is not running")
            elif choice == "8":
                start_gpt_sovits_server()
            elif choice == "9":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-9.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Pause before showing menu again
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Setup true voice cloning using Coqui TTS (XTTS)
This will give you REAL voice synthesis - new words in your voice
"""
import subprocess
import sys
import os

def install_coqui_tts():
    """Install Coqui TTS for true voice cloning"""
    print("🎌 Setting up TRUE Voice Cloning with Coqui TTS")
    print("=" * 60)
    
    print("📦 Installing Coqui TTS...")
    try:
        # Install TTS
        subprocess.run([sys.executable, "-m", "pip", "install", "TTS"], check=True)
        print("✅ Coqui TTS installed successfully!")
        
        # Test import
        import TTS
        print(f"✅ TTS version: {TTS.__version__}")
        
        return True
        
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return False

def test_voice_cloning():
    """Test voice cloning with new sentences"""
    try:
        from TTS.api import TTS
        
        print("\n🎵 Initializing voice cloning model...")
        
        # Initialize TTS with voice cloning model
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        
        print("✅ Model loaded!")
        
        # Test sentences (completely different from your sample)
        test_sentences = [
            "Hello Tyler, this is your voice saying something completely new.",
            "I can now speak any text you want in your voice.",
            "This is true voice synthesis, not just playing audio clips."
        ]
        
        voice_sample = "character_files/main_sample.wav"
        
        for i, sentence in enumerate(test_sentences, 1):
            print(f"\n🗣️ Generating: '{sentence}'")
            output_file = f"true_voice_clone_{i}.wav"
            
            # Generate speech in your voice
            tts.tts_to_file(
                text=sentence,
                speaker_wav=voice_sample,
                language="en",
                file_path=output_file
            )
            
            print(f"✅ Generated: {output_file}")
            
        print("\n🎉 SUCCESS! You now have true voice synthesis!")
        print("These files contain your voice saying DIFFERENT words!")
        
    except Exception as e:
        print(f"❌ Voice cloning test failed: {e}")
        print("💡 Try: pip install TTS torch torchaudio")

def main():
    print("🎯 This will give you REAL voice synthesis:")
    print("   ✅ Your voice saying ANY text")
    print("   ✅ Not just playing audio clips")
    print("   ✅ True text-to-speech with voice cloning")
    print()
    
    if install_coqui_tts():
        test_voice_cloning()
    else:
        print("❌ Setup failed. Try manual installation:")
        print("   pip install TTS torch torchaudio")

if __name__ == "__main__":
    main()
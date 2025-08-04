#!/usr/bin/env python3
"""
Basic Voice Chat - Core Riko functionality
Clean implementation of the original voice chat system
"""

from faster_whisper import WhisperModel
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from server.process.asr_func.asr_push_to_talk import record_and_transcribe
from server.process.llm_funcs.llm_scr import llm_response
from server.process.tts_func.sovits_ping import sovits_gen, play_audio
from pathlib import Path
import uuid

def main():
    """Main voice chat loop"""
    print('\n========= Riko Voice Chat =========')
    print('🎤 Push-to-talk voice conversation')
    print('Press Ctrl+C to exit\n')
    
    # Initialize Whisper model
    whisper_model = WhisperModel("base.en", device="cpu", compute_type="float32")
    
    while True:
        try:
            # Record and transcribe user input
            conversation_recording = Path("audio") / "conversation.wav"
            conversation_recording.parent.mkdir(parents=True, exist_ok=True)
            
            user_text = record_and_transcribe(whisper_model, conversation_recording)
            if not user_text.strip():
                continue
            
            print(f"👤 You: {user_text}")
            
            # Get LLM response
            response = llm_response(user_text)
            print(f"🎌 Riko: {response}")
            
            # Generate and play audio
            uid = uuid.uuid4().hex
            output_path = Path("audio") / f"output_{uid}.wav"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            sovits_gen(response, output_path)
            play_audio(output_path)
            
            # Cleanup
            for fp in Path("audio").glob("*.wav"):
                if fp.is_file():
                    fp.unlink()
                    
        except KeyboardInterrupt:
            print("\n👋 Chat ended")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
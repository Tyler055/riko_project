import gradio as gr
import asyncio
import threading
import queue
import numpy as np
import soundfile as sf
import tempfile
import os
from pathlib import Path
import sys

# Add server path to import modules
sys.path.append(str(Path(__file__).parent.parent / "server"))

from process.asr_func.asr_push_to_talk import record_and_transcribe
from process.llm_funcs.llm_scr import llm_response
from process.tts_func.sovits_ping import sovits_gen
from faster_whisper import WhisperModel

class RikoWebInterface:
    def __init__(self):
        self.whisper_model = WhisperModel("base.en", device="cpu", compute_type="float32")
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.conversation_history = []
        
    def process_audio_input(self, audio_data, sample_rate):
        """Process audio input from the web interface"""
        if audio_data is None:
            return "No audio received", None, self.conversation_history
            
        # Save audio to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            sf.write(tmp_file.name, audio_data, sample_rate)
            
            # Transcribe audio
            segments, _ = self.whisper_model.transcribe(tmp_file.name)
            user_text = " ".join([segment.text for segment in segments])
            
            # Clean up temp file
            os.unlink(tmp_file.name)
            
        if not user_text.strip():
            return "No speech detected", None, self.conversation_history
            
        # Get LLM response
        riko_response = llm_response(user_text)
        
        # Generate TTS
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_output:
            audio_path = sovits_gen(riko_response, tmp_output.name)
            
        # Update conversation history
        self.conversation_history.append(f"You: {user_text}")
        self.conversation_history.append(f"Riko: {riko_response}")
        
        return user_text, audio_path, "\n".join(self.conversation_history[-10:])  # Last 10 messages
    
    def create_interface(self):
        """Create the Gradio web interface"""
        with gr.Blocks(title="Riko AI Voice Assistant", theme=gr.themes.Soft()) as interface:
            gr.Markdown("# 🎌 Riko AI Voice Assistant")
            gr.Markdown("Talk to Riko, your anime AI companion!")
            
            with gr.Row():
                with gr.Column(scale=2):
                    # Audio input
                    audio_input = gr.Audio(
                        sources=["microphone"],
                        type="numpy",
                        label="🎤 Talk to Riko",
                        streaming=False
                    )
                    
                    # Text display
                    transcription_output = gr.Textbox(
                        label="📝 What you said",
                        interactive=False
                    )
                    
                    # Audio output
                    audio_output = gr.Audio(
                        label="🔊 Riko's Response",
                        autoplay=True
                    )
                    
                with gr.Column(scale=1):
                    # Conversation history
                    conversation_display = gr.Textbox(
                        label="💬 Conversation History",
                        lines=15,
                        max_lines=20,
                        interactive=False
                    )
                    
                    # Clear button
                    clear_btn = gr.Button("🗑️ Clear History", variant="secondary")
            
            # Process audio when uploaded
            audio_input.change(
                fn=self.process_audio_input,
                inputs=[audio_input],
                outputs=[transcription_output, audio_output, conversation_display]
            )
            
            # Clear conversation
            def clear_conversation():
                self.conversation_history = []
                return "", ""
                
            clear_btn.click(
                fn=clear_conversation,
                outputs=[conversation_display, transcription_output]
            )
            
        return interface

def main():
    riko_interface = RikoWebInterface()
    interface = riko_interface.create_interface()
    
    print("🚀 Starting Riko Web Interface...")
    print("📱 Open your browser to interact with Riko!")
    
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True
    )

if __name__ == "__main__":
    main()
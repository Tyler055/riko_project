import sounddevice as sd
import numpy as np
import threading
import queue
import time
from collections import deque
import soundfile as sf
import tempfile
import os

class LiveMicrophoneRecorder:
    def __init__(self, whisper_model, sample_rate=16000, chunk_duration=0.5):
        self.whisper_model = whisper_model
        self.sample_rate = sample_rate
        self.chunk_size = int(sample_rate * chunk_duration)
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.recording_thread = None
        
        # Voice Activity Detection parameters
        self.silence_threshold = 0.01  # Adjust based on your microphone
        self.min_speech_duration = 1.0  # Minimum seconds of speech
        self.max_silence_duration = 2.0  # Max seconds of silence before stopping
        
        # Audio buffer for VAD
        self.audio_buffer = deque(maxlen=int(sample_rate * 10))  # 10 second buffer
        self.speech_buffer = []
        self.silence_counter = 0
        self.speech_detected = False
        
    def audio_callback(self, indata, frames, time, status):
        """Callback function for audio stream"""
        if status:
            print(f"Audio callback status: {status}")
        
        # Add audio to buffer
        audio_chunk = indata[:, 0]  # Take first channel
        self.audio_buffer.extend(audio_chunk)
        
        # Simple VAD based on RMS energy
        rms = np.sqrt(np.mean(audio_chunk**2))
        
        if rms > self.silence_threshold:
            # Speech detected
            if not self.speech_detected:
                print("🎤 Speech detected, starting recording...")
                self.speech_detected = True
                self.speech_buffer = []
            
            self.speech_buffer.extend(audio_chunk)
            self.silence_counter = 0
        else:
            # Silence detected
            if self.speech_detected:
                self.silence_counter += len(audio_chunk) / self.sample_rate
                self.speech_buffer.extend(audio_chunk)  # Include some silence
                
                # Check if we should stop recording
                if self.silence_counter > self.max_silence_duration:
                    if len(self.speech_buffer) / self.sample_rate > self.min_speech_duration:
                        # We have enough speech, process it
                        self.process_speech_buffer()
                    
                    # Reset for next speech
                    self.speech_detected = False
                    self.silence_counter = 0
                    self.speech_buffer = []
    
    def process_speech_buffer(self):
        """Process the collected speech buffer"""
        if not self.speech_buffer:
            return
            
        print("🎯 Processing speech...")
        
        # Convert to numpy array
        audio_data = np.array(self.speech_buffer, dtype=np.float32)
        
        # Save to temporary file for Whisper
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            sf.write(tmp_file.name, audio_data, self.sample_rate)
            
            # Transcribe
            try:
                segments, _ = self.whisper_model.transcribe(tmp_file.name)
                transcription = " ".join([segment.text for segment in segments])
                
                if transcription.strip():
                    print(f"📝 Transcription: {transcription}")
                    # Put transcription in queue for main thread
                    self.audio_queue.put(transcription.strip())
                else:
                    print("⚠️ No speech detected in audio")
                    
            except Exception as e:
                print(f"❌ Transcription error: {e}")
            finally:
                # Clean up temp file
                os.unlink(tmp_file.name)
    
    def start_listening(self):
        """Start continuous listening"""
        if self.is_recording:
            print("Already recording!")
            return
            
        print("🎧 Starting live microphone listening...")
        print("💡 Speak naturally - Riko will detect when you start and stop talking")
        print("🛑 Press Ctrl+C to stop")
        
        self.is_recording = True
        
        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                callback=self.audio_callback,
                blocksize=self.chunk_size,
                dtype=np.float32
            ):
                while self.is_recording:
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            print("\n🛑 Stopping live microphone...")
        except Exception as e:
            print(f"❌ Audio stream error: {e}")
        finally:
            self.is_recording = False
    
    def stop_listening(self):
        """Stop continuous listening"""
        self.is_recording = False
    
    def get_transcription(self, timeout=None):
        """Get the next transcription from the queue"""
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def has_transcription(self):
        """Check if there's a transcription available"""
        return not self.audio_queue.empty()

# Example usage
if __name__ == "__main__":
    from faster_whisper import WhisperModel
    
    print("Loading Whisper model...")
    whisper_model = WhisperModel("base.en", device="cpu", compute_type="float32")
    
    recorder = LiveMicrophoneRecorder(whisper_model)
    
    try:
        recorder.start_listening()
    except KeyboardInterrupt:
        print("\nExiting...")
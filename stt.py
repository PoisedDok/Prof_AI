import pyaudio
import wave
import time
import whisper
import os

# Adjust as needed:
MODEL_NAME = "base"  # or "small", "medium", etc.

class OfflineSTT:
    def __init__(self):
        print(f"Loading Whisper model '{MODEL_NAME}' (this may take time)...")
        self.model = whisper.load_model(MODEL_NAME)
        print("Whisper model loaded.")

    def record_and_transcribe(self, record_seconds=5, output_wav="temp.wav"):
        """Records audio for 'record_seconds' then transcribes with Whisper."""
        print("Recording microphone input...")
        chunk = 1024
        sample_format = pyaudio.paInt16
        channels = 1
        fs = 16000  # 16kHz is enough for speech

        p = pyaudio.PyAudio()
        stream = p.open(format=sample_format, channels=channels, rate=fs, input=True, frames_per_buffer=chunk)
        
        frames = []
        for _ in range(0, int(fs / chunk * record_seconds)):
            data = stream.read(chunk)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        p.terminate()

        # Save as WAV
        wf = wave.open(output_wav, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))
        wf.close()

        print("Transcribing...")
        try:
            result = self.model.transcribe(output_wav, language='en')
            text = result["text"].strip()
            return text
        except Exception as e:
            print(f"STT error: {e}")
            return ""

# Usage example:
# stt_engine = OfflineSTT()
# text = stt_engine.record_and_transcribe(5)
# print("Recognized text:", text)

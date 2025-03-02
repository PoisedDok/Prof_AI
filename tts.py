import os
import asyncio
from PyQt5.QtCore import QThread, pyqtSignal
import edge_tts
import simpleaudio as sa
from pydub import AudioSegment

class TTSThread(QThread):
    speaking = pyqtSignal()
    finished = pyqtSignal()

    def __init__(self, text, voice="en-US-AriaNeural"):
        super().__init__()
        self.text = text
        self.voice = voice
        self.output_mp3 = "speech.mp3"
        self.output_wav = "speech.wav"

    async def generate_audio(self):
        """Generate TTS audio file in MP3 format."""
        try:
            tts = edge_tts.Communicate(self.text, self.voice)
            await tts.save(self.output_mp3)
        except Exception as e:
            print(f"Error generating TTS audio: {e}")

    def convert_mp3_to_wav(self):
        """Convert MP3 to WAV format for playback."""
        try:
            audio = AudioSegment.from_file(self.output_mp3, format="mp3")
            audio.export(self.output_wav, format="wav")
        except Exception as e:
            print(f"Error converting MP3 to WAV: {e}")

    def play_audio(self):
        """Play the WAV file using simpleaudio."""
        try:
            wave_obj = sa.WaveObject.from_wave_file(self.output_wav)
            play_obj = wave_obj.play()
            play_obj.wait_done()  # Block until playback is finished
        except Exception as e:
            print(f"Error playing TTS audio: {e}")
        finally:
            # Cleanup files
            if os.path.exists(self.output_mp3):
                os.remove(self.output_mp3)
            if os.path.exists(self.output_wav):
                os.remove(self.output_wav)

    def run(self):
        """Main TTS processing function."""
        self.speaking.emit()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.generate_audio())  # Generate MP3
        self.convert_mp3_to_wav()  # Convert MP3 to WAV
        self.play_audio()  # Play the WAV file
        self.finished.emit()


class OfflineTTS:
    def __init__(self, default_voice="en-US-AriaNeural"):
        self.tts_thread = None
        self.voice = default_voice

    def set_voice(self, voice):
        """Change the voice dynamically."""
        self.voice = voice

    def speak(self, text, on_speaking=None, on_finished=None):
        """Generate and play speech asynchronously."""
        if self.tts_thread and self.tts_thread.isRunning():
            self.tts_thread.terminate()

        self.tts_thread = TTSThread(text, voice=self.voice)
        if on_speaking:
            self.tts_thread.speaking.connect(on_speaking)
        if on_finished:
            self.tts_thread.finished.connect(on_finished)
        self.tts_thread.start()

import pyttsx3
from PyQt5.QtCore import QThread, pyqtSignal


class TTSThread(QThread):
    speaking = pyqtSignal()
    finished = pyqtSignal()

    def __init__(self, text):
        super().__init__()
        self.text = text

    def run(self):
        self.speaking.emit()  # Emit the speaking signal

        # Create a new pyttsx3 engine instance for this thread
        engine = pyttsx3.init()
        engine.setProperty("rate", 160)  # Set the desired rate
        engine.setProperty("volume", 1.0)  # Set the desired volume
        voices = engine.getProperty("voices")
        if voices:
            engine.setProperty("voice", voices[0].id)  # Set the desired voice

        # Run the text-to-speech
        engine.say(self.text)
        engine.runAndWait()

        self.finished.emit()  # Emit the finished signal


class OfflineTTS:
    def __init__(self):
        self.tts_thread = None  # Initialize tts_thread attribute

    def speak(self, text, on_speaking=None, on_finished=None):
        # Stop any ongoing speech safely
        if self.tts_thread and self.tts_thread.isRunning():
            self.tts_thread.terminate()

        # Create a new TTSThread for the current speech
        self.tts_thread = TTSThread(text)
        if on_speaking:
            self.tts_thread.speaking.connect(on_speaking)
        if on_finished:
            self.tts_thread.finished.connect(on_finished)
        self.tts_thread.start()

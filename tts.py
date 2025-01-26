import pyttsx3
from PyQt5.QtCore import QThread, pyqtSignal


class TTSThread(QThread):
    speaking = pyqtSignal()
    finished = pyqtSignal()

    def __init__(self, text, engine):
        super().__init__()
        self.text = text
        self.engine = engine

    def run(self):
        self.speaking.emit()  # Emit the speaking signal
        self.engine.say(self.text)
        self.engine.runAndWait()
        self.finished.emit()


class OfflineTTS:
    def __init__(self):
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty("voices")
        if voices:
            self.engine.setProperty("voice", voices[0].id)  # Change index for a different voice
        self.engine.setProperty("rate", 160)
        self.engine.setProperty("volume", 1.0)
        self.tts_thread = None  # Initialize tts_thread attribute

    def speak(self, text, on_speaking=None, on_finished=None):
        if self.tts_thread and self.tts_thread.isRunning():
            self.tts_thread.terminate()  # Stop any ongoing speech safely

        self.tts_thread = TTSThread(text, self.engine)
        if on_speaking:
            self.tts_thread.speaking.connect(on_speaking)
        if on_finished:
            self.tts_thread.finished.connect(on_finished)
        self.tts_thread.start()

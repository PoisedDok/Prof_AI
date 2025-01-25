import pyttsx3
from PyQt5.QtCore import QThread, pyqtSignal


class TTSThread(QThread):
    """
    Thread for handling text-to-speech in the background.
    """
    finished = pyqtSignal()  # Signal to notify when TTS is done

    def __init__(self, text, engine):
        super().__init__()
        self.text = text
        self.engine = engine

    def run(self):
        self.engine.say(self.text)
        self.engine.runAndWait()
        self.finished.emit()


class OfflineTTS:
    def __init__(self):
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty("voices")
        # Explicitly set a voice (e.g., first available voice)
        if voices:
            self.engine.setProperty("voice", voices[0].id)  # Change index for a different voice
        self.engine.setProperty("rate", 160)
        self.engine.setProperty("volume", 1.0)

        self.tts_thread = None

    def speak(self, text, on_finished=None):
        """
        Speaks the given text in a non-blocking way.
        If `on_finished` is provided, it is called after the speech is complete.
        """
        if self.tts_thread and self.tts_thread.isRunning():
            self.tts_thread.terminate()  # Stop any ongoing speech safely

        self.tts_thread = TTSThread(text, self.engine)
        if on_finished:
            self.tts_thread.finished.connect(on_finished)
        self.tts_thread.start()

# workers.py
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from ollama_integration import ask_ai

class AIWorker(QObject):
    finished = pyqtSignal(str)  # Signal to emit the AI response
    error = pyqtSignal(str)     # Signal to emit error messages

    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt

    def run(self):
        try:
            response = ask_ai(self.prompt,model="ollama")
            self.finished.emit(response)
        except Exception as e:
            self.error.emit(str(e))

# main.py
import sys
import warnings
import logging
from PyQt5.QtWidgets import QApplication
from db import init_db
from stt import OfflineSTT
from tts import OfflineTTS
from ui_mainwindow import MainWindow

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to capture all logs
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# Suppress specific FutureWarning from whisper
warnings.filterwarnings("ignore", category=FutureWarning, module='whisper')

def main():
    # 1. Initialize DB
    init_db()

    # 2. Initialize STT and TTS engines
    stt_engine = OfflineSTT()    # Loads Whisper model
    tts_engine = OfflineTTS()    # pyttsx3-based TTS

    # 3. Launch PyQt Application
    app = QApplication(sys.argv)
    window = MainWindow(stt_engine, tts_engine)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import sys
import os
import logging
import importlib
import re
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QPushButton, QLabel,
    QSplitter, QTextEdit, QLineEdit, QComboBox, QDockWidget, QMessageBox, QFileDialog,
    QFrame, QGraphicsDropShadowEffect, QApplication
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QPoint, QSize, QEasingCurve, QPropertyAnimation
from PyQt5.QtGui import QFont, QIcon, QTextCursor, QColor

# AI / DB Imports (ensure these modules exist)
#from expert_mode import expert_mode_query
from course_mode import load_demo_data
from db import create_or_get_user
from workers import AIWorker
from course_data import get_class_units, build_llm_prompt, get_class_subjects
from wait_function import BackgroundWaitFunction
from tts import OfflineTTS

# Dynamic Simulation Loading Imports
import importlib.util

# Import the LEGO-style AI bot widget
from lego_ai_bot import LegoAIBotWidget

# Set up logging
logging.basicConfig(level=logging.DEBUG)


class MainWindow(QMainWindow):
    # Flow states for course/unit/topic selection
    STATE_IDLE = "idle"
    STATE_AWAIT_UNIT = "await_unit"
    STATE_AWAIT_TOPIC = "await_topic"

    def __init__(self, stt_engine, tts_engine):
        super().__init__()
        logging.debug("Initializing MainWindow...")

        # Basic window setup
        self.setWindowTitle("Offline Science Tutor")
        self.setWindowIcon(QIcon("assets/app_icon.png"))
        self.resize(1400, 900)

        # Engines for STT & TTS
        self.stt_engine = stt_engine
        self.tts_engine = tts_engine  # Instance of OfflineTTS
        self.voice_enabled = False  # Initially off

        # Theme (default light mode)
        self.dark_mode = False

        # Demo user & data
        self.user_info = create_or_get_user("DemoUser")
        self.user_id = self.user_info[0]
        load_demo_data()

        # Flow tracking for course/unit/topic selection
        self.flow_state = self.STATE_IDLE
        self.selected_subject = None
        self.selected_unit_number = None
        self.selected_topic = None
        self.available_units = {}
        self.available_topics = {}

        # Load simulation modules dynamically
        self.simulation_classes = {}
        self._load_simulations()

        # Build the main layout with a modern “web-like” appearance
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Top Bar with Logo and Options Toggle Buttons
        top_bar = self._create_top_bar()
        main_layout.addWidget(top_bar, stretch=0)

        # 2. Central Splitter: Chat Panel (left) & Simulation Panel (right)
        self.central_splitter = QSplitter(Qt.Horizontal)
        self.central_splitter.setHandleWidth(4)
        self.chat_panel = self._create_chat_panel()
        self.simulation_panel = self._create_simulation_panel()
        self.central_splitter.addWidget(self.chat_panel)
        self.central_splitter.addWidget(self.simulation_panel)
        # Initially assign all width to chat panel (simulation panel collapsed)
        self.central_splitter.setSizes([self.width(), 0])
        main_layout.addWidget(self.central_splitter, stretch=1)

        # 3. Bottom-Right Score Frame
        score_frame = self._create_score_frame()
        main_layout.addWidget(score_frame, stretch=0, alignment=Qt.AlignRight | Qt.AlignBottom)

        main_container.setLayout(main_layout)
        self.setCentralWidget(main_container)

        # 4. Course Sidebar (Dock)
        self.course_dock = self._create_course_sidebar()
        self.addDockWidget(Qt.LeftDockWidgetArea, self.course_dock)

        # 5. Global Stylesheet (start with light mode)
        self.setStyleSheet(self._global_style(light_mode=True))

        # 6. Background Wait Function for TTS visualization (applied to chat input)
        self.background_wait_function = BackgroundWaitFunction(self.question_input)

        logging.debug("MainWindow initialized.")

    def _load_simulations(self):
        """
        Dynamically load all simulation modules from the 'simulations' folder.
        Each simulation file must be named <name>_sim.py and contain a class named
        <Name>Simulation that inherits from QWidget.
        """
        simulations_path = os.path.join(os.path.dirname(__file__), "simulations")
        if not os.path.isdir(simulations_path):
            logging.error(f"Simulations directory not found: {simulations_path}")
            return

        sys.path.insert(0, simulations_path)
        for file in os.listdir(simulations_path):
            if file.endswith("_sim.py") and not file.startswith("__"):
                module_name = file[:-3]
                try:
                    module = importlib.import_module(module_name)
                    class_name = ''.join(word.capitalize() for word in module_name.split('_')[:-1]) + "Simulation"
                    sim_class = getattr(module, class_name)
                    sim_display_name = class_name.replace("Simulation", "").replace("_", " ")
                    self.simulation_classes[sim_display_name] = sim_class
                    logging.debug(f"Loaded simulation: {sim_display_name}")
                except AttributeError:
                    logging.error(f"Class {class_name} not found in module {module_name}")
                except Exception as e:
                    logging.error(f"Failed to load simulation {module_name}: {e}")
        sys.path.pop(0)

    # -------------------------
    # TTS & Messaging Handling
    # -------------------------
    def _handle_tts_speaking(self):
        self.background_wait_function.set_equalizer(True)

    def _handle_tts_finished(self):
        self.background_wait_function.set_equalizer(False)

    def _send_message(self):
        msg = self.question_input.text().strip()
        if msg:
            self._append_chat_message(msg, sender="user")
            self.question_input.clear()
            self.background_wait_function.start_waiting()
            self._process_user_message(msg)

    # -------------------------
    # A. Top Bar with Logo and Options
    # -------------------------
    
    def _create_top_bar(self):
        top_bar_widget = QWidget()
        layout = QHBoxLayout(top_bar_widget)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(20)
        top_bar_widget.setObjectName("TopBar")

        # Logo on the left
        logo = QLabel("Prof AI")
        logo.setFont(QFont("Montserrat", 26, QFont.Bold))
        logo.setStyleSheet("color: #1976D2; padding-left: 20px;")
        layout.addWidget(logo, alignment=Qt.AlignLeft)

        layout.addStretch()

        # Grouped toggle buttons on the right
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(12)

        self.btn_dark_mode = QToolButton()
        self.btn_dark_mode.setIcon(QIcon("assets/dark_mode_icon.png"))
        self.btn_dark_mode.setCheckable(True)
        self.btn_dark_mode.setCursor(Qt.PointingHandCursor)
        self.btn_dark_mode.setStyleSheet("background: transparent; border: none;")
        self.btn_dark_mode.clicked.connect(lambda: self.toggle_dark_mode(self.btn_dark_mode.isChecked()))
        btn_layout.addWidget(self.btn_dark_mode)

        self.btn_voice = QToolButton()
        self.btn_voice.setIcon(QIcon("assets/voice_icon_off.png"))  # Default icon
        self.btn_voice.setCheckable(True)
        self.btn_voice.setCursor(Qt.PointingHandCursor)
        self.btn_voice.setStyleSheet("background: transparent; border: none;")
        self.btn_voice.clicked.connect(lambda: self.toggle_voice(self.btn_voice.isChecked()))
        btn_layout.addWidget(self.btn_voice)



        self.btn_courses = QToolButton()
        self.btn_courses.setIcon(QIcon("assets/courses_icon.png"))
        self.btn_courses.setCursor(Qt.PointingHandCursor)
        self.btn_courses.setStyleSheet("background: transparent; border: none;")
        self.btn_courses.clicked.connect(self._toggle_course_dock)
        btn_layout.addWidget(self.btn_courses)

        layout.addWidget(btn_container, alignment=Qt.AlignRight)
        return top_bar_widget

    def toggle_dark_mode(self, checked):
        self.dark_mode = checked
        self.setStyleSheet(self._global_style(light_mode=not self.dark_mode))
        chat_styles = "background-color: #1E1E1E; color: #FFFFFF;" if self.dark_mode else "background-color: #FFFFFF; color: #333333;"
        self.chat_display.setStyleSheet(chat_styles)
        self.question_input.setStyleSheet(chat_styles)

    def toggle_voice(self,checked):
            if checked:  # Check if toggled
                self.btn_voice.setIcon(QIcon("assets/voice_icon_on.png"))
            else:
                self.btn_voice.setIcon(QIcon("assets/voice_icon_off.png"))
            self.btn_voice.repaint()

    def _toggle_course_dock(self):
        self.course_dock.setVisible(not self.course_dock.isVisible())

    # -------------------------
    # B. Course Sidebar (Dock) with Interactive Animations
    # -------------------------
    def _create_course_sidebar(self):
        """
        Creates a modular tile-based subject selector for courses.
        Each course tile expands with an animated class dropdown.
        """
        dock = QDockWidget("", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea)
        dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        dock.setStyleSheet("QDockWidget { background-color: transparent; }")
        title_bar = QWidget()
        title_bar.setFixedHeight(0)
        title_bar.setStyleSheet("background: transparent; border: none;")
        dock.setTitleBarWidget(title_bar)


        course_widget = QWidget()
        layout = QVBoxLayout(course_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        subjects = {
            "Physics": "assets/physics.png",
            "Chemistry": "assets/chemistry.png",
            "Biology": "assets/biology.png",
            "AI": "assets/ai.png"
        }

        for subject, icon_path in subjects.items():
            # Create a course tile button with proper objectName for styling.
            subject_button = QPushButton()
            subject_button.setObjectName("courseTile")
            subject_button.setIcon(QIcon(icon_path))
            subject_button.setIconSize(QSize(60, 60))
            subject_button.setText(subject)
            subject_button.setCursor(Qt.PointingHandCursor)
            subject_button.setCheckable(True)
            subject_button.clicked.connect(lambda checked, s=subject: self._toggle_class_dropdown(s, checked))
            layout.addWidget(subject_button)

            # Create a class selection dropdown with initial collapsed state.
            class_dropdown = QComboBox()
            class_dropdown.setObjectName("courseDropdown")
            class_dropdown.addItems([f"Class {i}" for i in range(1, 11)])
            class_dropdown.setCursor(Qt.PointingHandCursor)
            class_dropdown.currentTextChanged.connect(lambda text, s=subject: self.start_class_flow(s, int(text.split()[1])))
            class_dropdown.setVisible(False)
            class_dropdown.setMaximumHeight(0)
            layout.addWidget(class_dropdown)

            setattr(self, f"{subject}_dropdown", class_dropdown)

        course_widget.setLayout(layout)
        dock.setWidget(course_widget)
        return dock

    def _toggle_class_dropdown(self, subject, checked):
        """
        Animates the expansion or collapse of the class dropdown for a given subject.
        Also ensures that all other dropdowns are collapsed.
        """
        for subj in ["Physics", "Chemistry", "Biology", "AI"]:
            dropdown = getattr(self, f"{subj}_dropdown")
            if subj == subject:
                if checked:
                    dropdown.setVisible(True)
                    dropdown.setMaximumHeight(0)
                    targetHeight = 40  # Adjust as needed
                    anim = QPropertyAnimation(dropdown, b"maximumHeight")
                    anim.setDuration(300)
                    anim.setStartValue(0)
                    anim.setEndValue(targetHeight)
                    anim.setEasingCurve(QEasingCurve.OutQuad)
                    anim.start()
                    dropdown.anim = anim
                else:
                    currentHeight = dropdown.height()
                    anim = QPropertyAnimation(dropdown, b"maximumHeight")
                    anim.setDuration(300)
                    anim.setStartValue(currentHeight)
                    anim.setEndValue(0)
                    anim.setEasingCurve(QEasingCurve.InQuad)
                    anim.finished.connect(lambda d=dropdown: d.setVisible(False))
                    anim.start()
                    dropdown.anim = anim
            else:
                if dropdown.isVisible():
                    currentHeight = dropdown.height()
                    anim = QPropertyAnimation(dropdown, b"maximumHeight")
                    anim.setDuration(300)
                    anim.setStartValue(currentHeight)
                    anim.setEndValue(0)
                    anim.setEasingCurve(QEasingCurve.InQuad)
                    anim.finished.connect(lambda d=dropdown: d.setVisible(False))
                    anim.start()
                    dropdown.anim = anim

    def start_class_flow(self, subject: str, class_number: int):
        if self.flow_state != self.STATE_IDLE:
            self._stop_flow()
        self.flow_state = self.STATE_IDLE
        self.selected_subject = subject
        self.selected_class_number = class_number
        self.flow_state = self.STATE_AWAIT_UNIT
        self.available_units = get_class_units(class_number, subject)
        if not self.available_units:
            self._append_chat_message("No data available for this subject.", sender='ai')
            self.flow_state = self.STATE_IDLE
            return
        lines = [f"Welcome to Class {class_number} {subject}!",
                 "Here are the available units:\n"]
        for unit_num, unit_info in self.available_units.items():
            lines.append(f"{unit_num}. {unit_info['name']}")
        lines.append("Please type the unit number (e.g., 1, 2) in the chat to proceed, or 'stop' to cancel.")
        self._append_chat_message("\n".join(lines), sender='ai')

    def user_selected_unit(self, unit_number: str):
        if unit_number not in self.available_units:
            self._append_chat_message("Invalid unit number. Please try again or type 'stop'.", sender='ai')
            return
        self.selected_unit_number = unit_number
        self.flow_state = self.STATE_AWAIT_TOPIC
        self._append_chat_message(f"You selected Unit {unit_number}: {self.available_units[unit_number]['name']}", sender='user')
        self.available_topics = list(self.available_units[unit_number]['topics'].keys())
        lines = [f"Here are the topics in Unit {unit_number}:\n"]
        for i, topic_name in enumerate(self.available_topics, start=1):
            lines.append(f"{i}. {topic_name}")
        lines.append("Please type the topic number or name. Type 'stop' to cancel.")
        self._append_chat_message("\n".join(lines), sender='ai')

    def user_selected_topic(self, topic_input: str):
        try:
            topic_index = int(topic_input)
            if 1 <= topic_index <= len(self.available_topics):
                topic_name = self.available_topics[topic_index - 1]
            else:
                self._append_chat_message("Invalid topic index. Try again or 'stop'.", sender='ai')
                return
        except ValueError:
            if topic_input in self.available_topics:
                topic_name = topic_input
            else:
                self._append_chat_message("Invalid topic name. Try again or 'stop'.", sender='ai')
                return
        self.selected_topic = topic_name
        prompt = build_llm_prompt(self.selected_class_number, self.selected_subject, self.selected_unit_number, topic_name)
        self.flow_state = self.STATE_IDLE
        self._append_chat_message(f"You selected topic: {topic_name}", sender='user')
        self._append_chat_message("Sending a special prompt to the LLM now...", sender='ai')
        self._send_to_llm(prompt)

    def _stop_flow(self):
        logging.debug("Stopping flow...")
        self.flow_state = self.STATE_IDLE
        self.selected_subject = None
        self.selected_class_number = None
        self.selected_unit_number = None
        self.selected_topic = None
        self.available_units = {}
        self.available_topics = {}
        if hasattr(self, 'worker') and hasattr(self, 'worker_thread'):
            try:
                self.worker.cancel()
                if self.worker_thread.isRunning():
                    self.worker_thread.quit()
                    self.worker_thread.wait()
            except Exception as e:
                logging.debug(f"AIWorker cancellation issue: {e}")
        if self.voice_enabled and self.tts_engine.tts_thread:
            try:
                if self.tts_engine.tts_thread.isRunning():
                    self.tts_engine.tts_thread.terminate()
                    self.tts_engine.tts_thread.wait()
            except Exception as e:
                logging.debug(f"TTS termination issue: {e}")
        self.question_input.setDisabled(False)
        logging.debug("Flow stopped.")

    # -------------------------
    # C. Chat Panel with Export Chat and Bot Overlay
    # -------------------------
    def _create_chat_panel(self):
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)
        chat_layout.setContentsMargins(20, 20, 20, 20)
        chat_layout.setSpacing(15)

        # Header with Chat title and Export/Save/Load Chat buttons
        header_layout = QHBoxLayout()
        chat_title = QLabel("Chat with Prof AI")
        chat_title.setFont(QFont("Montserrat", 18, QFont.Bold))
        header_layout.addWidget(chat_title)
        header_layout.addStretch()

        # Export Chat button (already present)
        #btn_export_chat = QToolButton()
        #btn_export_chat.setText("Export Chat")
        #btn_export_chat.setCursor(Qt.PointingHandCursor)
        #btn_export_chat.clicked.connect(self._export_chat)
        #header_layout.addWidget(btn_export_chat)

        # NEW: Save Chat button
        btn_save_chat = QToolButton()
        btn_save_chat.setIcon(QIcon("assets/save_icon.png"))
        btn_save_chat.setCursor(Qt.PointingHandCursor)
        btn_save_chat.setStyleSheet("background: transparent; border: none;")
        btn_save_chat.clicked.connect(self._save_chat)
        header_layout.addWidget(btn_save_chat)

        # NEW: Load Chat button
        btn_load_chat = QToolButton()
        btn_load_chat.setIcon(QIcon("assets/load_icon.png"))
        btn_load_chat.setCursor(Qt.PointingHandCursor)
        btn_load_chat.setStyleSheet("background: transparent; border: none;")
        btn_load_chat.clicked.connect(self._load_chat)
        header_layout.addWidget(btn_load_chat)

        chat_layout.addLayout(header_layout)

        # Chat display area with modern translucent background and drop shadow
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.95);
            border: none;
            padding: 10px;
            font-family: 'Montserrat', sans-serif;
            font-size: 14px;
            color: #333333;
            border-radius: 10px;
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.chat_display.setGraphicsEffect(shadow)
        chat_layout.addWidget(self.chat_display, stretch=1)

        # Create and position the LEGO-style AI Bot widget on the chat display
        self.lego_bot = LegoAIBotWidget(self.chat_display)
        self.lego_bot.move(10, self.chat_display.height() - self.lego_bot.height() - 10)
        self.lego_bot.show()
        self.chat_display.installEventFilter(self)

        # Modern input container for the chat message and buttons
        input_container = QFrame()
        input_container.setObjectName("InputContainer")
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(10, 10, 10, 10)
        input_layout.setSpacing(10)

        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("Type your message here...")
        self.question_input.setStyleSheet("padding: 10px; border-radius: 8px; border: 1px solid #E0E0E0;")
        input_layout.addWidget(self.question_input, stretch=1)

        # Send button with a modern flat style
        btn_send = QToolButton()
        btn_send.setIcon(QIcon("assets/send_icon.png"))
        btn_send.setCursor(Qt.PointingHandCursor)
        btn_send.setStyleSheet("""
            QToolButton {
            background: transparent;
            border: none;
            padding: 0px;
            margin: 5px;
        }

        QToolButton:hover {
            background: rgba(0, 0, 0, 0.1);  /* Optional: Slight hover effect */
            border-radius: 4px;
        }

        """)
        btn_send.clicked.connect(self._on_send_clicked)
        input_layout.addWidget(btn_send)

        # Stop button with a distinct color
        self.btn_stop_flow = QToolButton()
        self.btn_stop_flow.setIcon(QIcon("assets/stop_icon.png"))
        self.btn_stop_flow.setCursor(Qt.PointingHandCursor)
        self.btn_stop_flow.setStyleSheet("""
            QToolButton {
            background: transparent;
            border: none;
            padding: 0px;
            margin: 5px;
        }

        QToolButton:hover {
            background: rgba(0, 0, 0, 0.1);  /* Optional: Slight hover effect */
            border-radius: 4px;
        }

        """)
        self.btn_stop_flow.clicked.connect(self._on_stop_flow_clicked)
        input_layout.addWidget(self.btn_stop_flow)

        chat_layout.addWidget(input_container)
        
        # Update the LEGO AI bot's state based on text changes
        self.question_input.textChanged.connect(self._on_text_changed)
        
        return chat_widget


    def _save_chat(self):
        """
        Saves the current chat text as plain text to a file chosen by the user.
        """
        filename, _ = QFileDialog.getSaveFileName(self, "Save Chat", "", "Text Files (*.txt)")
        if filename:
            try:
                # We save the plain text version of the entire chat_display.
                chat_content = self.chat_display.toPlainText()
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(chat_content)
                QMessageBox.information(self, "Save Chat", f"Chat saved to {filename}.")
            except Exception as e:
                logging.error(f"Save chat failed: {e}")
                QMessageBox.critical(self, "Save Error", f"Failed to save chat: {e}")

    def _load_chat(self):
        """
        Loads a saved chat file (plain text) and replaces the current chat content.
        """
        filename, _ = QFileDialog.getOpenFileName(self, "Load Chat", "", "Text Files (*.txt)")
        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    loaded_content = f.read()
                self.chat_display.clear()
                self.chat_display.append(loaded_content)
                QMessageBox.information(self, "Load Chat", f"Chat loaded from {filename}.")
            except Exception as e:
                logging.error(f"Load chat failed: {e}")
                QMessageBox.critical(self, "Load Error", f"Failed to load chat: {e}")


    def eventFilter(self, source, event):
        if source == self.chat_display and event.type() == event.Resize:
            self.lego_bot.move(10, self.chat_display.height() - self.lego_bot.height() - 10)
        return super().eventFilter(source, event)

    def _export_chat(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export Chat", "", "Text Files (*.txt)")
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(self.chat_display.toPlainText())
                QMessageBox.information(self, "Export Chat", f"Chat exported to {filename}.")
            except Exception as e:
                logging.error(f"Chat export failed: {e}")
                QMessageBox.critical(self, "Export Error", f"Failed to export chat: {e}")

    def _on_send_clicked(self):
        msg = self.question_input.text().strip()
        if not msg:
            return
        self._append_chat_message(msg, sender='user')
        self.question_input.clear()
        self.lego_bot.setThinking()
        if self.flow_state == self.STATE_AWAIT_UNIT and hasattr(self, 'pending_subject'):
            if msg.lower() == 'yes':
                self._stop_flow()
                self.start_class_flow(self.pending_subject, self.pending_class_number)
                delattr(self, 'pending_subject')
                delattr(self, 'pending_class_number')
            elif msg.lower() == 'no':
                delattr(self, 'pending_subject')
                delattr(self, 'pending_class_number')
            return
        if self.flow_state == self.STATE_AWAIT_UNIT:
            try:
                unit_number = int(msg)
                if 1 <= unit_number <= len(self.available_units):
                    self.user_selected_unit(str(unit_number))
                else:
                    self._append_chat_message("Invalid unit number. Try again or type 'stop'.", sender='ai')
            except ValueError:
                self._append_chat_message("Invalid input. Please enter a unit number.", sender='ai')
            return
        if self.flow_state == self.STATE_AWAIT_TOPIC:
            try:
                topic_index = int(msg)
                if 1 <= topic_index <= len(self.available_topics):
                    topic_name = self.available_topics[topic_index - 1]
                    self.user_selected_topic(topic_name)
                else:
                    self._append_chat_message("Invalid topic index. Try again or type 'stop'.", sender='ai')
            except ValueError:
                if msg in self.available_topics:
                    self.user_selected_topic(msg)
                else:
                    self._append_chat_message("Invalid topic name. Try again or type 'stop'.", sender='ai')
            return
        if self.flow_state == self.STATE_IDLE:
            self._process_user_message(msg)

    def _on_stop_flow_clicked(self):
        logging.debug("User pressed STOP.")
        self._append_chat_message("User pressed STOP. Cancelling flow...", sender='ai')
        self._stop_flow()
        self.background_wait_function.stop_waiting()

    def _on_text_changed(self, text):
        if text.strip():
            self.lego_bot.setListening()
        else:
            self.lego_bot.setIdle()

    def _append_chat_message(self, message, sender='ai'):
        """
        Improved text formatting:
        - If 'sender' == 'user', shows a normal user bubble.
        - If 'sender' == 'ai', automatically splits the text into 'Reasoning' vs 'Answer'
            by looking for the first line that starts with '*' or '#'.
        - Removes those marker characters (* or #) in the Answer portion for cleaner output.
        - Wraps Reasoning and Answer in separate bordered boxes under headings.
        """
        if sender == 'user':
            # ----- USER BUBBLE (Unchanged) -----
            bubble = (
                '<div style="display: flex; justify-content: flex-end; margin: 10px;">'
                '<div style="max-width: 75%; background-color: #DCF8C6; '
                'padding: 12px; border-radius: 16px; box-shadow: 0px 1px 3px rgba(0,0,0,0.1);">'
                '<div style="font-weight: bold; margin-bottom: 5px;">You</div>'
                f'<div style="word-wrap: break-word;">{message}</div>'
                '</div></div>'
            )
            self.chat_display.append(bubble)
            self.chat_display.moveCursor(QTextCursor.End)
            return

        # ----- AI BUBBLE -----
        # 1. Split lines
        lines = message.splitlines()

        # 2. Find index of the line that starts with '*' or '#'
        idx_answer_start = None
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('*') or stripped.startswith('#') :
                idx_answer_start = i
                break

        # 3. Separate reasoning vs. answer based on that index
        if idx_answer_start is None:
            # No marker => everything is "Answer"
            reasoning_text = ""
            answer_text = message
        else:
            reasoning_text = "\n".join(lines[:idx_answer_start])
            # For the answer portion, remove leading '*' or '#' from each line
            cleaned_answer_lines = []
            for ans_line in lines[idx_answer_start:]:
                # Remove all leading ** (or single *)
                ans_line = re.sub(r'^\**|\**$', '', ans_line).strip()  
                ans_line = re.sub(r'^#+', '', ans_line).strip()  
                cleaned_answer_lines.append(ans_line)
            answer_text = "\n".join(cleaned_answer_lines)

        # 4. Convert newlines to <br> for HTML
        reasoning_html = reasoning_text.replace("\n", "<br>").strip()
        answer_html = answer_text.replace("\n", "<br>").strip()

        # 5. Build the outer bubble (header + two sections + footer)
        bubble_top = (
            '<div style="display: flex; justify-content: flex-start; margin: 10px;">'
            '<div style="max-width: 75%; background-color: #F1F0F0; '
            'padding: 12px; border-radius: 16px; box-shadow: 0px 1px 3px rgba(0,0,0,0.1);">'
            '<div style="font-weight: bold; margin-bottom: 5px;">Prof</div>'
        )
        bubble_bottom = '</div></div>'

        # Reasoning (only if we have something)
        reasoning_section = ""
        if reasoning_html:
            reasoning_section = (
                '<div style="border: 2px dashed #ccc; border-radius: 8px; padding: 10px; margin-bottom: 8px;">'
                '<div style="font-weight: bold; margin-bottom: 5px;">Reasoning:</div>'
                f'<div style="word-wrap: break-word;">{reasoning_html}</div>'
                '</div>'
            )

        # Answer
        answer_section = (
            '<div style="border: 2px solid #ccc; border-radius: 8px; padding: 10px;">'
            '<div style="font-weight: bold; margin-bottom: 5px;">Answer:</div>'
            f'<div style="word-wrap: break-word;">{answer_html}</div>'
            '</div>'
        )

        # Combine everything
        bubble = bubble_top + reasoning_section + answer_section + bubble_bottom
        self.chat_display.append(bubble)
        self.chat_display.moveCursor(QTextCursor.End)

    def _process_user_message(self, message):
        logging.debug("Processing query with Prof...")
        self._append_chat_message("Processing...", sender='ai')
        self.question_input.setDisabled(True)
        self.lego_bot.setThinking()
        self.worker = AIWorker(message)
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._handle_ai_response)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker.error.connect(self._handle_ai_error)
        self.background_wait_function.start_waiting()
        self.worker_thread.start()

    def _handle_ai_response(self, response):
        self._append_chat_message(response, sender='ai')
        self.background_wait_function.stop_waiting()
        if self.voice_enabled:
            self.tts_engine.speak(response)
        self.lego_bot.setSpeaking()
        QTimer.singleShot(1500, self.lego_bot.setIdle)
        self.question_input.setDisabled(False)
        self._trigger_simulation(response)

    def _handle_ai_error(self, error_msg):
        self._append_chat_message(f"Error: {error_msg}", sender='ai')
        self.question_input.setDisabled(False)
        self.background_wait_function.stop_waiting()

    def _send_to_llm(self, prompt):
        self._append_chat_message("Processing specialized topic prompt...", sender='ai')
        self.question_input.setDisabled(True)
        self.thread = QThread()
        self.worker = AIWorker(prompt)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._handle_ai_response)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.error.connect(self._handle_ai_error)
        self.background_wait_function.start_waiting()
        self.thread.start()

    # -------------
    # D. Simulation Panel (Automatically Expands)
    # -------------
    def _create_simulation_panel(self):
        sim_widget = QWidget()
        layout = QVBoxLayout(sim_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        placeholder = QLabel("Simulation will appear here when relevant.")
        placeholder.setFont(QFont("Montserrat", 14))
        placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(placeholder)
        return sim_widget

    def _trigger_simulation(self, text_response):
        """
        Checks the AI response for simulation-related keywords.
        If found, automatically loads the corresponding simulation and expands the simulation panel.
        Otherwise, the simulation panel is collapsed.
        """
        txt = text_response.lower()
        simulation_map = {
            "pendulum": "Pendulum",
            "projectile": "Projectile Motion",
            "circuit": "Electric Circuit",
            "string theory": "String Theory",
            "thermodynamics": "Thermodynamics",
            "optic": "Optics (Lens)",
            "lens": "Optics (Lens)",
            "wave": "Waves (Standing Wave)",
            "gravity": "Gravity (Orbits)",
            "orbit": "Gravity (Orbits)",
            "magnetic": "Magnetic Fields"
        }
        matched = False
        sim_name = None
        for key, sname in simulation_map.items():
            if key in txt:
                matched = True
                sim_name = sname
                break
        totalWidth = self.central_splitter.width()
        if matched:
            self._select_simulation(sim_name)
            simulationWidth = 600  # Desired simulation panel width
            chatWidth = totalWidth - simulationWidth
            self.central_splitter.setSizes([chatWidth, simulationWidth])
        else:
            self.central_splitter.setSizes([totalWidth, 0])

    def _select_simulation(self, sim_name):
        layout = self.simulation_panel.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        sim_class = self.simulation_classes.get(sim_name, None)
        if sim_class:
            try:
                sim = sim_class()
            except Exception as e:
                sim = QLabel("Failed to load simulation.")
                logging.error(f"Failed to instantiate simulation {sim_name}: {e}")
        else:
            sim = QLabel("No simulation available.")
            sim.setFont(QFont("Montserrat", 14))
            sim.setAlignment(Qt.AlignCenter)
        layout.addWidget(sim)

    # -------------
    # E. Score Frame (Bottom-Right)
    # -------------
    def _create_score_frame(self):
        score_widget = QWidget()
        layout = QHBoxLayout(score_widget)
        layout.setContentsMargins(10, 5, 10, 5)
        score_label = QLabel("Score: 0")
        score_label.setFont(QFont("Montserrat", 12))
        xp_label = QLabel("XP: 0 / 1000")
        xp_label.setFont(QFont("Montserrat", 12))
        layout.addWidget(score_label)
        layout.addWidget(xp_label)
        layout.addStretch()
        return score_widget

    # -------------
    # F. Global Stylesheet (Modern Dark/Light) with Course Tile Styles
    # -------------
    def _global_style(self, light_mode=True):
        if light_mode:
            return """
            QMainWindow {
                background-color: #F9FAFB;
            }
            QWidget#TopBar {
                background-color: #FFFFFF;
                border-bottom: 1px solid #E0E0E0;
            }
            QDockWidget {
                background-color: #FFFFFF;
                border-right: 1px solid #CCCCCC;
            }
            QDockWidget::title {
                background-color: #1976D2;
                color: #FFFFFF;
                padding: 8px;
                font-weight: bold;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTextEdit {
                background-color: rgba(255, 255, 255, 0.95);
                border: none;
                padding: 10px;
                font-family: 'Montserrat', sans-serif;
                font-size: 14px;
                color: #333333;
                border-radius: 10px;
            }
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 8px;
                font-family: 'Montserrat', sans-serif;
                font-size: 14px;
                color: #333333;
            }
            QPushButton, QToolButton {
                background-color: #1976D2;
                color: #FFFFFF;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-family: 'Montserrat', sans-serif;
                font-size: 14px;
            }
            QPushButton:hover, QToolButton:hover {
                background-color: #1565C0;
            }
            QPushButton:checked, QToolButton:checked {
                background-color: #1565C0;
                border: 2px solid #0D47A1;
            }
            QComboBox {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 8px;
                font-family: 'Montserrat', sans-serif;
                font-size: 14px;
                color: #333333;
            }
            QLabel {
                font-family: 'Montserrat', sans-serif;
                font-size: 14px;
                color: #333333;
            }
            /* Course tile styles for light mode */
            QPushButton#courseTile {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
                text-align: left;
            }
            QPushButton#courseTile:hover {
                background-color: #F5F5F5;
            }
            QPushButton#courseTile:checked {
                background-color: #E3F2FD;
                border: 1px solid #1976D2;
            }
            QComboBox#courseDropdown {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 6px;
                font-size: 14px;
                color: #333333;
            }
            """
        else:
            return """
            QMainWindow {
                background-color: #2E2E2E;
            }
            QWidget#TopBar {
                background-color: #424242;
                border-bottom: 1px solid #616161;
            }
            QDockWidget {
                background-color: #424242;
                border-right: 1px solid #616161;
            }
            QDockWidget::title {
                background-color: #1976D2;
                color: #FFFFFF;
                padding: 8px;
                font-weight: bold;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTextEdit {
                background-color: rgba(30, 30, 30, 0.95);
                border: none;
                padding: 10px;
                font-family: 'Montserrat', sans-serif;
                font-size: 14px;
                color: #DDDDDD;
                border-radius: 10px;
            }
            QLineEdit {
                background-color: #424242;
                border: 1px solid #616161;
                border-radius: 8px;
                padding: 8px;
                font-family: 'Montserrat', sans-serif;
                font-size: 14px;
                color: #DDDDDD;
            }
            QPushButton, QToolButton {
                background-color: #1976D2;
                color: #FFFFFF;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-family: 'Montserrat', sans-serif;
                font-size: 14px;
            }
            QPushButton:hover, QToolButton:hover {
                background-color: #1565C0;
            }
            QPushButton:checked, QToolButton:checked {
                background-color: #1565C0;
                border: 2px solid #0D47A1;
            }
            QComboBox {
                background-color: #424242;
                border: 1px solid #616161;
                border-radius: 8px;
                padding: 8px;
                font-family: 'Montserrat', sans-serif;
                font-size: 14px;
                color: #DDDDDD;
            }
            QLabel {
                font-family: 'Montserrat', sans-serif;
                font-size: 14px;
                color: #FFFFFF;
            }
            /* Course tile styles for dark mode */
            QPushButton#courseTile {
                background-color: #333333;
                border: 1px solid #616161;
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
                text-align: left;
                color: #FFFFFF;
            }
            QPushButton#courseTile:hover {
                background-color: #444444;
            }
            QPushButton#courseTile:checked {
                background-color: #1E88E5;
                border: 1px solid #1565C0;
            }
            QComboBox#courseDropdown {
                background-color: #333333;
                border: 1px solid #616161;
                border-radius: 4px;
                padding: 6px;
                font-size: 14px;
                color: #FFFFFF;
            }
            """

# Standalone Test
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # Placeholder STT and TTS engines (replace with actual implementations)
    stt_engine = None
    tts_engine = OfflineTTS()

    app = QApplication(sys.argv)
    window = MainWindow(stt_engine, tts_engine)
    window.show()
    sys.exit(app.exec_())

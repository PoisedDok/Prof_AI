#!/usr/bin/env python3
import sys
import logging
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QMenu,
    QPushButton, QLabel, QSplitter, QTextEdit, QLineEdit, QComboBox,
    QDockWidget, QTreeWidget, QTreeWidgetItem, QAction
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QTextCursor

# Simulation Widgets (replace with actual or placeholders)
from simulation import (
    PendulumWidget, ProjectileMotionWidget, ElectricCircuitWidget, 
    StringTheoryWidget, ThermodynamicsWidget, OpticsWidget, 
    WaveWidget, GravityWidget, MagneticFieldWidget
)

# AI / DB
from expert_mode import expert_mode_query
from course_mode import load_demo_data
from db import create_or_get_user
from workers import AIWorker
from course_data import get_class_units, build_llm_prompt,get_class_subjects
from wait_function import BackgroundWaitFunction
from tts import *

class MainWindow(QMainWindow):
    # States for the guided flow
    STATE_IDLE = "idle"
    STATE_AWAIT_UNIT = "await_unit"    # user must pick a unit number
    STATE_AWAIT_TOPIC = "await_topic"  # user must pick a topic

    def __init__(self, stt_engine, tts_engine):
        super().__init__()
        logging.debug("Initializing MainWindow...")

        # Basic window setup
        self.setWindowTitle("Offline Science Tutor")
        self.setWindowIcon(QIcon("assets/app_icon.png"))
        self.resize(1200, 800)

        # Engines for speech & AI
        self.stt_engine = stt_engine
        self.tts_engine = tts_engine
        self.voice_enabled = False  # Initially voice is off

        # Dark / Light
        self.dark_mode = False

        # Demo user & data
        self.user_info = create_or_get_user("DemoUser")
        self.user_id = self.user_info[0]
        load_demo_data()

        # Flow tracking
        self.flow_state = self.STATE_IDLE
        self.selected_subject = None
        self.selected_unit_number = None
        self.selected_topic = None

        # Keep a reference to the subject's units
        self.available_units = {}
        self.available_topics = []

        # Layout setup
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Top bar (3-dot menu)
        top_bar = self._create_top_bar()
        main_layout.addWidget(top_bar, stretch=0)

        # 2. Central: Chat (left) & Simulation (right)
        self.central_splitter = QSplitter(Qt.Horizontal)
        self.central_splitter.addWidget(self._create_chat_panel())
        self.central_splitter.addWidget(self._create_simulation_panel())
        self.central_splitter.setSizes([600, 600])
        main_layout.addWidget(self.central_splitter, stretch=1)

        # 3. Bottom-right Score
        score_frame = self._create_score_frame()
        main_layout.addWidget(score_frame, stretch=0, alignment=Qt.AlignRight | Qt.AlignBottom)

        main_container.setLayout(main_layout)
        self.setCentralWidget(main_container)

        # Collapsible course dock
        self.course_dock = self._create_course_sidebar()
        self.addDockWidget(Qt.LeftDockWidgetArea, self.course_dock)

        # Apply stylesheet
        self.setStyleSheet(self._global_style(light_mode=True))

        # Background wait function for TTS visualization
        self.background_wait_function = BackgroundWaitFunction(self.question_input)

        logging.debug("MainWindow initialized.")

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

    def _process_user_message(self, message):
        # Process the user's message and handle AI response
        response = "Processing message..."  # Placeholder
        self._append_chat_message(response, sender="ai")

        # Use TTS to speak the response
        self.tts_engine.speak(
            response,
            on_speaking=self._handle_tts_speaking,
            on_finished=self._handle_tts_finished,
        )

    # -------------------------------------------------------------------------
    # A. Top Bar
    # -------------------------------------------------------------------------
    def _create_top_bar(self):
        top_bar_widget = QWidget()
        layout = QHBoxLayout(top_bar_widget)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        menu_button = QToolButton()
        menu_button.setText("⋮")
        menu_button.setPopupMode(QToolButton.InstantPopup)

        main_menu = QMenu()

        self.dark_mode_action = QAction("Dark Mode", self, checkable=True)
        self.dark_mode_action.setChecked(False)
        self.dark_mode_action.triggered.connect(self.toggle_dark_mode)
        main_menu.addAction(self.dark_mode_action)

        self.voice_toggle_action = QAction("Voice Input", self, checkable=True)
        self.voice_toggle_action.setChecked(False)
        self.voice_toggle_action.triggered.connect(self.toggle_voice)
        main_menu.addAction(self.voice_toggle_action)

        self.course_toggle_action = QAction("Course", self)
        self.course_toggle_action.triggered.connect(self._toggle_course_dock)
        main_menu.addAction(self.course_toggle_action)

        menu_button.setMenu(main_menu)
        layout.addWidget(menu_button, alignment=Qt.AlignLeft)
        layout.addStretch()

        return top_bar_widget

    def toggle_dark_mode(self, checked):
        """
        Toggles between dark and light mode and applies styles dynamically.
        """
        self.dark_mode = checked
        dark_mode_styles = self._global_style(light_mode=not self.dark_mode)

        # Apply styles
        self.setStyleSheet(dark_mode_styles)

        # Update individual widget styles
        chat_styles = (
            "background-color: #1E1E1E; color: #FFFFFF;"
            if self.dark_mode
            else "background-color: #FFFFFF; color: #000000;"
        )
        self.chat_display.setStyleSheet(chat_styles)
        self.question_input.setStyleSheet(chat_styles)

        # Update course tree widget
        course_styles = (
            "background-color: #1E1E1E; color: #FFFFFF;"
            if self.dark_mode
            else "background-color: #FFFFFF; color: #000000;"
        )
        self.course_tree.setStyleSheet(course_styles)

    def toggle_voice(self, checked):
        self.voice_enabled = checked

    def _toggle_course_dock(self):
        is_visible = self.course_dock.isVisible()
        self.course_dock.setVisible(not is_visible)

    # -------------------------------------------------------------------------
    # B. Course Sidebar (Dock)
    # -------------------------------------------------------------------------
    def _create_course_sidebar(self):
        dock = QDockWidget("Courses", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable)

        self.course_tree = QTreeWidget()
        self.course_tree.setHeaderHidden(True)
        self.course_tree.itemClicked.connect(self._on_course_item_clicked)

        # Classes 1..10
        for grade in range(1, 11):
            grade_item = QTreeWidgetItem(self.course_tree)
            grade_item.setText(0, f"Class {grade}")
            # For demonstration, same 4 subjects
            for subject in ["Physics", "Chemistry", "Biology", "AI"]:
                sub_item = QTreeWidgetItem(grade_item)
                sub_item.setText(0, subject)

        dock.setWidget(self.course_tree)
        return dock

    def _on_course_item_clicked(self, item, column):
        logging.debug("Course item clicked: _on_course_item_clicked method entered")
        parent = item.parent()
        if parent and "Class" in parent.text(0):
            logging.debug("Parent item is a class item")
            grade_text = parent.text(0)  # e.g., 'Class 10'
            subject_text = item.text(0)  # e.g., 'Physics'

            logging.debug(f"Course item clicked: {grade_text} -> {subject_text}")
            try:
                class_number = int(grade_text.split(" ")[1])
            except (IndexError, ValueError):
                logging.error("Invalid class number format")
                return

            # Check if a course selection is already in progress
            if self.flow_state == self.STATE_AWAIT_UNIT:
                logging.debug("Course selection already in progress")

                # If trying to select the same course, do nothing
                if (self.selected_subject == subject_text and 
                    self.selected_class_number == class_number):
                    logging.debug("Same course selected, ignoring")
                    return

                # Prompt user about switching courses
                switch_message = (
                    f"You are currently selecting units for Class {self.selected_class_number} {self.selected_subject}. "
                    f"Do you want to switch to Class {class_number} {subject_text}?\n"
                    "Type 'yes' to switch or 'no' to continue with the current course."
                )
                self._append_chat_message(switch_message, sender='ai')

                # Store the new course details for potential switch
                self.pending_subject = subject_text
                self.pending_class_number = class_number

                return

            # If flow state is idle, start a new course flow
            logging.debug("Flow state is idle, proceeding with new flow")
            self.start_class_flow(subject_text, class_number)

        elif "Class" in item.text(0):
            logging.debug("Clicked on class item directly, doing nothing")
            pass

    # Course Flow Methods
    # -------------------------------------------------------------------------
    def start_class_flow(self, subject: str, class_number: int):
        """
        1) Sets subject
        2) Shows welcome & list of units in one go
        3) Sets flow_state to 'await_unit'
        """
        if self.flow_state != self.STATE_IDLE:
            self._stop_flow()  # Stop any existing flow

        # Reset flow state to idle before starting a new flow
        self.flow_state = self.STATE_IDLE

        self.selected_subject = subject
        self.selected_class_number = class_number
        self.flow_state = self.STATE_AWAIT_UNIT

        # Retrieve units
        self.available_units = get_class_units(class_number, subject)
        if not self.available_units:
            self._append_chat_message("No data available for this subject.", sender='ai')
            self.flow_state = self.STATE_IDLE
            return

        # Build a text listing all the units
        lines = [f"Welcome to Class {class_number} {subject}!",
                "Here are the available units:\n"]
        for unit_num, unit_info in self.available_units.items():
            lines.append(f"{unit_num}. {unit_info['name']}")
        lines.append("Please type the *unit number* (e.g. 1, 2) in the chat to proceed, or 'stop' to cancel.")
        message = "\n".join(lines)
        self._append_chat_message(message, sender='ai')
        
        
    def user_selected_unit(self, unit_number: str):
        """
        Called when user typed the unit number in chat while in STATE_AWAIT_UNIT.
        """
        if unit_number not in self.available_units:
            self._append_chat_message("Invalid unit number. Please try again or type 'stop' to cancel.", sender='ai')
            return

        self.selected_unit_number = unit_number
        self.flow_state = self.STATE_AWAIT_TOPIC
        self._append_chat_message(f"You selected Unit {unit_number}: {self.available_units[unit_number]['name']}", sender='user')

        # Prepare list of topics
        self.available_topics = list(self.available_units[unit_number]['topics'].keys())
        lines = [f"Here are the topics in Unit {unit_number}:\n"]
        for i, topic_name in enumerate(self.available_topics, start=1):
            lines.append(f"{i}. {topic_name}")
        lines.append("Please type the topic number or name. Type 'stop' to cancel.")
        self._append_chat_message("\n".join(lines), sender='ai')

    def user_selected_topic(self, topic_input: str):
        """
        Called when user typed a topic name or index in chat while in STATE_AWAIT_TOPIC.
        """
        # Check if they typed an integer index
        try:
            idx = int(topic_input)
            if 1 <= idx <= len(self.available_topics):
                topic_name = self.available_topics[idx - 1]
            else:
                self._append_chat_message("Invalid topic index. Try again or 'stop'.", sender='ai')
                return
        except ValueError:
            # They typed a name, check if it's in available_topics
            if topic_input in self.available_topics:
                topic_name = topic_input
            else:
                self._append_chat_message("Invalid topic name. Try again or 'stop'.", sender='ai')
                return

        self.selected_topic = topic_name
        # Construct a prompt to the LLM
        prompt = build_llm_prompt(self.selected_class_number, self.selected_subject, self.selected_unit_number, topic_name)
        self.flow_state = self.STATE_IDLE  # or 'topic_talking', depending on how you want to manage further interactions

        self._append_chat_message(f"You selected topic: {topic_name}", sender='user')
        self._append_chat_message("Sending a special prompt to the LLM now...", sender='ai')

        # Start the LLM conversation with the constructed prompt
        self._send_to_llm(prompt)


    def _stop_flow(self):
        """
        Completely resets the current flow state and cancels any ongoing processing.
        """
        logging.debug("Stopping all ongoing processes...")

        # 1. Cancel flow state
        self.flow_state = self.STATE_IDLE
        self.selected_subject = None
        self.selected_unit_number = None
        self.selected_topic = None
        self.available_units = {}
        self.available_topics = []

        # 2. Cancel AIWorker safely
        if hasattr(self, 'worker'):
            try:
                logging.debug("Cancelling AIWorker...")
                self.worker.cancel()  # Set cancellation flag
                if self.worker_thread.isRunning():
                    self.worker_thread.quit()
                    self.worker_thread.wait()
            except Exception as e:
                logging.debug(f"AIWorker cancellation issue: {e}")

        # 3. Stop TTS playback safely
        if self.voice_enabled and self.tts_engine.tts_thread:
            try:
                if self.tts_engine.tts_thread.isRunning():
                    logging.debug("Stopping TTS playback...")
                    self.tts_engine.tts_thread.terminate()
                    self.tts_engine.tts_thread.wait()
            except Exception as e:
                logging.debug(f"TTS playback termination issue: {e}")

        # 4. Re-enable chat input
        logging.debug("Re-enabling chat input...")
        self.question_input.setDisabled(False)

        logging.debug("All processes stopped.")



    # -------------------------------------------------------------------------
    # C. Chat Panel
    # -------------------------------------------------------------------------
    def _create_chat_panel(self):
        chat_widget = QWidget()
        layout = QVBoxLayout(chat_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display, stretch=1)

        # Input row
        input_row = QHBoxLayout()

        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("Type here...")
        input_row.addWidget(self.question_input)

        btn_send = QPushButton("Send")
        btn_send.clicked.connect(self._on_send_clicked)
        input_row.addWidget(btn_send)

        # Stop button
        self.btn_stop_flow = QPushButton("Stop")
        self.btn_stop_flow.setStyleSheet("background-color: red; color: white;")
        self.btn_stop_flow.clicked.connect(self._on_stop_flow_clicked)
        input_row.addWidget(self.btn_stop_flow)

        layout.addLayout(input_row)
        return chat_widget

    def _on_send_clicked(self):
        msg = self.question_input.text().strip()
        if not msg:
            return
        self._append_chat_message(msg, sender='user')
        self.question_input.clear()

        # Special handling for course switch
        if self.flow_state == self.STATE_AWAIT_UNIT and hasattr(self, 'pending_subject'):
            if msg.lower() == 'yes':
                # User wants to switch courses
                self._stop_flow()
                self.start_class_flow(self.pending_subject, self.pending_class_number)
                delattr(self, 'pending_subject')
                delattr(self, 'pending_class_number')
            elif msg.lower() == 'no':
                # User wants to continue with current course
                delattr(self, 'pending_subject')
                delattr(self, 'pending_class_number')
            return

        # Check if user's message is a unit number
        if self.flow_state == self.STATE_AWAIT_UNIT:
            try:
                unit_number = int(msg)
                if 1 <= unit_number <= len(self.available_units):
                    self.user_selected_unit(str(unit_number))
                else:
                    self._append_chat_message("Invalid unit number. Please try again or 'stop'.", sender='ai')
            except ValueError:
                self._append_chat_message("Invalid input. Please enter a unit number.", sender='ai')
            return

        # Check if user's message is a topic number or name
        if self.flow_state == self.STATE_AWAIT_TOPIC:
            try:
                topic_index = int(msg)
                if 1 <= topic_index <= len(self.available_topics):
                    topic_name = self.available_topics[topic_index - 1]
                    self.user_selected_topic(topic_name)
                else:
                    self._append_chat_message("Invalid topic index. Try again or 'stop'.", sender='ai')
            except ValueError:
                if msg in self.available_topics:
                    self.user_selected_topic(msg)
                else:
                    self._append_chat_message("Invalid topic name. Try again or 'stop'.", sender='ai')
            return

        # If not in any specific flow state, process as a normal chat message
        if self.flow_state == self.STATE_IDLE:
            self._process_user_message(msg)

    def _on_stop_flow_clicked(self):
        """
        Handles the STOP button click event to cancel the current flow.
        """
        logging.debug("User pressed the STOP button.")
        self._append_chat_message("User pressed the STOP button. Cancelling flow...", sender='ai')
        self._stop_flow()
        self.background_wait_function.stop_waiting()

    def _append_chat_message(self, message, sender='ai'):
        """
        Appends a message in the chat window.
        Formats AI responses for better readability.
        """
        if sender == 'user':
            bubble = f"<div style='text-align: right; margin: 5px;'><b>You:</b> {message}</div>"
        else:
            # Format AI responses for readability
            formatted_message = message.replace("\n", "<br>")  # Convert newlines to HTML breaks
            bubble = (
                f"<div style='text-align: left; margin: 5px;'><b>AI:</b><br>"
                f"<p style='line-height: 1.6;'>{formatted_message}</p></div>"
            )

        self.chat_display.append(bubble)
        self.chat_display.moveCursor(QTextCursor.End)

    def _process_user_message(self, message):
        """
        Processes the user's message by sending it to the AIWorker.
        """
        logging.debug("Processing user message with AIWorker...")
        self._append_chat_message("Processing...", sender='ai')
        self.question_input.setDisabled(True)

        # Create and run AIWorker
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
        """
        Handles AI's response after processing the user's message.
        """
        self._append_chat_message(response, sender='ai')
        self.background_wait_function.stop_waiting() 

        # Speak out loud if voice is enabled
        if self.voice_enabled:
            self.tts_engine.speak(response)

        self.question_input.setDisabled(False)
        self.background_wait_function.stop_waiting()

        # Check if we want to trigger simulations
        self._trigger_simulation(response)


    def _handle_ai_error(self, error_msg):
        self._append_chat_message(f"Error: {error_msg}", sender='ai')
        self.question_input.setDisabled(False)
        self.background_wait_function.stop_waiting()

    def _send_to_llm(self, prompt):
        """
        Sends a pre-constructed prompt to the LLM, similar to normal chat logic,
        but we skip the user input step.
        """
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

    # -------------------------------------------------------------------------
    # D. Simulation Panel
    # -------------------------------------------------------------------------
    def _create_simulation_panel(self):
        sim_widget = QWidget()
        layout = QVBoxLayout(sim_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        top_row = QHBoxLayout()
        label = QLabel("Simulation Game:")
        self.simulation_selector = QComboBox()
        self.simulation_selector.addItems([
            "Pendulum",
            "Projectile Motion",
            "Electric Circuit",
            "String Theory",
            "Thermodynamics",
            "Optics (Lens)",
            "Waves (Standing Wave)",
            "Gravity (Orbits)",
            "Magnetic Fields"
        ])
        self.simulation_selector.currentTextChanged.connect(self._select_simulation)
        top_row.addWidget(label)
        top_row.addWidget(self.simulation_selector)
        layout.addLayout(top_row)

        self.simulation_display = QWidget()
        self.simulation_display.setLayout(QVBoxLayout())
        placeholder = QLabel("Game-like interactive simulation shown here.")
        placeholder.setFont(QFont("Arial", 14))
        placeholder.setAlignment(Qt.AlignCenter)
        self.simulation_display.layout().addWidget(placeholder)
        layout.addWidget(self.simulation_display)

        return sim_widget

    def _trigger_simulation(self, text_response):
        txt = text_response.lower()
        self.background_wait_function.stop_waiting()
        if "pendulum" in txt:
            self.simulation_selector.setCurrentText("Pendulum")
        elif "projectile" in txt:
            self.simulation_selector.setCurrentText("Projectile Motion")
        elif "circuit" in txt:
            self.simulation_selector.setCurrentText("Electric Circuit")
        elif "string theory" in txt:
            self.simulation_selector.setCurrentText("String Theory")
        elif "thermodynamics" in txt:
            self.simulation_selector.setCurrentText("Thermodynamics")
        elif "optic" in txt or "lens" in txt:
            self.simulation_selector.setCurrentText("Optics (Lens)")
        elif "wave" in txt:
            self.simulation_selector.setCurrentText("Waves (Standing Wave)")
        elif "gravity" in txt or "orbit" in txt:
            self.simulation_selector.setCurrentText("Gravity (Orbits)")
        elif "magnetic" in txt:
            self.simulation_selector.setCurrentText("Magnetic Fields")

    def _select_simulation(self, sim_name):
        layout = self.simulation_display.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if sim_name == "Pendulum":
            sim = PendulumWidget()
        elif sim_name == "Projectile Motion":
            sim = ProjectileMotionWidget()
        elif sim_name == "Electric Circuit":
            sim = ElectricCircuitWidget()
        elif sim_name == "String Theory":
            sim = StringTheoryWidget()
        elif sim_name == "Thermodynamics":
            sim = ThermodynamicsWidget()
        elif sim_name == "Optics (Lens)":
            sim = OpticsWidget()
        elif sim_name == "Waves (Standing Wave)":
            sim = WaveWidget()
        elif sim_name == "Gravity (Orbits)":
            sim = GravityWidget()
        elif sim_name == "Magnetic Fields":
            sim = MagneticFieldWidget()
        else:
            sim = QLabel("No simulation available.")
            sim.setFont(QFont("Arial", 14))
            sim.setAlignment(Qt.AlignCenter)

        layout.addWidget(sim)

    # -------------------------------------------------------------------------
    # E. Score Frame (Bottom-Right)
    # -------------------------------------------------------------------------
    def _create_score_frame(self):
        score_widget = QWidget()
        layout = QHBoxLayout(score_widget)
        score_label = QLabel("Score: 0")
        score_label.setFont(QFont("Arial", 12))
        xp_label = QLabel("XP: 0 / 1000")
        xp_label.setFont(QFont("Arial", 12))
        layout.addWidget(score_label)
        layout.addWidget(xp_label)
        return score_widget

    # -------------------------------------------------------------------------
    # F. StyleSheets (Dark/Light)
    # -------------------------------------------------------------------------
    def _global_style(self, light_mode=True):
        """
        Applies a global stylesheet based on the light_mode flag.
        """
        if light_mode:
            return """
            QMainWindow {
                background-color: #F9FAFB;
            }
            #TopBar {
                background-color: #FFFFFF;
                border-bottom: 1px solid #E0E0E0;
            }
            QDockWidget {
                background-color: #FFFFFF;
                border-right: 1px solid #CCCCCC;
            }
            QDockWidget::title {
                background-color: #0078D7;
                color: #FFFFFF;
                padding: 5px;
                font-weight: bold;
            }
            QTextEdit {
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px;
                color: #000000;
            }
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px;
                color: #000000;
            }
            QPushButton {
                border: none;
                background-color: #0078D7;
                color: #FFFFFF;
                padding: 6px 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
            QComboBox {
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                color: #000000;
            }
            QTreeWidget {
                background-color: #FFFFFF;
                color: #000000;
            }
            QLabel {
                color: #000000;
            }
            """
        else:
            return """
            QMainWindow {
                background-color: #2E2E2E;
            }
            #TopBar {
                background-color: #3A3A3A;
                border-bottom: 1px solid #5A5A5A;
            }
            QDockWidget {
                background-color: #3A3A3A;
                border-right: 1px solid #5A5A5A;
            }
            QDockWidget::title {
                background-color: #333333;
                color: #FFFFFF;
                padding: 5px;
                font-weight: bold;
            }
            QTextEdit {
                background-color: #1E1E1E;
                border: 1px solid #5A5A5A;
                border-radius: 5px;
                padding: 5px;
                color: #FFFFFF;
            }
            QLineEdit {
                background-color: #1E1E1E;
                border: 1px solid #5A5A5A;
                border-radius: 5px;
                padding: 5px;
                color: #FFFFFF;
            }
            QPushButton {
                border: none;
                background-color: #0078D7;
                color: #FFFFFF;
                padding: 6px 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
            QComboBox {
                background-color: #1E1E1E;
                border: 1px solid #5A5A5A;
                border-radius: 5px;
                color: #FFFFFF;
            }
            QTreeWidget {
                background-color: #1E1E1E;
                color: #FFFFFF;
            }
            QLabel {
                color: #FFFFFF;
            }
            """


# Standalone test
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    logging.basicConfig(level=logging.DEBUG)

    app = QApplication(sys.argv)
    window = MainWindow(None, None)
    window.show()
    sys.exit(app.exec_())

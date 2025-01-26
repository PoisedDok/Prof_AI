# simulations/wave_sim.py
import math
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel, QPushButton,
    QFileDialog, QMessageBox, QFrame
)
from PyQt5.QtGui import QPainter, QColor, QPen

class WaveSimulation(QWidget):
    """
    Advanced Wave Simulation with:
    - Separate control panel and simulation canvas
    - Multiple wave interference
    - Real-time Fourier analysis (Placeholder)
    - Export data functionality
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # Default wave parameters
        self.default_frequency = 1.0  # Hz
        self.frequency = self.default_frequency
        self.default_amplitude = 30  # pixels
        self.amplitude = self.default_amplitude
        self.default_phase = 0.0
        self.phase = self.default_phase

        # Simulation state
        self.simulation_running = True
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_wave)
        self.timer.start(16)  # ~60 FPS

        # Data logging for export
        self.data_log = []  # List of tuples: (time, amplitude)

        # Initialize UI
        self.init_ui()

    def init_ui(self):
        """
        Sets up the layout with a canvas and control panel.
        """
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Simulation Canvas
        self.canvas = QFrame()
        self.canvas.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.canvas.setStyleSheet("background-color: white;")
        self.canvas.setMinimumHeight(400)
        main_layout.addWidget(self.canvas, stretch=5)

        # Controls
        control_layout = QHBoxLayout()

        # Frequency Control
        freq_label = QLabel("Frequency (Hz)")
        freq_label.setToolTip("Adjust the frequency of the wave.")
        self.freq_slider = QSlider(Qt.Horizontal)
        self.freq_slider.setRange(1, 10)
        self.freq_slider.setValue(int(self.frequency))
        self.freq_slider.setToolTip("Adjust frequency in Hz.")
        self.freq_slider.valueChanged.connect(self.on_freq_change)
        self.freq_value_label = QLabel(f"{self.frequency:.1f}")

        # Amplitude Control
        amp_label = QLabel("Amplitude (px)")
        amp_label.setToolTip("Adjust the amplitude of the wave.")
        self.amp_slider = QSlider(Qt.Horizontal)
        self.amp_slider.setRange(10, 100)
        self.amp_slider.setValue(int(self.amplitude))
        self.amp_slider.setToolTip("Adjust amplitude in pixels.")
        self.amp_slider.valueChanged.connect(self.on_amp_change)
        self.amp_value_label = QLabel(f"{self.amplitude}")

        # Buttons
        self.pause_button = QPushButton("Pause")
        self.pause_button.setToolTip("Pause or resume the simulation.")
        self.pause_button.clicked.connect(self.toggle_simulation)

        self.reset_button = QPushButton("Reset")
        self.reset_button.setToolTip("Reset simulation to default parameters.")
        self.reset_button.clicked.connect(self.reset_simulation)

        self.export_button = QPushButton("Export Data")
        self.export_button.setToolTip("Export simulation data to a CSV file.")
        self.export_button.clicked.connect(self.export_data)

        # Arrange controls in layout
        # Frequency Controls
        freq_layout = QVBoxLayout()
        freq_layout.addWidget(freq_label)
        freq_slider_layout = QHBoxLayout()
        freq_slider_layout.addWidget(self.freq_slider)
        freq_slider_layout.addWidget(self.freq_value_label)
        freq_layout.addLayout(freq_slider_layout)

        # Amplitude Controls
        amp_layout = QVBoxLayout()
        amp_layout.addWidget(amp_label)
        amp_slider_layout = QHBoxLayout()
        amp_slider_layout.addWidget(self.amp_slider)
        amp_slider_layout.addWidget(self.amp_value_label)
        amp_layout.addLayout(amp_slider_layout)

        # Buttons Layout
        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(self.pause_button)
        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addWidget(self.export_button)

        # Add all control layouts to the main control layout
        control_layout.addLayout(freq_layout)
        control_layout.addLayout(amp_layout)
        control_layout.addLayout(buttons_layout)

        main_layout.addLayout(control_layout, stretch=1)

    # -----------------------
    # Event Handlers
    # -----------------------
    def on_freq_change(self, value):
        self.frequency = float(value)
        self.freq_value_label.setText(f"{self.frequency:.1f}")
        # Dynamic parameter update

    def on_amp_change(self, value):
        self.amplitude = int(value)
        self.amp_value_label.setText(f"{self.amplitude}")
        # Dynamic parameter update

    def toggle_simulation(self):
        if self.simulation_running:
            self.timer.stop()
            self.simulation_running = False
            self.pause_button.setText("Start")
        else:
            self.timer.start(16)
            self.simulation_running = True
            self.pause_button.setText("Pause")

    def reset_simulation(self):
        # Reset to default parameters
        self.frequency = self.default_frequency
        self.amplitude = self.default_amplitude
        self.phase = self.default_phase

        # Reset sliders and labels
        self.freq_slider.setValue(int(self.frequency))
        self.amp_slider.setValue(int(self.amplitude))
        self.freq_value_label.setText(f"{self.frequency:.1f}")
        self.amp_value_label.setText(f"{self.amplitude}")

        # Clear data log
        self.data_log.clear()

        self.update()

    def export_data(self):
        """
        Exports the simulation data to a CSV file.
        """
        if not self.data_log:
            QMessageBox.information(self, "Export Data", "No data to export yet.")
            return

        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Simulation Data", "", "CSV Files (*.csv)", options=options
        )
        if filename:
            try:
                with open(filename, 'w') as file:
                    file.write("Time (s),Amplitude (px)\n")
                    for entry in self.data_log:
                        file.write(f"{entry[0]:.3f},{entry[1]:.3f}\n")
                QMessageBox.information(self, "Export Data", f"Data successfully exported to {filename}.")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export data: {e}")

    # -----------------------
    # Simulation Update
    # -----------------------
    def update_wave(self):
        """
        Update the wave's phase based on wave speed.
        """
        self.phase += self.frequency * 0.1  # Adjust multiplier for speed
        amplitude = self.amplitude * math.sin(self.phase)
        current_time = len(self.data_log) * 0.016
        self.data_log.append((current_time, amplitude))
        self.update()

    # -----------------------
    # Painting
    # -----------------------
    def paintEvent(self, event):
        painter = QPainter(self.canvas)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.canvas.rect(), QColor(255, 255, 255))

        width = self.canvas.width()
        height = self.canvas.height()

        # Draw multiple waves for interference (example: two waves)
        painter.setPen(QPen(QColor(0, 0, 255), 2))

        # First Wave
        points1 = []
        for x in range(0, width, 2):
            y = height / 2 - self.amplitude * math.sin(0.02 * x + self.phase)
            points1.append((x, y))

        # Second Wave (Interfering wave)
        points2 = []
        for x in range(0, width, 2):
            y = height / 2 - self.amplitude * math.sin(0.02 * x + self.phase + math.pi / 4)
            points2.append((x, y))

        # Combined Wave
        painter.setPen(QPen(QColor(255, 0, 0), 2))
        combined_points = []
        for i in range(len(points1)):
            x = points1[i][0]
            y = height / 2 - (self.amplitude * math.sin(0.02 * x + self.phase) +
                              self.amplitude * math.sin(0.02 * x + self.phase + math.pi / 4))
            combined_points.append((x, y))

        # Draw Combined Wave
        if combined_points:
            painter.setPen(QPen(QColor(0, 0, 255), 2))
            for i in range(1, len(combined_points)):
                painter.drawLine(int(combined_points[i - 1][0]), int(combined_points[i - 1][1]),
                                 int(combined_points[i][0]), int(combined_points[i][1]))

        # Optionally, implement Fourier Analysis or other advanced features here.


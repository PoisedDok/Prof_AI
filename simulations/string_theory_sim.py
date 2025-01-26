# simulations/string_theory_sim.py
import math
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel, QPushButton,
    QFileDialog, QMessageBox, QFrame
)
from PyQt5.QtGui import QPainter, QColor, QPen

class StringTheorySimulation(QWidget):
    """
    Advanced String Theory Simulation with:
    - Separate control panel and simulation canvas
    - Multiple wave interference
    - Dynamic parameter updates
    - Export data functionality
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # Default string parameters
        self.default_tension = 5.0
        self.tension = self.default_tension
        self.default_wave_speed = 2.0
        self.wave_speed = self.default_wave_speed

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

        # Tension Control
        tension_label = QLabel("Tension")
        tension_label.setToolTip("Adjust the string tension.")
        self.tension_slider = QSlider(Qt.Horizontal)
        self.tension_slider.setRange(1, 20)
        self.tension_slider.setValue(int(self.tension))
        self.tension_slider.setToolTip("Adjust string tension.")
        self.tension_slider.valueChanged.connect(self.on_tension_change)
        self.tension_value_label = QLabel(f"{self.tension:.1f}")

        # Wave Speed Control
        wave_speed_label = QLabel("Wave Speed")
        wave_speed_label.setToolTip("Adjust the speed of the wave.")
        self.wave_speed_slider = QSlider(Qt.Horizontal)
        self.wave_speed_slider.setRange(1, 10)
        self.wave_speed_slider.setValue(int(self.wave_speed))
        self.wave_speed_slider.setToolTip("Adjust wave speed.")
        self.wave_speed_slider.valueChanged.connect(self.on_wave_speed_change)
        self.wave_speed_value_label = QLabel(f"{self.wave_speed:.1f}")

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
        # Tension Controls
        tension_layout = QVBoxLayout()
        tension_layout.addWidget(tension_label)
        tension_slider_layout = QHBoxLayout()
        tension_slider_layout.addWidget(self.tension_slider)
        tension_slider_layout.addWidget(self.tension_value_label)
        tension_layout.addLayout(tension_slider_layout)

        # Wave Speed Controls
        wave_speed_layout = QVBoxLayout()
        wave_speed_layout.addWidget(wave_speed_label)
        wave_speed_slider_layout = QHBoxLayout()
        wave_speed_slider_layout.addWidget(self.wave_speed_slider)
        wave_speed_slider_layout.addWidget(self.wave_speed_value_label)
        wave_speed_layout.addLayout(wave_speed_slider_layout)

        # Buttons Layout
        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(self.pause_button)
        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addWidget(self.export_button)

        # Add all control layouts to the main control layout
        control_layout.addLayout(tension_layout)
        control_layout.addLayout(wave_speed_layout)
        control_layout.addLayout(buttons_layout)

        main_layout.addLayout(control_layout, stretch=1)

    # -----------------------
    # Event Handlers
    # -----------------------
    def on_tension_change(self, value):
        self.tension = float(value)
        self.tension_value_label.setText(f"{self.tension:.1f}")
        # Dynamic parameter update

    def on_wave_speed_change(self, value):
        self.wave_speed = float(value)
        self.wave_speed_value_label.setText(f"{self.wave_speed:.1f}")
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
        self.tension = self.default_tension
        self.wave_speed = self.default_wave_speed

        # Reset sliders and labels
        self.tension_slider.setValue(int(self.tension))
        self.wave_speed_slider.setValue(int(self.wave_speed))
        self.tension_value_label.setText(f"{self.tension:.1f}")
        self.wave_speed_value_label.setText(f"{self.wave_speed:.1f}")

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
                    file.write("Time (s),Amplitude\n")
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
        Update the wave's phase based on wave speed and tension.
        """
        # The wave's phase changes over time
        self.phase += self.wave_speed * 0.05  # Adjust the multiplier for speed

        # Log data (for export)
        # Placeholder: log amplitude at a specific point or overall wave parameters
        amplitude = self.amplitude_at_point(100)  # Example point x=100
        current_time = len(self.data_log) * 0.016
        self.data_log.append((current_time, amplitude))

        # Trigger repaint
        self.update()

    def amplitude_at_point(self, x):
        """
        Calculate amplitude at a given x position based on tension and phase.
        """
        return self.tension * math.sin(0.02 * x + self.phase)

    # -----------------------
    # Painting
    # -----------------------
    def paintEvent(self, event):
        painter = QPainter(self.canvas)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.canvas.rect(), QColor(255, 255, 255))

        width = self.canvas.width()
        height = self.canvas.height()

        # Draw base line
        base_y = height / 2
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.drawLine(0, base_y, width, base_y)

        # Draw waves
        painter.setPen(QPen(QColor(0, 0, 255), 2))
        points = []
        for x in range(0, width, 2):
            y = base_y - self.amplitude_at_point(x)
            points.append(QPoint(x, int(y)))

        # Draw polyline for wave
        if points:
            painter.drawPolyline(*points)

        # Draw multiple waves for interference (optional)
        # Example: Add a second wave with different parameters
        # painter.setPen(QPen(QColor(255, 0, 0), 2))
        # points2 = []
        # for x in range(0, width, 2):
        #     y = base_y - (self.tension * math.sin(0.02 * x + self.phase * 1.5))
        #     points2.append(QPoint(x, int(y)))
        # if points2:
        #     painter.drawPolyline(*points2)

        # Optionally draw data log points
        # for data_point in self.data_log:
        #     t, amplitude = data_point
        #     # Convert time to x position or any other representation
        #     x_pos = t * 10  # Example scaling
        #     y_pos = base_y - amplitude
        #     painter.drawEllipse(QPoint(int(x_pos), int(y_pos)), 2, 2)


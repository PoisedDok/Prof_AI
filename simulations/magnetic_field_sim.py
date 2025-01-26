# simulations/magnetic_field_sim.py
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel, QPushButton,
    QFileDialog, QMessageBox, QFrame
)
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
import math
class MagneticFieldSimulation(QWidget):
    """
    Advanced Magnetic Field Simulation with:
    - Separate control panel and simulation canvas
    - Interactive coils
    - Field line visualization
    - Export data functionality
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # Default magnetic field parameters
        self.default_current = 5.0  # Amperes
        self.current = self.default_current
        self.default_turns = 10
        self.turns = self.default_turns

        # Simulation state
        self.simulation_running = True  # Static simulation
        self.data_log = []  # List of tuples: (Current, Turns, Field Strength)

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

        # Current Control
        current_label = QLabel("Current (A)")
        current_label.setToolTip("Adjust the current flowing through the coil.")
        self.current_slider = QSlider(Qt.Horizontal)
        self.current_slider.setRange(1, 20)
        self.current_slider.setValue(int(self.current))
        self.current_slider.setToolTip("Adjust current in Amperes.")
        self.current_slider.valueChanged.connect(self.on_current_change)
        self.current_value_label = QLabel(f"{self.current:.1f}")

        # Turns Control
        turns_label = QLabel("Turns")
        turns_label.setToolTip("Adjust the number of turns in the coil.")
        self.turns_slider = QSlider(Qt.Horizontal)
        self.turns_slider.setRange(1, 50)
        self.turns_slider.setValue(int(self.turns))
        self.turns_slider.setToolTip("Adjust number of coil turns.")
        self.turns_slider.valueChanged.connect(self.on_turns_change)
        self.turns_value_label = QLabel(f"{self.turns}")

        # Buttons
        self.reset_button = QPushButton("Reset")
        self.reset_button.setToolTip("Reset simulation to default parameters.")
        self.reset_button.clicked.connect(self.reset_simulation)

        self.export_button = QPushButton("Export Data")
        self.export_button.setToolTip("Export simulation data to a CSV file.")
        self.export_button.clicked.connect(self.export_data)

        # Arrange controls in layout
        # Current Controls
        current_layout = QVBoxLayout()
        current_layout.addWidget(current_label)
        current_slider_layout = QHBoxLayout()
        current_slider_layout.addWidget(self.current_slider)
        current_slider_layout.addWidget(self.current_value_label)
        current_layout.addLayout(current_slider_layout)

        # Turns Controls
        turns_layout = QVBoxLayout()
        turns_layout.addWidget(turns_label)
        turns_slider_layout = QHBoxLayout()
        turns_slider_layout.addWidget(self.turns_slider)
        turns_slider_layout.addWidget(self.turns_value_label)
        turns_layout.addLayout(turns_slider_layout)

        # Buttons Layout
        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addWidget(self.export_button)

        # Add all control layouts to the main control layout
        control_layout.addLayout(current_layout)
        control_layout.addLayout(turns_layout)
        control_layout.addLayout(buttons_layout)

        main_layout.addLayout(control_layout, stretch=1)

    # -----------------------
    # Event Handlers
    # -----------------------
    def on_current_change(self, value):
        self.current = float(value)
        self.current_value_label.setText(f"{self.current:.1f}")
        self.calculate_field_strength()

    def on_turns_change(self, value):
        self.turns = value
        self.turns_value_label.setText(f"{self.turns}")
        self.calculate_field_strength()

    def calculate_field_strength(self):
        """
        Simplistic magnetic field strength calculation: B = μ₀ * I * N / (2 * R)
        Assuming R is constant and μ₀ = 1 for simplicity.
        """
        R = 100  # Radius in pixels (constant for visualization)
        B = (self.current * self.turns) / (2 * R)
        self.field_strength = B
        self.data_log.append((self.current, self.turns, B))
        self.update()

    def reset_simulation(self):
        # Reset to default parameters
        self.current = self.default_current
        self.turns = self.default_turns

        # Reset sliders and labels
        self.current_slider.setValue(int(self.current))
        self.turns_slider.setValue(int(self.turns))
        self.current_value_label.setText(f"{self.current:.1f}")
        self.turns_value_label.setText(f"{self.turns}")

        # Clear data log
        self.data_log.clear()

        # Recalculate field strength
        self.calculate_field_strength()

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
                    file.write("Current (A),Turns,B Field Strength (μT)\n")
                    for entry in self.data_log:
                        I, N, B = entry
                        file.write(f"{I:.1f},{N},{B:.3f}\n")
                QMessageBox.information(self, "Export Data", f"Data successfully exported to {filename}.")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export data: {e}")

    # -----------------------
    # Painting
    # -----------------------
    def paintEvent(self, event):
        painter = QPainter(self.canvas)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.canvas.rect(), QColor(255, 255, 255))

        width = self.canvas.width()
        height = self.canvas.height()

        # Draw Coil
        coil_center_x = width / 2
        coil_center_y = height / 2
        coil_radius = 50

        painter.setBrush(QColor(192, 192, 192))  # Gray color
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.drawEllipse(int(coil_center_x - coil_radius), int(coil_center_y - coil_radius),
                            2 * coil_radius, 2 * coil_radius)

        # Draw Magnetic Field Lines
        painter.setPen(QPen(QColor(0, 255, 0), 1, Qt.DashLine))
        num_field_lines = 8
        for i in range(1, num_field_lines + 1):
            angle = (360 / num_field_lines) * i
            rad = math.radians(angle)
            x = coil_center_x + coil_radius * math.cos(rad)
            y = coil_center_y + coil_radius * math.sin(rad)
            painter.drawLine(int(coil_center_x), int(coil_center_y), int(x), int(y))

        # Draw Field Strength Label
        painter.setPen(QPen(Qt.black, 1))
        painter.setFont(QFont("Arial", 12))
        painter.drawText(int(coil_center_x - 50), int(coil_center_y - coil_radius - 10),
                         f"B = {self.field_strength:.2f} μT")


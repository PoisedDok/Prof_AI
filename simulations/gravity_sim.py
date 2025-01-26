# simulations/gravity_sim.py
import math
import logging
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel, QPushButton,
    QFileDialog, QMessageBox
)
from PyQt5.QtGui import QPainter, QColor, QPen, QFont

logging.basicConfig(level=logging.DEBUG)

class GravitySimulation(QWidget):
    """
    Advanced Gravity "Orbits" Simulation with:
    - Painting directly in the main widget (no separate QFrame)
    - Adjustable orbit radius for a single planet
    - Real-time animation with start/pause
    - Export data functionality
    - Framework for extended multiple-body, drag-and-drop, etc.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Default orbit simulation parameters
        self.default_orbit_radius = 150  # pixels
        self.orbit_radius = self.default_orbit_radius
        self.angle = 0.0   # Current angular position of the planet

        self.simulation_running = True

        # Timer for animation (approx. 60 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_orbit)
        self.timer.start(16)

        # Data logging for export
        # Each entry: (time_in_seconds, x_position, y_position)
        self.data_log = []

        # Build UI
        self.init_ui()

        logging.debug("GravitySimulation initialized.")

    def init_ui(self):
        """
        Creates layouts for controls (orbit radius, pause/start, etc.)
        """
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # --- Controls (top/bottom or side) ---
        control_layout = QHBoxLayout()

        # Orbit Radius
        radius_label = QLabel("Orbit Radius (px)")
        radius_label.setToolTip("Adjust the radius of the orbiting planet.")
        self.radius_slider = QSlider(Qt.Horizontal)
        self.radius_slider.setRange(50, 300)
        self.radius_slider.setValue(int(self.orbit_radius))
        self.radius_slider.setToolTip("Adjust orbit radius in pixels.")
        self.radius_slider.valueChanged.connect(self.on_radius_change)
        self.radius_value_label = QLabel(f"{self.orbit_radius:.0f}")

        # Start/Pause Button
        self.pause_button = QPushButton("Pause")
        self.pause_button.setToolTip("Pause or resume the simulation.")
        self.pause_button.clicked.connect(self.toggle_simulation)

        # Reset Button
        self.reset_button = QPushButton("Reset")
        self.reset_button.setToolTip("Reset simulation to default parameters.")
        self.reset_button.clicked.connect(self.reset_simulation)

        # Export Data Button
        self.export_button = QPushButton("Export Data")
        self.export_button.setToolTip("Export simulation data to a CSV file.")
        self.export_button.clicked.connect(self.export_data)

        # Arrange orbit radius controls
        radius_layout = QVBoxLayout()
        radius_layout.addWidget(radius_label)
        radius_slider_layout = QHBoxLayout()
        radius_slider_layout.addWidget(self.radius_slider)
        radius_slider_layout.addWidget(self.radius_value_label)
        radius_layout.addLayout(radius_slider_layout)

        # Arrange buttons
        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(self.pause_button)
        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addWidget(self.export_button)

        # Add sub-layouts to main control layout
        control_layout.addLayout(radius_layout)
        control_layout.addLayout(buttons_layout)
        control_layout.addStretch()

        main_layout.addLayout(control_layout, stretch=0)

        # Stretch for drawing space
        # We'll paint the entire widget area below the controls
        # so no separate QFrame is needed.
        # Just let this widget's paintEvent handle it.
        self.setLayout(main_layout)

    # -----------------------
    # Event Handlers
    # -----------------------

    def on_radius_change(self, value):
        self.orbit_radius = float(value)
        self.radius_value_label.setText(f"{self.orbit_radius:.0f}")

    def toggle_simulation(self):
        if self.simulation_running:
            self.timer.stop()
            self.simulation_running = False
            self.pause_button.setText("Start")
            logging.debug("Simulation paused.")
        else:
            self.timer.start(16)
            self.simulation_running = True
            self.pause_button.setText("Pause")
            logging.debug("Simulation resumed.")

    def reset_simulation(self):
        """
        Resets the simulation to default parameters.
        """
        logging.debug("Resetting simulation to defaults.")

        # Orbit parameters
        self.orbit_radius = self.default_orbit_radius
        self.angle = 0.0
        self.radius_slider.setValue(int(self.orbit_radius))
        self.radius_value_label.setText(f"{self.orbit_radius:.0f}")

        # Clear data log
        self.data_log.clear()

        # Update display
        self.update()

    def export_data(self):
        """
        Exports the logged orbit data to a CSV file.
        """
        if not self.data_log:
            QMessageBox.information(self, "Export Data", "No data to export yet.")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Simulation Data", "", "CSV Files (*.csv)"
        )
        if filename:
            try:
                with open(filename, 'w') as file:
                    file.write("Time (s),X (px),Y (px)\n")
                    for entry in self.data_log:
                        t, x, y = entry
                        file.write(f"{t:.3f},{x:.2f},{y:.2f}\n")
                QMessageBox.information(self, "Export Data",
                                        f"Data successfully exported to {filename}.")
                logging.info(f"Gravity simulation data exported to {filename}.")
            except Exception as e:
                logging.error(f"Export failed: {e}")
                QMessageBox.critical(self, "Export Error", f"Failed to export data: {e}")

    # -----------------------
    # Simulation Update
    # -----------------------

    def update_orbit(self):
        """
        Update the orbiting body's position based on angle and radius,
        then request a repaint.
        """
        if not self.simulation_running:
            return

        # Simple constant angular velocity
        self.angle += 0.02  # radians per frame, can be a parameter

        # Calculate position of planet in local coords
        x = self.orbit_radius * math.cos(self.angle)
        y = self.orbit_radius * math.sin(self.angle)

        # Log data (time vs. position). We assume ~16 ms per frame => 1/60 s
        current_time = len(self.data_log) * (16 / 1000.0)
        self.data_log.append((current_time, x, y))

        # Repaint
        self.update()

    # -----------------------
    # Painting
    # -----------------------
    def paintEvent(self, event):
        """
        Draws the star at the center of the widget and the orbiting planet.
        Also can display the orbit path or other references.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Fill background black
        painter.fillRect(self.rect(), QColor(0, 0, 0))

        # Center
        cx = self.width() // 2
        cy = self.height() // 2

        # Draw the star in the center
        star_color = QColor(255, 215, 0)  # golden
        painter.setBrush(star_color)
        painter.setPen(Qt.NoPen)
        star_radius = 20
        painter.drawEllipse(cx - star_radius, cy - star_radius, star_radius * 2, star_radius * 2)

        # Calculate planet's position
        px = cx + int(self.orbit_radius * math.cos(self.angle))
        py = cy + int(self.orbit_radius * math.sin(self.angle))

        # Draw the planet
        planet_color = QColor(0, 0, 255)  # blue
        painter.setBrush(planet_color)
        painter.setPen(Qt.NoPen)
        planet_radius = 10
        painter.drawEllipse(px - planet_radius, py - planet_radius, planet_radius * 2, planet_radius * 2)

        # Draw the orbit path as a dashed circle
        painter.setPen(QPen(QColor(255, 255, 255, 128), 1, Qt.DashLine))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(
            int(cx - self.orbit_radius),  # x position
            int(cy - self.orbit_radius),  # y position
            int(self.orbit_radius * 2),   # width
            int(self.orbit_radius * 2)    # height
        )


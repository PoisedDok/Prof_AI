# simulations/pendulum_sim.py
import math
from PyQt5.QtCore import QTimer, Qt, QPoint
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel, QPushButton,
    QFileDialog, QMessageBox, QFrame
)
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QMouseEvent

class PendulumSimulation(QWidget):
    """
    Advanced Pendulum Simulation with:
    - Separate control panel and simulation canvas
    - Drag-and-drop to set initial angle
    - Real-time parameter updates
    - Tooltips and error handling
    - Export data functionality
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # Default physics parameters
        self.default_angle = math.pi / 4  # 45 degrees
        self.angle = self.default_angle
        self.angular_velocity = 0.0
        self.angular_acceleration = 0.0
        self.default_length = 200.0  # pixels
        self.length = self.default_length
        self.default_gravity = 9.8  # m/s^2
        self.gravity = self.default_gravity
        self.default_damping = 0.995
        self.damping = self.default_damping

        # Simulation state
        self.simulation_running = True
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_pendulum)
        self.timer.start(16)  # ~60 FPS

        # For dragging the pendulum bob
        self.dragging = False

        # Data logging for export
        self.data_log = []  # List of tuples: (time, angle, angular_velocity)

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

        # Gravity Control
        gravity_label = QLabel("Gravity (m/s²)")
        gravity_label.setToolTip("Adjust the gravitational acceleration.")
        self.gravity_slider = QSlider(Qt.Horizontal)
        self.gravity_slider.setRange(1, 20)
        self.gravity_slider.setValue(int(self.gravity))
        self.gravity_slider.setToolTip("Adjust gravitational acceleration.")
        self.gravity_slider.valueChanged.connect(self.on_gravity_change)
        self.gravity_value_label = QLabel(f"{self.gravity:.2f}")

        # Length Control
        length_label = QLabel("Length (px)")
        length_label.setToolTip("Adjust the length of the pendulum.")
        self.length_slider = QSlider(Qt.Horizontal)
        self.length_slider.setRange(50, 300)
        self.length_slider.setValue(int(self.length))
        self.length_slider.setToolTip("Adjust pendulum length in pixels.")
        self.length_slider.valueChanged.connect(self.on_length_change)
        self.length_value_label = QLabel(f"{self.length:.1f}")

        # Damping Control
        damping_label = QLabel("Damping")
        damping_label.setToolTip("Adjust the damping factor (closer to 1 means less damping).")
        self.damping_slider = QSlider(Qt.Horizontal)
        self.damping_slider.setRange(900, 999)  # Represents 0.900 to 0.999
        self.damping_slider.setValue(int(self.damping * 1000))
        self.damping_slider.setToolTip("Adjust damping factor (0.900 - 0.999).")
        self.damping_slider.valueChanged.connect(self.on_damping_change)
        self.damping_value_label = QLabel(f"{self.damping:.3f}")

        # Pause/Start Button
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

        # Arrange controls in layout
        # Gravity Controls
        gravity_layout = QVBoxLayout()
        gravity_layout.addWidget(gravity_label)
        gravity_slider_layout = QHBoxLayout()
        gravity_slider_layout.addWidget(self.gravity_slider)
        gravity_slider_layout.addWidget(self.gravity_value_label)
        gravity_layout.addLayout(gravity_slider_layout)

        # Length Controls
        length_layout = QVBoxLayout()
        length_layout.addWidget(length_label)
        length_slider_layout = QHBoxLayout()
        length_slider_layout.addWidget(self.length_slider)
        length_slider_layout.addWidget(self.length_value_label)
        length_layout.addLayout(length_slider_layout)

        # Damping Controls
        damping_layout = QVBoxLayout()
        damping_layout.addWidget(damping_label)
        damping_slider_layout = QHBoxLayout()
        damping_slider_layout.addWidget(self.damping_slider)
        damping_slider_layout.addWidget(self.damping_value_label)
        damping_layout.addLayout(damping_slider_layout)

        # Buttons Layout
        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(self.pause_button)
        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addWidget(self.export_button)

        # Add all control layouts to the main control layout
        control_layout.addLayout(gravity_layout)
        control_layout.addLayout(length_layout)
        control_layout.addLayout(damping_layout)
        control_layout.addLayout(buttons_layout)

        main_layout.addLayout(control_layout, stretch=1)

    # -----------------------
    # Event Handlers
    # -----------------------
    def on_gravity_change(self, value):
        self.gravity = float(value)
        self.gravity_value_label.setText(f"{self.gravity:.2f}")
        # Optionally reset simulation or adjust parameters dynamically
        # self.reset_simulation()

    def on_length_change(self, value):
        self.length = float(value)
        self.length_value_label.setText(f"{self.length:.1f}")
        # Optionally reset simulation or adjust parameters dynamically
        # self.reset_simulation()

    def on_damping_change(self, value):
        self.damping = float(value) / 1000.0
        self.damping_value_label.setText(f"{self.damping:.3f}")
        # Optionally reset simulation or adjust parameters dynamically
        # self.reset_simulation()

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
        # Reset physics parameters to default
        self.angle = self.default_angle
        self.angular_velocity = 0.0
        self.angular_acceleration = 0.0
        self.length = self.default_length
        self.gravity = self.default_gravity
        self.damping = self.default_damping

        # Reset sliders and labels
        self.gravity_slider.setValue(int(self.gravity))
        self.length_slider.setValue(int(self.length))
        self.damping_slider.setValue(int(self.damping * 1000))

        self.gravity_value_label.setText(f"{self.gravity:.2f}")
        self.length_value_label.setText(f"{self.length:.1f}")
        self.damping_value_label.setText(f"{self.damping:.3f}")

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
                    file.write("Time,Angle (rad),Angular Velocity (rad/s)\n")
                    for entry in self.data_log:
                        file.write(f"{entry[0]:.3f},{entry[1]:.5f},{entry[2]:.5f}\n")
                QMessageBox.information(self, "Export Data", f"Data successfully exported to {filename}.")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export data: {e}")

    # -----------------------
    # Simulation Update
    # -----------------------
    def update_pendulum(self):
        """
        Update the pendulum's physics and log data.
        """
        # Update physics
        self.angular_acceleration = -(self.gravity / self.length) * math.sin(self.angle)
        self.angular_velocity += self.angular_acceleration
        self.angle += self.angular_velocity
        self.angular_velocity *= self.damping

        # Log data (for export)
        # Assuming each timer tick is ~16 ms
        if not self.data_log:
            current_time = 0.0
        else:
            current_time = self.data_log[-1][0] + 0.016
        self.data_log.append((current_time, self.angle, self.angular_velocity))

        # Trigger repaint
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

        # Pivot point (center-top of the canvas)
        pivot_x = width / 2
        pivot_y = height / 4

        # Bob position
        bob_x = pivot_x + self.length * math.sin(self.angle)
        bob_y = pivot_y + self.length * math.cos(self.angle)

        # Draw rod
        pen = QPen(QColor(0, 0, 0), 2)
        painter.setPen(pen)
        painter.drawLine(pivot_x, pivot_y, bob_x, bob_y)

        # Draw pivot
        painter.setBrush(QColor(0, 0, 0))
        painter.drawEllipse(QPoint(int(pivot_x), int(pivot_y)), 5, 5)

        # Draw bob
        painter.setBrush(QColor(200, 0, 0))
        painter.drawEllipse(QPoint(int(bob_x), int(bob_y)), 15, 15)

    # -----------------------
    # Mouse Events for Dragging Bob
    # -----------------------
    def mousePressEvent(self, event):
        """
        Detect if the mouse press is near the bob to start dragging.
        """
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            canvas_rect = self.canvas.geometry()
            pivot_x = canvas_rect.x() + self.canvas.width() / 2
            pivot_y = canvas_rect.y() + self.canvas.height() / 4
            bob_x = pivot_x + self.length * math.sin(self.angle)
            bob_y = pivot_y + self.length * math.cos(self.angle)

            distance_sq = (pos.x() - bob_x) ** 2 + (pos.y() - bob_y) ** 2
            if distance_sq <= 15 ** 2:
                self.dragging = True
                self.timer.stop()
                self.pause_button.setText("Start")

    def mouseMoveEvent(self, event):
        """
        Update the angle based on mouse movement while dragging.
        """
        if self.dragging:
            pos = event.pos()
            canvas_rect = self.canvas.geometry()
            pivot_x = canvas_rect.x() + self.canvas.width() / 2
            pivot_y = canvas_rect.y() + self.canvas.height() / 4

            dx = pos.x() - pivot_x
            dy = pos.y() - pivot_y

            if dy != 0:
                new_angle = math.atan2(dx, dy)
                self.angle = new_angle
                self.angular_velocity = 0  # Reset velocity when manually setting angle
                self.update()

    def mouseReleaseEvent(self, event):
        """
        Stop dragging and resume simulation.
        """
        if event.button() == Qt.LeftButton and self.dragging:
            self.dragging = False
            if self.simulation_running:
                self.timer.start(16)


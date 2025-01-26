# simulations/projectile_sim.py
import math
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel, QPushButton,
    QFileDialog, QMessageBox, QFrame
)
from PyQt5.QtGui import QPainter, QColor, QPen

class ProjectileSimulation(QWidget):
    """
    Advanced Projectile Motion Simulation with:
    - Separate control panel and simulation canvas
    - Trajectory prediction
    - Dynamic parameter updates
    - Export data functionality
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # Default physics parameters
        self.default_gravity = 9.8  # m/s^2
        self.gravity = self.default_gravity
        self.default_angle_deg = 45.0  # degrees
        self.angle_deg = self.default_angle_deg
        self.default_speed = 50.0  # m/s
        self.speed = self.default_speed

        # Simulation state
        self.simulation_running = True
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_motion)
        self.timer.start(16)  # ~60 FPS

        # Data logging for export
        self.data_log = []  # List of tuples: (time, x, y)

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

        # Angle Control
        angle_label = QLabel("Angle (°)")
        angle_label.setToolTip("Adjust the launch angle.")
        self.angle_slider = QSlider(Qt.Horizontal)
        self.angle_slider.setRange(0, 90)
        self.angle_slider.setValue(int(self.angle_deg))
        self.angle_slider.setToolTip("Adjust launch angle in degrees.")
        self.angle_slider.valueChanged.connect(self.on_angle_change)
        self.angle_value_label = QLabel(f"{self.angle_deg:.1f}")

        # Speed Control
        speed_label = QLabel("Speed (m/s)")
        speed_label.setToolTip("Adjust the initial speed.")
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(10, 100)
        self.speed_slider.setValue(int(self.speed))
        self.speed_slider.setToolTip("Adjust initial speed in m/s.")
        self.speed_slider.valueChanged.connect(self.on_speed_change)
        self.speed_value_label = QLabel(f"{self.speed:.1f}")

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
        # Gravity Controls
        gravity_layout = QVBoxLayout()
        gravity_layout.addWidget(gravity_label)
        gravity_slider_layout = QHBoxLayout()
        gravity_slider_layout.addWidget(self.gravity_slider)
        gravity_slider_layout.addWidget(self.gravity_value_label)
        gravity_layout.addLayout(gravity_slider_layout)

        # Angle Controls
        angle_layout = QVBoxLayout()
        angle_layout.addWidget(angle_label)
        angle_slider_layout = QHBoxLayout()
        angle_slider_layout.addWidget(self.angle_slider)
        angle_slider_layout.addWidget(self.angle_value_label)
        angle_layout.addLayout(angle_slider_layout)

        # Speed Controls
        speed_layout = QVBoxLayout()
        speed_layout.addWidget(speed_label)
        speed_slider_layout = QHBoxLayout()
        speed_slider_layout.addWidget(self.speed_slider)
        speed_slider_layout.addWidget(self.speed_value_label)
        speed_layout.addLayout(speed_slider_layout)

        # Buttons Layout
        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(self.pause_button)
        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addWidget(self.export_button)

        # Add all control layouts to the main control layout
        control_layout.addLayout(gravity_layout)
        control_layout.addLayout(angle_layout)
        control_layout.addLayout(speed_layout)
        control_layout.addLayout(buttons_layout)

        main_layout.addLayout(control_layout, stretch=1)

    # -----------------------
    # Event Handlers
    # -----------------------
    def on_gravity_change(self, value):
        self.gravity = float(value)
        self.gravity_value_label.setText(f"{self.gravity:.2f}")
        # Dynamic parameter update

    def on_angle_change(self, value):
        self.angle_deg = float(value)
        self.angle_value_label.setText(f"{self.angle_deg:.1f}")
        # Dynamic parameter update

    def on_speed_change(self, value):
        self.speed = float(value)
        self.speed_value_label.setText(f"{self.speed:.1f}")
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
        self.gravity = self.default_gravity
        self.angle_deg = self.default_angle_deg
        self.speed = self.default_speed
        self.gravity_slider.setValue(int(self.gravity))
        self.angle_slider.setValue(int(self.angle_deg))
        self.speed_slider.setValue(int(self.speed))
        self.gravity_value_label.setText(f"{self.gravity:.2f}")
        self.angle_value_label.setText(f"{self.angle_deg:.1f}")
        self.speed_value_label.setText(f"{self.speed:.1f}")

        # Reset simulation state
        self.time = 0.0
        self.position = (0.0, 0.0)
        self.path = []
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
                    file.write("Time (s),X (m),Y (m)\n")
                    for entry in self.data_log:
                        file.write(f"{entry[0]:.3f},{entry[1]:.3f},{entry[2]:.3f}\n")
                QMessageBox.information(self, "Export Data", f"Data successfully exported to {filename}.")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export data: {e}")

    # -----------------------
    # Simulation Update
    # -----------------------
    def update_motion(self):
        """
        Update the projectile's position based on physics equations.
        """
        # Convert angle to radians
        angle_rad = math.radians(self.angle_deg)

        # Calculate velocities
        vx = self.speed * math.cos(angle_rad)
        vy = self.speed * math.sin(angle_rad)

        # Time increment
        dt = 0.016  # ~60 FPS
        self.time += dt

        # Update positions
        x = vx * self.time
        y = vy * self.time - 0.5 * self.gravity * (self.time ** 2)

        # Log data
        self.data_log.append((self.time, x, y))

        # Reset if projectile hits the ground
        if y < 0:
            self.reset_simulation()
        else:
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

        # Ground level
        ground_y = height - 20
        painter.setPen(QPen(QColor(0, 128, 0), 2))
        painter.drawLine(0, ground_y, width, ground_y)

        # Draw trajectory path
        painter.setPen(QPen(QColor(0, 0, 255), 2))
        for i in range(1, len(self.data_log)):
            x1, y1 = self.data_log[i - 1][1], self.data_log[i - 1][2]
            x2, y2 = self.data_log[i][1], self.data_log[i][2]
            painter.drawLine(
                int(x1), int(ground_y - y1),
                int(x2), int(ground_y - y2)
            )

        # Draw projectile
        if self.data_log:
            x, y = self.data_log[-1][1], self.data_log[-1][2]
            painter.setBrush(QColor(255, 0, 0))
            painter.drawEllipse(int(x) - 10, int(ground_y - y) - 10, 20, 20)

        # Draw trajectory prediction (dashed line)
        # Calculate predicted trajectory until it hits the ground
        prediction_pen = QPen(QColor(150, 150, 150), 1, Qt.DashLine)
        painter.setPen(prediction_pen)
        prediction_points = []
        for t in range(int(self.time * 100), int((self.time + 5) * 100)):
            t_sec = t / 100.0
            pred_x = self.speed * math.cos(math.radians(self.angle_deg)) * t_sec
            pred_y = self.speed * math.sin(math.radians(self.angle_deg)) * t_sec - 0.5 * self.gravity * (t_sec ** 2)
            if pred_y < 0:
                break
            prediction_points.append((pred_x, pred_y))
        for i in range(1, len(prediction_points)):
            x1, y1 = prediction_points[i - 1]
            x2, y2 = prediction_points[i]
            painter.drawLine(
                int(x1), int(ground_y - y1),
                int(x2), int(ground_y - y2)
            )

    # -----------------------
    # Export Functionality
    # -----------------------
    # The `export_data` method is already implemented above.


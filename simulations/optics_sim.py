# simulations/optics_sim.py
import math
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel, QPushButton,
    QFileDialog, QMessageBox, QFrame
)
from PyQt5.QtGui import QPainter, QColor, QPen, QFont

class OpticsSimulation(QWidget):
    """
    Advanced Optics Simulation with:
    - Separate control panel and simulation canvas
    - Ray tracing for lens combinations
    - Export data functionality
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # Default optics parameters
        self.default_focal_length = 50  # pixels
        self.focal_length = self.default_focal_length
        self.default_object_distance = 150  # pixels
        self.object_distance = self.default_object_distance

        # Simulation state
        self.simulation_running = True  # Not much dynamic behavior
        self.data_log = []  # List of tuples: (Object Distance, Image Distance)

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

        # Focal Length Control
        f_label = QLabel("Focal Length (px)")
        f_label.setToolTip("Adjust the focal length of the lens.")
        self.f_slider = QSlider(Qt.Horizontal)
        self.f_slider.setRange(10, 100)
        self.f_slider.setValue(int(self.focal_length))
        self.f_slider.setToolTip("Adjust focal length in pixels.")
        self.f_slider.valueChanged.connect(self.on_f_change)
        self.f_value_label = QLabel(f"{self.focal_length}")

        # Object Distance Control
        o_label = QLabel("Object Distance (px)")
        o_label.setToolTip("Adjust the distance of the object from the lens.")
        self.o_slider = QSlider(Qt.Horizontal)
        self.o_slider.setRange(10, 300)
        self.o_slider.setValue(int(self.object_distance))
        self.o_slider.setToolTip("Adjust object distance in pixels.")
        self.o_slider.valueChanged.connect(self.on_o_change)
        self.o_value_label = QLabel(f"{self.object_distance}")

        # Buttons
        self.reset_button = QPushButton("Reset")
        self.reset_button.setToolTip("Reset simulation to default parameters.")
        self.reset_button.clicked.connect(self.reset_simulation)

        self.export_button = QPushButton("Export Data")
        self.export_button.setToolTip("Export simulation data to a CSV file.")
        self.export_button.clicked.connect(self.export_data)

        # Arrange controls in layout
        # Focal Length Controls
        f_layout = QVBoxLayout()
        f_layout.addWidget(f_label)
        f_slider_layout = QHBoxLayout()
        f_slider_layout.addWidget(self.f_slider)
        f_slider_layout.addWidget(self.f_value_label)
        f_layout.addLayout(f_slider_layout)

        # Object Distance Controls
        o_layout = QVBoxLayout()
        o_layout.addWidget(o_label)
        o_slider_layout = QHBoxLayout()
        o_slider_layout.addWidget(self.o_slider)
        o_slider_layout.addWidget(self.o_value_label)
        o_layout.addLayout(o_slider_layout)

        # Buttons Layout
        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addWidget(self.export_button)

        # Add all control layouts to the main control layout
        control_layout.addLayout(f_layout)
        control_layout.addLayout(o_layout)
        control_layout.addLayout(buttons_layout)

        main_layout.addLayout(control_layout, stretch=1)

    # -----------------------
    # Event Handlers
    # -----------------------
    def on_f_change(self, value):
        self.focal_length = float(value)
        self.f_value_label.setText(f"{self.focal_length}")
        self.calculate_image_distance()

    def on_o_change(self, value):
        self.object_distance = float(value)
        self.o_value_label.setText(f"{self.object_distance}")
        self.calculate_image_distance()

    def calculate_image_distance(self):
        """
        Using the lens formula:
        1/f = 1/do + 1/di => di = (f * do) / (do - f)
        """
        f = self.focal_length
        do = self.object_distance

        if do == f:
            di = float('inf')  # Image at infinity
            self.image_distance = di
            self.image_label_text = "Image Distance: ∞"
        else:
            di = (f * do) / (do - f)
            self.image_distance = di
            self.image_label_text = f"Image Distance: {di:.2f} px"

        # Log data
        self.data_log.append((do, di))

        self.update()

    def reset_simulation(self):
        # Reset to default parameters
        self.focal_length = self.default_focal_length
        self.object_distance = self.default_object_distance

        # Reset sliders and labels
        self.f_slider.setValue(int(self.focal_length))
        self.o_slider.setValue(int(self.object_distance))
        self.f_value_label.setText(f"{self.focal_length}")
        self.o_value_label.setText(f"{self.object_distance}")

        # Clear data log
        self.data_log.clear()

        # Recalculate image distance
        self.calculate_image_distance()

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
                    file.write("Object Distance (px),Image Distance (px)\n")
                    for entry in self.data_log:
                        do, di = entry
                        if di == float('inf'):
                            di_str = "∞"
                        else:
                            di_str = f"{di:.2f}"
                        file.write(f"{do:.1f},{di_str}\n")
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

        # Draw Lens in the center
        lens_x = width / 2
        lens_y_top = height / 2 - 100
        lens_y_bottom = height / 2 + 100
        lens_width = 40

        painter.setBrush(QColor(173, 216, 230, 128))  # Light blue with transparency
        painter.drawRect(lens_x - lens_width / 2, lens_y_top, lens_width, lens_y_bottom - lens_y_top)

        # Draw object
        object_x = lens_x - self.object_distance
        object_y = height / 2
        painter.setBrush(QColor(255, 0, 0))  # Red
        painter.drawRect(object_x - 10, object_y - 50, 20, 100)  # Object as a vertical bar

        # Draw image
        if self.image_distance != float('inf'):
            image_x = lens_x + self.image_distance
            image_y = height / 2
            painter.setBrush(QColor(0, 0, 255))  # Blue
            painter.drawRect(image_x - 10, image_y - 50, 20, 100)  # Image as a vertical bar

        # Draw Focal Points
        painter.setPen(QPen(QColor(0, 255, 0), 1, Qt.DashLine))
        # Front focal point
        painter.drawLine(lens_x + self.focal_length, 0, lens_x + self.focal_length, height)
        # Back focal point
        painter.drawLine(lens_x - self.focal_length, 0, lens_x - self.focal_length, height)

        # Draw Labels
        painter.setPen(QPen(Qt.black, 1))
        painter.setFont(QFont("Arial", 10))
        painter.drawText(object_x - 10, object_y - 60, "Object")
        if self.image_distance != float('inf'):
            painter.drawText(lens_x + self.image_distance - 10, height / 2 - 60, "Image")

        # Update data log
        if self.object_distance != 0 and self.focal_length != self.object_distance:
            di = (self.focal_length * self.object_distance) / (self.object_distance - self.focal_length)
            self.data_log.append((self.object_distance, di))


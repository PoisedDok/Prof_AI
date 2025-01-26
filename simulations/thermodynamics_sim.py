# simulations/thermodynamics_sim.py
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel, QPushButton,
    QFileDialog, QMessageBox, QFrame
)
from PyQt5.QtGui import QPainter, QColor, QPen, QFont

class ThermodynamicsSimulation(QWidget):
    """
    Advanced Thermodynamics Simulation with:
    - Separate control panel and simulation canvas
    - PV Diagram
    - Interactive Heat Engine simulation (Placeholder)
    - Export data functionality
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # Default thermodynamic parameters
        self.default_temperature = 300  # Kelvin
        self.temperature = self.default_temperature
        self.default_volume = 1.0       # Arbitrary units
        self.volume = self.default_volume
        self.default_pressure = 1.0     # atm
        self.pressure = self.default_pressure

        # Simulation state
        self.timer = None  # Not needed for static simulation
        self.data_log = []  # List of tuples: (Temperature, Volume, Pressure)

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

        # Temperature Control
        temp_label = QLabel("Temperature (K)")
        temp_label.setToolTip("Adjust the temperature.")
        self.temp_slider = QSlider(Qt.Horizontal)
        self.temp_slider.setRange(200, 600)
        self.temp_slider.setValue(int(self.temperature))
        self.temp_slider.setToolTip("Adjust temperature in Kelvin.")
        self.temp_slider.valueChanged.connect(self.on_temp_change)
        self.temp_value_label = QLabel(f"{self.temperature:.0f}")

        # Volume Control
        vol_label = QLabel("Volume")
        vol_label.setToolTip("Adjust the volume.")
        self.vol_slider = QSlider(Qt.Horizontal)
        self.vol_slider.setRange(1, 10)
        self.vol_slider.setValue(int(self.volume))
        self.vol_slider.setToolTip("Adjust volume.")
        self.vol_slider.valueChanged.connect(self.on_vol_change)
        self.vol_value_label = QLabel(f"{self.volume:.1f}")

        # Pressure Control
        pres_label = QLabel("Pressure (atm)")
        pres_label.setToolTip("Adjust the pressure.")
        self.pres_slider = QSlider(Qt.Horizontal)
        self.pres_slider.setRange(1, 20)
        self.pres_slider.setValue(int(self.pressure))
        self.pres_slider.setToolTip("Adjust pressure in atmospheres.")
        self.pres_slider.valueChanged.connect(self.on_pres_change)
        self.pres_value_label = QLabel(f"{self.pressure:.1f}")

        # Buttons
        self.reset_button = QPushButton("Reset")
        self.reset_button.setToolTip("Reset simulation to default parameters.")
        self.reset_button.clicked.connect(self.reset_simulation)

        self.export_button = QPushButton("Export Data")
        self.export_button.setToolTip("Export simulation data to a CSV file.")
        self.export_button.clicked.connect(self.export_data)

        # Arrange controls in layout
        # Temperature Controls
        temp_layout = QVBoxLayout()
        temp_layout.addWidget(temp_label)
        temp_slider_layout = QHBoxLayout()
        temp_slider_layout.addWidget(self.temp_slider)
        temp_slider_layout.addWidget(self.temp_value_label)
        temp_layout.addLayout(temp_slider_layout)

        # Volume Controls
        vol_layout = QVBoxLayout()
        vol_layout.addWidget(vol_label)
        vol_slider_layout = QHBoxLayout()
        vol_slider_layout.addWidget(self.vol_slider)
        vol_slider_layout.addWidget(self.vol_value_label)
        vol_layout.addLayout(vol_slider_layout)

        # Pressure Controls
        pres_layout = QVBoxLayout()
        pres_layout.addWidget(pres_label)
        pres_slider_layout = QHBoxLayout()
        pres_slider_layout.addWidget(self.pres_slider)
        pres_slider_layout.addWidget(self.pres_value_label)
        pres_layout.addLayout(pres_slider_layout)

        # Buttons Layout
        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addWidget(self.export_button)

        # Add all control layouts to the main control layout
        control_layout.addLayout(temp_layout)
        control_layout.addLayout(vol_layout)
        control_layout.addLayout(pres_layout)
        control_layout.addLayout(buttons_layout)

        main_layout.addLayout(control_layout, stretch=1)

    # -----------------------
    # Event Handlers
    # -----------------------
    def on_temp_change(self, value):
        self.temperature = float(value)
        self.temp_value_label.setText(f"{self.temperature:.0f}")
        self.calculate_pressure()

    def on_vol_change(self, value):
        self.volume = float(value)
        self.vol_value_label.setText(f"{self.volume:.1f}")
        self.calculate_pressure()

    def on_pres_change(self, value):
        self.pressure = float(value)
        self.pres_value_label.setText(f"{self.pressure:.1f}")
        self.calculate_pressure()

    def calculate_pressure(self):
        """
        Simple ideal gas law: PV = nRT (Assuming nR = 1 for simplicity)
        Thus, P = T / V
        """
        if self.volume == 0:
            self.pressure = 0
        else:
            self.pressure = self.temperature / self.volume
        self.pres_slider.blockSignals(True)
        self.pres_slider.setValue(int(self.pressure))
        self.pres_slider.blockSignals(False)
        self.pres_value_label.setText(f"{self.pressure:.1f}")

        # Log data
        self.data_log.append((self.temperature, self.volume, self.pressure))

        self.update()

    def reset_simulation(self):
        # Reset to default parameters
        self.temperature = self.default_temperature
        self.volume = self.default_volume
        self.pressure = self.default_pressure

        # Reset sliders and labels
        self.temp_slider.setValue(int(self.temperature))
        self.vol_slider.setValue(int(self.volume))
        self.pres_slider.setValue(int(self.pressure))

        self.temp_value_label.setText(f"{self.temperature:.0f}")
        self.vol_value_label.setText(f"{self.volume:.1f}")
        self.pres_value_label.setText(f"{self.pressure:.1f}")

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
                    file.write("Temperature (K),Volume,Pressure (atm)\n")
                    for entry in self.data_log:
                        file.write(f"{entry[0]:.0f},{entry[1]:.1f},{entry[2]:.1f}\n")
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

        # Draw PV Diagram
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        margin = 50
        # X-axis (Volume)
        painter.drawLine(margin, height - margin, width - margin, height - margin)
        # Y-axis (Pressure)
        painter.drawLine(margin, margin, margin, height - margin)

        # Labels
        painter.setFont(QFont("Arial", 12))
        painter.drawText(width - margin + 10, height - margin + 5, "Volume")
        painter.drawText(margin - 40, margin - 10, "Pressure")

        # Plot data points
        painter.setPen(QPen(QColor(255, 0, 0), 2))
        scale_x = (width - 2 * margin) / 10  # Assuming Volume ranges from 1 to 10
        scale_y = (height - 2 * margin) / 20  # Assuming Pressure ranges from 1 to 20

        points = []
        for entry in self.data_log:
            temp, vol, pres = entry
            x = margin + vol * scale_x
            y = height - margin - pres * scale_y
            points.append((x, y))

        for i in range(1, len(points)):
            painter.drawLine(int(points[i - 1][0]), int(points[i - 1][1]),
                             int(points[i][0]), int(points[i][1]))

        # Draw Current Pressure and Volume
        if self.data_log:
            current_p = self.pressure
            current_v = self.volume
            x = margin + current_v * scale_x
            y = height - margin - current_p * scale_y
            painter.setBrush(QColor(0, 255, 0))
            painter.drawEllipse(int(x) - 5, int(y) - 5, 10, 10)


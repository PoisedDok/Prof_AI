# simulations/electric_circuit_sim.py
import math
import logging
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel, QPushButton,
    QFileDialog, QMessageBox, QComboBox, QSpinBox, QFrame
)
from PyQt5.QtGui import QPainter, QColor, QPen, QFont

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

class ElectricCircuitSimulation(QWidget):
    """
    A flexible circuit playground for classes 1-10.
    - Supports 1-4 resistors
    - Series or Parallel configuration
    - Real-time calculation of total resistance and current
    - Error handling for invalid resistor values
    - Data logging and export functionality
    - Friendly UI with dynamic drawing
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Default circuit parameters
        self.default_voltage = 9.0
        self.voltage = self.default_voltage

        # Circuit type can be 'Series' or 'Parallel'
        self.circuit_type = "Series"

        # Number of resistors (1–4)
        self.num_resistors = 2

        # Resistances stored in a list
        self.default_resistance = [100.0, 100.0, 200.0, 300.0]
        self.resistances = self.default_resistance[:self.num_resistors]

        # Computed values
        self.current = 0.0
        self.total_resistance = 0.0

        # Data log: (Voltage, [R...], circuitType, totalR, current)
        self.data_log = []

        self._init_ui()
        self._calculate_current()

        logging.info("ElectricCircuitSimulation initialized.")

    def _init_ui(self):
        """
        Sets up the UI with dynamic resistor sliders and a simple circuit diagram.
        """
        self.setMinimumSize(700, 500)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # ----------------
        # Controls Layout
        # ----------------
        control_layout = QHBoxLayout()

        # Voltage Slider
        voltage_layout = QVBoxLayout()
        lbl_voltage = QLabel("Voltage (V)")
        self.slider_voltage = QSlider(Qt.Horizontal)
        self.slider_voltage.setRange(1, 50)
        self.slider_voltage.setValue(int(self.voltage))
        self.slider_voltage.valueChanged.connect(self.on_voltage_changed)
        self.lbl_voltage_val = QLabel(f"{self.voltage:.1f}")

        voltage_layout.addWidget(lbl_voltage)
        hl_v = QHBoxLayout()
        hl_v.addWidget(self.slider_voltage)
        hl_v.addWidget(self.lbl_voltage_val)
        voltage_layout.addLayout(hl_v)
        control_layout.addLayout(voltage_layout)

        # Circuit Type Combo
        type_layout = QVBoxLayout()
        lbl_type = QLabel("Circuit Type")
        self.combo_type = QComboBox()
        self.combo_type.addItems(["Series", "Parallel"])
        self.combo_type.setCurrentText(self.circuit_type)
        self.combo_type.currentTextChanged.connect(self.on_circuit_type_changed)
        type_layout.addWidget(lbl_type)
        type_layout.addWidget(self.combo_type)
        control_layout.addLayout(type_layout)

        # Number of Resistors
        resistor_count_layout = QVBoxLayout()
        lbl_num_res = QLabel("Num Resistors")
        self.spin_resistor_count = QSpinBox()
        self.spin_resistor_count.setRange(1, 4)
        self.spin_resistor_count.setValue(self.num_resistors)
        self.spin_resistor_count.valueChanged.connect(self.on_num_resistors_changed)
        resistor_count_layout.addWidget(lbl_num_res)
        resistor_count_layout.addWidget(self.spin_resistor_count)
        control_layout.addLayout(resistor_count_layout)

        # Buttons: Reset & Export
        btn_layout = QVBoxLayout()
        self.btn_reset = QPushButton("Reset")
        self.btn_reset.clicked.connect(self.reset_simulation)

        self.btn_export = QPushButton("Export CSV")
        self.btn_export.clicked.connect(self.export_data)

        btn_layout.addWidget(self.btn_reset)
        btn_layout.addWidget(self.btn_export)
        control_layout.addLayout(btn_layout)

        # Add the top control layout
        main_layout.addLayout(control_layout)

        # ----------------
        # Resistors Sliders
        # ----------------
        self.resistor_layout = QVBoxLayout()
        self._build_resistor_controls()  # dynamically add resistor sliders
        main_layout.addLayout(self.resistor_layout)

        # ----------------
        # Labels: Current & Resistance
        # ----------------
        self.info_label = QLabel("Current: 0.00 A | Total R: 0.00 Ω")
        self.info_label.setFont(QFont("Arial", 12))
        main_layout.addWidget(self.info_label, alignment=Qt.AlignCenter)

        logging.info("UI initialization complete.")

    def _build_resistor_controls(self):
        """
        Builds or rebuilds the resistor slider controls based on num_resistors.
        Clears existing layout items first.
        """
        # Clear the layout
        while self.resistor_layout.count():
            item = self.resistor_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Create sliders for each resistor
        for i in range(self.num_resistors):
            resistor_box = QHBoxLayout()
            lbl = QLabel(f"R{i+1} (Ω):")
            lbl.setFixedWidth(60)

            slider = QSlider(Qt.Horizontal)
            slider.setRange(1, 2000)
            slider.setValue(int(self.resistances[i]))
            slider.valueChanged.connect(lambda val, idx=i: self._on_resistance_changed(val, idx))

            lbl_val = QLabel(f"{self.resistances[i]:.1f}")

            # Store references
            resistor_box.addWidget(lbl)
            resistor_box.addWidget(slider)
            resistor_box.addWidget(lbl_val)
            self.resistor_layout.addLayout(resistor_box)

            # Attach as custom attributes so we can update label text on change
            slider_lbl_name = f"_slider_label_{i}"
            setattr(self, slider_lbl_name, lbl_val)

        logging.info("Resistor controls rebuilt for %d resistors.", self.num_resistors)

    # ----------------------------
    # Event Handlers / Callbacks
    # ----------------------------
    def on_voltage_changed(self, value):
        self.voltage = float(value)
        self.lbl_voltage_val.setText(f"{self.voltage:.1f}")
        self._calculate_current()

    def on_circuit_type_changed(self, text):
        self.circuit_type = text
        logging.info("Circuit type changed to %s", text)
        self._calculate_current()

    def on_num_resistors_changed(self, count):
        # Keep previous resistor values, but only up to new count
        self.num_resistors = count
        # Expand or shrink the self.resistances array to match new count
        if count > len(self.resistances):
            # Add additional default values
            needed = count - len(self.resistances)
            self.resistances.extend(self.default_resistance[len(self.resistances):len(self.resistances)+needed])
        else:
            # Truncate the array
            self.resistances = self.resistances[:count]

        # Rebuild sliders
        self._build_resistor_controls()
        self._calculate_current()

    def _on_resistance_changed(self, value, index):
        """
        Called when the user changes one of the resistor sliders.
        """
        # Validate to avoid zero or negative
        if value < 1:
            value = 1
        self.resistances[index] = float(value)
        # Update label
        lbl_val = getattr(self, f"_slider_label_{index}", None)
        if lbl_val:
            lbl_val.setText(f"{self.resistances[index]:.1f}")

        self._calculate_current()

    # ----------------------------
    # Calculation Methods
    # ----------------------------
    def _calculate_current(self):
        """
        Computes total resistance based on circuit type and resistor list,
        then calculates current from I = V / R.
        """
        if self.circuit_type == "Series":
            self.total_resistance = sum(self.resistances)
        else:  # "Parallel"
            # sum(1/Ri) => 1/that
            inv_sum = 0.0
            for r in self.resistances:
                inv_sum += (1.0 / r)
            if inv_sum == 0:
                self.total_resistance = float('inf')
            else:
                self.total_resistance = 1.0 / inv_sum

        if math.isinf(self.total_resistance) or self.total_resistance == 0:
            # No valid total R => infinite or zero, handle gracefully
            self.current = float('inf')
        else:
            self.current = self.voltage / self.total_resistance

        # Update UI
        if math.isinf(self.current):
            txt_current = "∞"
        else:
            txt_current = f"{self.current:.2f}"
        txt_r = "∞" if math.isinf(self.total_resistance) else f"{self.total_resistance:.2f}"

        self.info_label.setText(f"Current: {txt_current} A | Total R: {txt_r} Ω")

        # Log data
        self.data_log.append((self.voltage, list(self.resistances), self.circuit_type, self.total_resistance, self.current))
        logging.info(
            "Calculated Current=%.3f, TotalR=%.3f, Type=%s, Resistances=%s",
            self.current,
            self.total_resistance,
            self.circuit_type,
            self.resistances
        )

        self.update()

    # ----------------------------
    # Painting
    # ----------------------------
    def paintEvent(self, event):
        """
        Draws a simplified circuit diagram depending on circuit type and resistor count.
        """
        painter = QPainter(self)
        if not painter.isActive():
            return
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()

        # Basic margin
        margin_left = 80
        margin_right = 80
        mid_y = height // 2

        # Battery block
        battery_width = 50
        battery_height = 100
        battery_x = margin_left
        battery_y = mid_y - battery_height // 2

        # Draw battery
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.setBrush(QColor(255, 215, 0))
        painter.drawRect(int(battery_x), int(battery_y), battery_width, battery_height)

        # Wire from battery to first resistor
        wire_start_x = battery_x + battery_width
        wire_start_y = mid_y
        painter.drawLine(wire_start_x, wire_start_y, wire_start_x + 20, wire_start_y)

        # Resistive network drawing
        network_start_x = wire_start_x + 20
        network_end_x = width - margin_right
        dx = network_end_x - network_start_x

        # Depending on circuit type, draw in a row (series) or stacked parallels
        if self.circuit_type == "Series":
            # Each resistor is placed horizontally in sequence
            segment_width = dx // (self.num_resistors + 1)

            prev_x = network_start_x
            for i in range(self.num_resistors):
                resistor_x = prev_x + segment_width
                resistor_y = mid_y - 10
                self._draw_resistor(painter, resistor_x, resistor_y, 40, 20)
                # Connect wire from previous
                painter.drawLine(prev_x, mid_y, resistor_x, mid_y)
                prev_x = resistor_x + 40  # skip resistor width

            # Connect last resistor to battery negative
            painter.drawLine(prev_x, mid_y, network_end_x, mid_y)
        else:
            # Parallel: place each resistor in parallel lines from top to bottom
            # We'll do a simplistic approach: draw them vertically
            top_y = mid_y - 70
            bot_y = mid_y + 70
            # Wire from network_start_x to top
            painter.drawLine(network_start_x, mid_y, network_start_x, top_y)
            # Wire from network_end_x to top
            painter.drawLine(network_end_x, mid_y, network_end_x, top_y)

            # Now distribute the resistors horizontally
            gap = (network_end_x - network_start_x) // (self.num_resistors + 1)
            for i in range(self.num_resistors):
                resistor_x = network_start_x + gap * (i + 1)
                resistor_y = top_y
                # Draw vertical resistor
                self._draw_resistor_vertical(painter, resistor_x - 10, resistor_y, 20, 50)
                # Connect wires
                # top to resistor top
                painter.drawLine(resistor_x, top_y, resistor_x, top_y + 50)
                # resistor bottom to bottom line
                painter.drawLine(resistor_x, top_y + 50, resistor_x, bot_y)

            # Finally connect top_y to bot_y on left
            painter.drawLine(network_start_x, top_y, network_start_x, bot_y)
            # and from network_end_x, top_y to bot_y
            painter.drawLine(network_end_x, top_y, network_end_x, bot_y)
            # close loop from left bottom to mid
            painter.drawLine(network_start_x, bot_y, network_start_x, mid_y)
            painter.drawLine(network_end_x, bot_y, network_end_x, mid_y)

        # Draw wire from the right end back to battery negative
        painter.drawLine(network_end_x, mid_y, network_end_x + 20, mid_y)
        painter.drawLine(network_end_x + 20, mid_y, battery_x, mid_y)

    def _draw_resistor(self, painter, x, y, w, h):
        """
        Draws a horizontal resistor rectangle at (x, y) with size (w, h).
        """
        painter.setBrush(QColor(192, 192, 192))
        painter.drawRect(int(x), int(y), int(w), int(h))

    def _draw_resistor_vertical(self, painter, x, y, w, h):
        """
        Draws a vertical resistor rectangle at (x, y) with size (w, h).
        """
        painter.setBrush(QColor(192, 192, 192))
        painter.drawRect(int(x), int(y), int(w), int(h))

    # ----------------------------
    # Reset & Export
    # ----------------------------
    def reset_simulation(self):
        logging.info("Resetting simulation to defaults.")
        self.voltage = self.default_voltage
        self.circuit_type = "Series"
        self.num_resistors = 2
        self.resistances = self.default_resistance[:self.num_resistors]

        self.spin_resistor_count.blockSignals(True)
        self.spin_resistor_count.setValue(self.num_resistors)
        self.spin_resistor_count.blockSignals(False)

        self.combo_type.blockSignals(True)
        self.combo_type.setCurrentText(self.circuit_type)
        self.combo_type.blockSignals(False)

        self.slider_voltage.blockSignals(True)
        self.slider_voltage.setValue(int(self.voltage))
        self.slider_voltage.blockSignals(False)
        self.lbl_voltage_val.setText(f"{self.voltage:.1f}")

        self._build_resistor_controls()
        self.data_log.clear()
        self._calculate_current()

    def export_data(self):
        """
        Exports the simulation data to a CSV file.
        """
        if not self.data_log:
            QMessageBox.information(self, "Export Data", "No data to export yet.")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Simulation Data", "", "CSV Files (*.csv)"
        )
        if not filename:
            return

        try:
            with open(filename, 'w') as file:
                file.write("Voltage (V),Resistances (Ohms),CircuitType,TotalR (Ohms),Current (A)\n")
                for entry in self.data_log:
                    voltage, resist_list, ctype, totR, curr = entry
                    resist_list_str = "/".join(f"{r:.1f}" for r in resist_list)
                    if math.isinf(curr):
                        curr_str = "∞"
                    else:
                        curr_str = f"{curr:.2f}"
                    if math.isinf(totR):
                        totr_str = "∞"
                    else:
                        totr_str = f"{totR:.2f}"
                    file.write(f"{voltage:.1f},{resist_list_str},{ctype},{totr_str},{curr_str}\n")

            QMessageBox.information(self, "Export Data", f"Data exported successfully to {filename}.")
            logging.info("Exported data to %s", filename)
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export data:\n{e}")
            logging.error("Export error: %s", e)

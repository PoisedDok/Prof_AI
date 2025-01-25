import math
from PyQt5.QtCore import QTimer, Qt, QRect
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSlider, QComboBox,
    QLineEdit, QPushButton
)
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont


class PendulumWidget(QWidget):
    """
    A 'game-like' pendulum simulation with controls for length, gravity, and damping.
    Real-time animation of a bob swinging.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initial physics variables
        self.angle = math.pi / 4  # initial angle (~45 degrees)
        self.angular_velocity = 0
        self.angular_acceleration = 0

        # Default adjustable parameters
        self.length = 200.0    # pendulum length in px
        self.gravity = 9.8     # gravitational acceleration
        self.damping = 0.995   # damping factor

        # Timer for real-time updates (~60 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_pendulum)
        self.timer.start(16)

        # Build the UI controls (sliders) for interactive variables
        self._init_ui()

    def _init_ui(self):
        # Create a layout for sliders
        self.layout_main = QVBoxLayout(self)
        self.layout_main.setContentsMargins(5, 5, 5, 5)

        # Gravity slider
        self.slider_gravity = QSlider(Qt.Horizontal)
        self.slider_gravity.setRange(1, 20)
        self.slider_gravity.setValue(int(self.gravity))
        self.slider_gravity.valueChanged.connect(self.on_gravity_change)

        # Length slider
        self.slider_length = QSlider(Qt.Horizontal)
        self.slider_length.setRange(50, 300)
        self.slider_length.setValue(int(self.length))
        self.slider_length.valueChanged.connect(self.on_length_change)

        # Damping slider
        self.slider_damping = QSlider(Qt.Horizontal)
        self.slider_damping.setRange(900, 999)  # represent 0.90 - 0.999
        self.slider_damping.setValue(int(self.damping * 1000))
        self.slider_damping.valueChanged.connect(self.on_damping_change)

        # Labels
        label_g = QLabel("Gravity")
        label_len = QLabel("Length")
        label_damp = QLabel("Damping")

        # Layout for controls
        layout_sliders = QHBoxLayout()
        layout_sliders.addWidget(label_g)
        layout_sliders.addWidget(self.slider_gravity)
        layout_sliders.addWidget(label_len)
        layout_sliders.addWidget(self.slider_length)
        layout_sliders.addWidget(label_damp)
        layout_sliders.addWidget(self.slider_damping)

        self.layout_main.addLayout(layout_sliders)

    def on_gravity_change(self, val):
        self.gravity = float(val)

    def on_length_change(self, val):
        self.length = float(val)

    def on_damping_change(self, val):
        self.damping = float(val) / 1000.0

    def update_pendulum(self):
        # Basic pendulum physics
        self.angular_acceleration = -(self.gravity / self.length) * math.sin(self.angle)
        self.angular_velocity += self.angular_acceleration
        self.angle += self.angular_velocity

        # Damping factor
        self.angular_velocity *= self.damping

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        width = self.width()
        height = self.height()

        # Pivot at top-center
        pivot_x = width // 2
        pivot_y = height // 4

        # Bob position
        bob_x = pivot_x + int(self.length * math.sin(self.angle))
        bob_y = pivot_y + int(self.length * math.cos(self.angle))

        # Draw rod
        pen = QPen(QColor(0, 0, 0), 2)
        painter.setPen(pen)
        painter.drawLine(pivot_x, pivot_y, bob_x, bob_y)

        # Draw pivot
        painter.setBrush(QColor(0, 0, 0))
        painter.drawEllipse(pivot_x - 3, pivot_y - 3, 6, 6)

        # Draw bob
        painter.setBrush(QColor(200, 0, 0))
        painter.drawEllipse(bob_x - 10, bob_y - 10, 20, 20)


class ProjectileMotionWidget(QWidget):
    """
    A 'game-like' projectile simulation with sliders for angle, initial speed, and gravity.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # Physics variables
        self.gravity = 9.8
        self.angle_deg = 45.0
        self.speed = 50.0
        self.time = 0.0
        self.dt = 0.016
        self.path = []

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_motion)
        self.timer.start(16)

        self._init_ui()

    def _init_ui(self):
        layout_main = QVBoxLayout(self)
        layout_main.setContentsMargins(5, 5, 5, 5)

        # Gravity slider
        label_g = QLabel("Gravity")
        self.slider_gravity = QSlider(Qt.Horizontal)
        self.slider_gravity.setRange(1, 20)
        self.slider_gravity.setValue(int(self.gravity))
        self.slider_gravity.valueChanged.connect(self.on_gravity_change)

        # Angle slider
        label_a = QLabel("Angle")
        self.slider_angle = QSlider(Qt.Horizontal)
        self.slider_angle.setRange(0, 90)
        self.slider_angle.setValue(int(self.angle_deg))
        self.slider_angle.valueChanged.connect(self.on_angle_change)

        # Speed slider
        label_s = QLabel("Speed")
        self.slider_speed = QSlider(Qt.Horizontal)
        self.slider_speed.setRange(10, 100)
        self.slider_speed.setValue(int(self.speed))
        self.slider_speed.valueChanged.connect(self.on_speed_change)

        row = QHBoxLayout()
        row.addWidget(label_g)
        row.addWidget(self.slider_gravity)
        row.addWidget(label_a)
        row.addWidget(self.slider_angle)
        row.addWidget(label_s)
        row.addWidget(self.slider_speed)

        layout_main.addLayout(row)

    def on_gravity_change(self, val):
        self.gravity = float(val)
        self.reset_motion()

    def on_angle_change(self, val):
        self.angle_deg = float(val)
        self.reset_motion()

    def on_speed_change(self, val):
        self.speed = float(val)
        self.reset_motion()

    def reset_motion(self):
        self.time = 0.0
        self.path.clear()

    def update_motion(self):
        self.time += self.dt
        # Basic equations
        angle_rad = math.radians(self.angle_deg)
        vx = self.speed * math.cos(angle_rad)
        vy = self.speed * math.sin(angle_rad) - self.gravity * self.time

        # position
        x = vx * self.time
        y = (self.speed * math.sin(angle_rad)) * self.time - 0.5 * self.gravity * (self.time**2)

        if y < 0.0:  # hit ground
            self.reset_motion()
        else:
            self.path.append((x, y))

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        ground_y = self.height() - 20  # simple ground line

        # ground line
        painter.setPen(QPen(QColor(0, 128, 0), 2))
        painter.drawLine(0, ground_y, self.width(), ground_y)

        # draw path
        painter.setPen(QPen(QColor(0, 0, 255), 2))
        for i in range(1, len(self.path)):
            x1, y1 = self.path[i-1]
            x2, y2 = self.path[i]
            painter.drawLine(int(x1), int(ground_y - y1), int(x2), int(ground_y - y2))

        # draw projectile
        if self.path:
            x, y = self.path[-1]
            painter.setBrush(QColor(255, 0, 0))
            painter.drawEllipse(int(x) - 5, int(ground_y - y) - 5, 10, 10)


class ElectricCircuitWidget(QWidget):
    """
    Game-like electric circuit sim with adjustable voltage, resistor1, resistor2.
    Displays current using ohm's law in real time.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.voltage = 9.0
        self.r1 = 100.0
        self.r2 = 100.0

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5,5,5,5)

        # row for voltage
        row_v = QHBoxLayout()
        label_v = QLabel("Voltage")
        self.slider_v = QSlider(Qt.Horizontal)
        self.slider_v.setRange(1, 20)
        self.slider_v.setValue(int(self.voltage))
        self.slider_v.valueChanged.connect(self.on_voltage_change)
        row_v.addWidget(label_v)
        row_v.addWidget(self.slider_v)
        layout.addLayout(row_v)

        # row for resistor1
        row_r1 = QHBoxLayout()
        label_r1 = QLabel("Resistor1")
        self.slider_r1 = QSlider(Qt.Horizontal)
        self.slider_r1.setRange(10, 1000)
        self.slider_r1.setValue(int(self.r1))
        self.slider_r1.valueChanged.connect(self.on_r1_change)
        row_r1.addWidget(label_r1)
        row_r1.addWidget(self.slider_r1)
        layout.addLayout(row_r1)

        # row for resistor2
        row_r2 = QHBoxLayout()
        label_r2 = QLabel("Resistor2")
        self.slider_r2 = QSlider(Qt.Horizontal)
        self.slider_r2.setRange(10, 1000)
        self.slider_r2.setValue(int(self.r2))
        self.slider_r2.valueChanged.connect(self.on_r2_change)
        row_r2.addWidget(label_r2)
        row_r2.addWidget(self.slider_r2)
        layout.addLayout(row_r2)

        self.label_current = QLabel("Current: 0.00 A")
        layout.addWidget(self.label_current)

        self.setLayout(layout)
        self.update()

    def on_voltage_change(self, val):
        self.voltage = float(val)
        self.update()

    def on_r1_change(self, val):
        self.r1 = float(val)
        self.update()

    def on_r2_change(self, val):
        self.r2 = float(val)
        self.update()

    def calc_current(self):
        total_r = self.r1 + self.r2
        if total_r == 0:
            return 0.0
        return self.voltage / total_r

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw circuit background
        painter.setBrush(QColor(230,230,255))
        painter.drawRect(self.rect())

        # Update current label
        current = self.calc_current()
        self.label_current.setText(f"Current: {current:.2f} A")

        # Some symbolic lines for a circuit
        painter.setPen(QPen(Qt.black, 3))
        mid_y = self.height() // 2
        margin = 50
        painter.drawLine(margin, mid_y, self.width() - margin, mid_y)

        # Battery
        painter.setBrush(QColor(255,255,0))
        painter.drawRect(margin - 20, mid_y - 20, 20, 40)

        # 2 Resistors
        x_r1 = (self.width() - margin - margin) // 3 + margin
        x_r2 = (self.width() - margin - margin) * 2 // 3 + margin
        painter.setBrush(QColor(192,192,192))
        painter.drawRect(x_r1 - 10, mid_y - 10, 20, 20)
        painter.drawRect(x_r2 - 10, mid_y - 10, 20, 20)


class StringTheoryWidget(QWidget):
    """
    Placeholder for 'string theory' game-like environment:
    Sliders controlling string tension, wave speed, etc.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.tension = 5.0
        self.wave_speed = 2.0
        self.time = 0.0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_string)
        self.timer.start(16)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        row = QHBoxLayout()

        label_ten = QLabel("Tension")
        self.slider_ten = QSlider(Qt.Horizontal)
        self.slider_ten.setRange(1, 20)
        self.slider_ten.setValue(int(self.tension))
        self.slider_ten.valueChanged.connect(self.on_tension_change)
        row.addWidget(label_ten)
        row.addWidget(self.slider_ten)

        label_ws = QLabel("Wave Speed")
        self.slider_ws = QSlider(Qt.Horizontal)
        self.slider_ws.setRange(1, 10)
        self.slider_ws.setValue(int(self.wave_speed))
        self.slider_ws.valueChanged.connect(self.on_ws_change)
        row.addWidget(label_ws)
        row.addWidget(self.slider_ws)

        layout.addLayout(row)
        self.setLayout(layout)

    def on_tension_change(self, val):
        self.tension = float(val)

    def on_ws_change(self, val):
        self.wave_speed = float(val)

    def update_string(self):
        self.time += 0.02
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw a "vibrating string" across the width
        mid_y = self.height() // 2
        amplitude = 30 + self.tension
        for x in range(0, self.width(), 5):
            y_offset = amplitude * math.sin(self.wave_speed * (x + self.time * 50) / 100.0)
            painter.drawPoint(x, mid_y + int(y_offset))


class ThermodynamicsWidget(QWidget):
    """
    A placeholder for thermodynamics game with sliders for Temperature, Volume, Pressure, etc.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.temperature = 300  # K
        self.volume = 1.0       # arbitrary volume units
        self.pressure = 1.0     # atm

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        row_temp = QHBoxLayout()
        label_temp = QLabel("Temperature (K)")
        self.slider_temp = QSlider(Qt.Horizontal)
        self.slider_temp.setRange(200, 600)
        self.slider_temp.setValue(int(self.temperature))
        self.slider_temp.valueChanged.connect(self.on_temp_change)
        row_temp.addWidget(label_temp)
        row_temp.addWidget(self.slider_temp)
        layout.addLayout(row_temp)

        row_vol = QHBoxLayout()
        label_vol = QLabel("Volume")
        self.slider_vol = QSlider(Qt.Horizontal)
        self.slider_vol.setRange(1, 10)
        self.slider_vol.setValue(int(self.volume))
        self.slider_vol.valueChanged.connect(self.on_vol_change)
        row_vol.addWidget(label_vol)
        row_vol.addWidget(self.slider_vol)
        layout.addLayout(row_vol)

        row_pres = QHBoxLayout()
        label_pres = QLabel("Pressure")
        self.slider_pres = QSlider(Qt.Horizontal)
        self.slider_pres.setRange(1, 20)
        self.slider_pres.setValue(int(self.pressure))
        self.slider_pres.valueChanged.connect(self.on_pres_change)
        row_pres.addWidget(label_pres)
        row_pres.addWidget(self.slider_pres)
        layout.addLayout(row_pres)

        self.desc_label = QLabel("Concept: PV = nRT (Placeholder).")
        layout.addWidget(self.desc_label)

        self.setLayout(layout)

    def on_temp_change(self, val):
        self.temperature = float(val)
        self.update()

    def on_vol_change(self, val):
        self.volume = float(val)
        self.update()

    def on_pres_change(self, val):
        self.pressure = float(val)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Visual representation
        text = f"Temp: {self.temperature} K, Vol: {self.volume}, Pressure: {self.pressure} atm"
        painter.drawText(self.rect(), Qt.AlignCenter, text)


class OpticsWidget(QWidget):
    """
    Lens simulation with focal length, object distance, lens type, etc.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.focal_length = 50
        self.object_distance = 100
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        row1 = QHBoxLayout()

        label_f = QLabel("Focal Length")
        self.slider_f = QSlider(Qt.Horizontal)
        self.slider_f.setRange(10, 100)
        self.slider_f.setValue(self.focal_length)
        self.slider_f.valueChanged.connect(self.on_f_change)
        row1.addWidget(label_f)
        row1.addWidget(self.slider_f)

        label_o = QLabel("Object Dist.")
        self.slider_o = QSlider(Qt.Horizontal)
        self.slider_o.setRange(10, 200)
        self.slider_o.setValue(self.object_distance)
        self.slider_o.valueChanged.connect(self.on_o_change)
        row1.addWidget(label_o)
        row1.addWidget(self.slider_o)

        layout.addLayout(row1)
        self.setLayout(layout)

    def on_f_change(self, val):
        self.focal_length = val
        self.update()

    def on_o_change(self, val):
        self.object_distance = val
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        # Draw lens in center
        painter.setBrush(QColor(173, 216, 230, 128))
        lens_w = 40
        lens_h = 200
        painter.drawEllipse(w//2 - lens_w//2, h//2 - lens_h//2, lens_w, lens_h)

        # Attempt to draw object and image lines (very simplified)
        object_x = w//2 - self.object_distance
        object_y = h//2
        painter.setPen(QPen(Qt.red, 2))
        painter.drawLine(object_x, object_y - 30, object_x, object_y + 30)  # object bar

        # Focal points
        fpt = self.focal_length
        painter.setPen(QPen(Qt.black, 1, Qt.DotLine))
        painter.drawLine(w//2 - fpt, 0, w//2 - fpt, h)
        painter.drawLine(w//2 + fpt, 0, w//2 + fpt, h)

        # Possibly compute image distance if lens formula
        # 1/f = 1/do + 1/di => di = (f*do)/(do - f)
        do = self.object_distance
        f = self.focal_length
        if (do != f):
            di = (f*do)/(do - f)
        else:
            di = 9999  # some large number if do==f

        image_x = w//2 + int(di)
        painter.setPen(QPen(Qt.blue, 2))
        painter.drawLine(image_x, object_y - 20, image_x, object_y + 20)  # image bar


class WaveWidget(QWidget):
    """
    Standing wave simulation with frequency, amplitude, etc.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.frequency = 1.0
        self.amplitude = 30
        self.phase = 0.0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_wave)
        self.timer.start(16)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        row = QHBoxLayout()

        label_f = QLabel("Frequency")
        self.slider_f = QSlider(Qt.Horizontal)
        self.slider_f.setRange(1, 10)
        self.slider_f.setValue(int(self.frequency))
        self.slider_f.valueChanged.connect(self.on_freq_change)
        row.addWidget(label_f)
        row.addWidget(self.slider_f)

        label_amp = QLabel("Amplitude")
        self.slider_amp = QSlider(Qt.Horizontal)
        self.slider_amp.setRange(10, 100)
        self.slider_amp.setValue(self.amplitude)
        self.slider_amp.valueChanged.connect(self.on_amp_change)
        row.addWidget(label_amp)
        row.addWidget(self.slider_amp)

        layout.addLayout(row)
        self.setLayout(layout)

    def on_freq_change(self, val):
        self.frequency = float(val)

    def on_amp_change(self, val):
        self.amplitude = int(val)

    def update_wave(self):
        self.phase += 0.1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        mid_y = self.height() // 2
        w = self.width()

        painter.setPen(QPen(Qt.blue, 2))
        for x in range(0, w, 2):
            y = self.amplitude * math.sin(self.frequency * (x * 0.02) + self.phase)
            painter.drawPoint(x, mid_y + int(y))


class GravityWidget(QWidget):
    """
    Gravity "orbits" simulation with sliders for planet mass, star mass, and radius.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0.0
        self.radius = 100
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_orbit)
        self.timer.start(16)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        row = QHBoxLayout()

        label_r = QLabel("Orbit Radius")
        self.slider_r = QSlider(Qt.Horizontal)
        self.slider_r.setRange(50, 200)
        self.slider_r.setValue(self.radius)
        self.slider_r.valueChanged.connect(self.on_radius_change)
        row.addWidget(label_r)
        row.addWidget(self.slider_r)

        layout.addLayout(row)
        self.setLayout(layout)

    def on_radius_change(self, val):
        self.radius = val

    def update_orbit(self):
        self.angle += 0.02
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        cx = self.width() // 2
        cy = self.height() // 2

        # Draw a star in the center
        painter.setBrush(QColor(255, 215, 0))  # golden star
        painter.drawEllipse(cx - 15, cy - 15, 30, 30)

        # Planet orbit
        px = cx + int(self.radius * math.cos(self.angle))
        py = cy + int(self.radius * math.sin(self.angle))

        painter.setBrush(QColor(0, 0, 255))
        painter.drawEllipse(px - 10, py - 10, 20, 20)


class MagneticFieldWidget(QWidget):
    """
    Magnetic field simulation with coil turns, current, etc.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current = 5.0
        self.turns = 10
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        row = QHBoxLayout()

        label_i = QLabel("Current (A)")
        self.slider_i = QSlider(Qt.Horizontal)
        self.slider_i.setRange(1, 20)
        self.slider_i.setValue(int(self.current))
        self.slider_i.valueChanged.connect(self.on_current_change)
        row.addWidget(label_i)
        row.addWidget(self.slider_i)

        label_t = QLabel("Turns")
        self.slider_t = QSlider(Qt.Horizontal)
        self.slider_t.setRange(1, 50)
        self.slider_t.setValue(self.turns)
        self.slider_t.valueChanged.connect(self.on_turns_change)
        row.addWidget(label_t)
        row.addWidget(self.slider_t)

        layout.addLayout(row)
        self.setLayout(layout)

    def on_current_change(self, val):
        self.current = float(val)
        self.update()

    def on_turns_change(self, val):
        self.turns = val
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Simple representation: coil with circles expanding to indicate field strength
        max_radius = min(self.width(), self.height()) // 2 - 10
        field_strength = self.current * self.turns
        step = max_radius // 5

        painter.setPen(QPen(Qt.green, 2))

        for i in range(1, 6):
            rad = i * step
            alpha = 30 + int(field_strength * i)  # dynamic alpha
            col = QColor(0, 255, 0, min(alpha, 255))
            painter.setPen(QPen(col, 2))
            painter.drawEllipse(self.width()//2 - rad, self.height()//2 - rad, rad*2, rad*2)

        painter.setPen(QPen(Qt.black, 1))
        painter.drawText(self.rect(), Qt.AlignCenter, f"Current: {self.current} A\nTurns: {self.turns}")


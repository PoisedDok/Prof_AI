from PyQt5.QtCore import QTimer


class BackgroundWaitFunction:
    def __init__(self, input_bar):
        self.input_bar = input_bar  # Pass the QLineEdit instance directly
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_placeholder)
        self.dots = ""
        self.max_dots = 3

    def start_waiting(self):
        """Start the 'Processing...' animation in the input bar."""
        self.dots = ""
        self.timer.start(500)  # Update dots every 500 ms
        self.input_bar.setPlaceholderText("Processing")

    def stop_waiting(self):
        """Stop the animation and reset to 'Type here'."""
        self.timer.stop()
        self.input_bar.setPlaceholderText("Type here")

    def update_placeholder(self):
        """Update the placeholder text with moving dots."""
        if len(self.dots) < self.max_dots:
            self.dots += "."
        else:
            self.dots = ""
        self.input_bar.setPlaceholderText(f"Processing{self.dots}")

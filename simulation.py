# simulation.py
import sys
import os
import importlib
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QMenuBar, QAction,
    QFileDialog, QMessageBox, QToolBar
)
from PyQt5.QtCore import Qt

class SimulationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Physics Simulations")
        self.setMinimumSize(1200, 800)

        # Setup the main tab widget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Dynamically load simulations
        self.load_simulations()

        # Create Menus and Toolbars
        self.create_menus_and_toolbars()

    def load_simulations(self):
        """
        Dynamically load all simulation modules from the simulations folder.
        Each simulation must have a class that inherits from QWidget and is named
        with the pattern <name>_sim.py containing a class <Name>Simulation.
        """
        simulations_path = os.path.join(os.path.dirname(__file__), "simulations")
        sys.path.insert(0, simulations_path)  # Add simulations folder to path

        for file in os.listdir(simulations_path):
            if file.endswith("_sim.py") and not file.startswith("__"):
                module_name = file[:-3]  # Strip .py
                try:
                    module = importlib.import_module(module_name)
                    # Assume class name is CamelCase of module name without '_sim'
                    class_name = ''.join(word.capitalize() for word in module_name.split('_')[:-1]) + "Simulation"
                    sim_class = getattr(module, class_name)
                    sim_instance = sim_class()
                    self.tab_widget.addTab(sim_instance, class_name.replace("Simulation", ""))
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to load {module_name}: {e}")

        sys.path.pop(0)  # Clean up path

    def create_menus_and_toolbars(self):
        """
        Creates a menu bar and toolbars for additional functionalities like exporting data,
        saving/loading settings, etc.
        """
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Simulation Menu
        sim_menu = menubar.addMenu("Simulations")
        export_action = QAction("Export Current Simulation Data", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_current_simulation_data)
        sim_menu.addAction(export_action)

        # Toolbar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(Qt.TopToolBarArea, toolbar)
        toolbar.addAction(exit_action)
        toolbar.addAction(export_action)

    def export_current_simulation_data(self):
        """
        Trigger export on the current simulation tab.
        """
        current_widget = self.tab_widget.currentWidget()
        if hasattr(current_widget, "export_data"):
            current_widget.export_data()
        else:
            QMessageBox.information(self, "Export Data", "This simulation does not support data export.")

def main():
    app = QApplication(sys.argv)
    window = SimulationApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

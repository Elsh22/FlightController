"""
Rocket Flight Controller - 3D OpenGL Version with Data Logging
"""
import sys
from PyQt6.QtWidgets import QApplication
from src.gui.main_window_spacex_3d import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("VCU Rocket Flight Controller - 3D + Logging")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

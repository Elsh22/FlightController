"""
Main Window for Rocket Flight Controller GUI
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QLabel, QComboBox, QGroupBox, QGridLayout)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont
import pyqtgraph as pg
from src.communication.serial_handler import SerialHandler
from src.gui.orientation_widget import OrientationWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rocket Flight Controller - Telemetry Display")
        self.setGeometry(100, 100, 1400, 800)
        
        # Serial handler
        self.serial_handler = SerialHandler()
        
        # Data storage
        self.time_data = []
        self.roll_data = []
        self.pitch_data = []
        self.yaw_data = []
        self.altitude_data = []
        
        # Setup UI
        self.setup_ui()
        
        # Update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        
    def setup_ui(self):
        """Setup the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Top control panel
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)
        
        # Middle section - graphs and orientation
        middle_layout = QHBoxLayout()
        
        # Left side - Real-time plots
        plot_layout = QVBoxLayout()
        
        # Orientation plot (Roll, Pitch, Yaw)
        self.orientation_plot = pg.PlotWidget(title="Orientation (deg)")
        self.orientation_plot.setLabel('left', 'Angle', units='deg')
        self.orientation_plot.setLabel('bottom', 'Time', units='s')
        self.orientation_plot.addLegend()
        self.orientation_plot.showGrid(x=True, y=True)
        
        self.roll_curve = self.orientation_plot.plot(pen=pg.mkPen('r', width=2), name='Roll')
        self.pitch_curve = self.orientation_plot.plot(pen=pg.mkPen('g', width=2), name='Pitch')
        self.yaw_curve = self.orientation_plot.plot(pen=pg.mkPen('b', width=2), name='Yaw')
        
        plot_layout.addWidget(self.orientation_plot)
        
        # Altitude plot
        self.altitude_plot = pg.PlotWidget(title="Altitude (m)")
        self.altitude_plot.setLabel('left', 'Altitude', units='m')
        self.altitude_plot.setLabel('bottom', 'Time', units='s')
        self.altitude_plot.showGrid(x=True, y=True)
        self.altitude_curve = self.altitude_plot.plot(pen=pg.mkPen('c', width=2))
        
        plot_layout.addWidget(self.altitude_plot)
        
        middle_layout.addLayout(plot_layout, 2)
        
        # Right side - 3D orientation visualization
        orientation_group = QGroupBox("Rocket Orientation")
        orientation_layout = QVBoxLayout()
        
        self.orientation_widget = OrientationWidget()
        orientation_layout.addWidget(self.orientation_widget)
        
        # Current values display
        values_layout = QGridLayout()
        
        self.roll_label = QLabel("Roll: 0.0°")
        self.pitch_label = QLabel("Pitch: 0.0°")
        self.yaw_label = QLabel("Yaw: 0.0°")
        self.altitude_label = QLabel("Altitude: 0.0 m")
        
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        
        for label in [self.roll_label, self.pitch_label, self.yaw_label, self.altitude_label]:
            label.setFont(font)
        
        values_layout.addWidget(QLabel("Current Values:"), 0, 0, 1, 2)
        values_layout.addWidget(self.roll_label, 1, 0)
        values_layout.addWidget(self.pitch_label, 1, 1)
        values_layout.addWidget(self.yaw_label, 2, 0)
        values_layout.addWidget(self.altitude_label, 2, 1)
        
        orientation_layout.addLayout(values_layout)
        orientation_group.setLayout(orientation_layout)
        
        middle_layout.addWidget(orientation_group, 1)
        
        main_layout.addLayout(middle_layout)
        
    def create_control_panel(self):
        """Create the top control panel"""
        control_group = QGroupBox("Connection Control")
        layout = QHBoxLayout()
        
        # COM port selection
        layout.addWidget(QLabel("COM Port:"))
        self.port_combo = QComboBox()
        self.port_combo.addItems(self.serial_handler.get_available_ports())
        layout.addWidget(self.port_combo)
        
        # Refresh ports button
        self.refresh_btn = QPushButton("Refresh Ports")
        self.refresh_btn.clicked.connect(self.refresh_ports)
        layout.addWidget(self.refresh_btn)
        
        # Connect button
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.toggle_connection)
        layout.addWidget(self.connect_btn)
        
        # Clear data button
        self.clear_btn = QPushButton("Clear Data")
        self.clear_btn.clicked.connect(self.clear_data)
        layout.addWidget(self.clear_btn)
        
        # Connection status
        self.status_label = QLabel("Status: Disconnected")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        control_group.setLayout(layout)
        return control_group
    
    def refresh_ports(self):
        """Refresh available COM ports"""
        self.port_combo.clear()
        self.port_combo.addItems(self.serial_handler.get_available_ports())
    
    def toggle_connection(self):
        """Connect or disconnect from serial port"""
        if not self.serial_handler.is_connected:
            port = self.port_combo.currentText()
            if self.serial_handler.connect(port):
                self.connect_btn.setText("Disconnect")
                self.status_label.setText("Status: Connected")
                self.status_label.setStyleSheet("color: green; font-weight: bold;")
                self.timer.start(50)  # Update every 50ms
            else:
                self.status_label.setText("Status: Connection Failed")
                self.status_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.serial_handler.disconnect()
            self.connect_btn.setText("Connect")
            self.status_label.setText("Status: Disconnected")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            self.timer.stop()
    
    def update_data(self):
        """Update plots with new data from serial"""
        data = self.serial_handler.read_data()
        
        if data:
            # Check if this is telemetry data (not a status message)
            if all(key in data for key in ['roll', 'pitch', 'yaw', 'altitude']):
                # Append new data
                self.time_data.append(data['time'])
                self.roll_data.append(data['roll'])
                self.pitch_data.append(data['pitch'])
                self.yaw_data.append(data['yaw'])
                self.altitude_data.append(data['altitude'])
                
                # Keep only last 500 points for performance
                max_points = 500
                if len(self.time_data) > max_points:
                    self.time_data = self.time_data[-max_points:]
                    self.roll_data = self.roll_data[-max_points:]
                    self.pitch_data = self.pitch_data[-max_points:]
                    self.yaw_data = self.yaw_data[-max_points:]
                    self.altitude_data = self.altitude_data[-max_points:]
                
                # Update plots
                self.roll_curve.setData(self.time_data, self.roll_data)
                self.pitch_curve.setData(self.time_data, self.pitch_data)
                self.yaw_curve.setData(self.time_data, self.yaw_data)
                self.altitude_curve.setData(self.time_data, self.altitude_data)
                
                # Update orientation visualization
                self.orientation_widget.update_orientation(
                    data['roll'], data['pitch'], data['yaw']
                )
                
                # Update labels
                self.roll_label.setText(f"Roll: {data['roll']:.1f}°")
                self.pitch_label.setText(f"Pitch: {data['pitch']:.1f}°")
                self.yaw_label.setText(f"Yaw: {data['yaw']:.1f}°")
                self.altitude_label.setText(f"Altitude: {data['altitude']:.1f} m")
            elif 'status' in data:
                # Handle status messages (optional: print to console)
                print(f"Arduino status: {data['status']}")
            elif 'error' in data:
                # Handle error messages
                print(f"Arduino error: {data['error']}")
    
    def clear_data(self):
        """Clear all plotted data"""
        self.time_data.clear()
        self.roll_data.clear()
        self.pitch_data.clear()
        self.yaw_data.clear()
        self.altitude_data.clear()
        
        self.roll_curve.setData([], [])
        self.pitch_curve.setData([], [])
        self.yaw_curve.setData([], [])
        self.altitude_curve.setData([], [])
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.serial_handler.is_connected:
            self.serial_handler.disconnect()
        event.accept()
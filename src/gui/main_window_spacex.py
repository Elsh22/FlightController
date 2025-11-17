"""
SpaceX-Inspired GUI with True 3D Rocket and Data Logging
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QLabel, QComboBox, QGroupBox, QGridLayout,
                              QCheckBox, QMessageBox)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont
import pyqtgraph as pg
from src.communication.serial_handler import SerialHandler
from src.gui.rocket_orientation_widget_3d import Rocket3DWidget
from src.data.data_logger import DataLogger


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 VCU Rocket Flight Controller - 3D Visualization + Data Logging")
        self.setGeometry(50, 50, 1800, 900)
        
        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1a2e; }
            QGroupBox { 
                color: #eee; 
                border: 2px solid #16213e;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLabel { color: #eee; }
            QPushButton {
                background-color: #0f3460;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #16213e;
            }
            QComboBox, QCheckBox {
                background-color: #0f3460;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 4px;
            }
        """)
        
        self.serial_handler = SerialHandler()
        self.data_logger = DataLogger()
        
        # Data storage
        self.time_data = []
        self.roll_data = []
        self.pitch_data = []
        self.yaw_data = []
        self.altitude_data = []
        self.velocity_data = []
        
        self.setup_ui()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Control panel
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)
        
        # Middle section
        middle_layout = QHBoxLayout()
        
        # Left - Plots
        plot_layout = QVBoxLayout()
        
        # Orientation plot
        self.orientation_plot = pg.PlotWidget(title="<span style='color: #eee'>ORIENTATION</span>")
        self.orientation_plot.setBackground('#16213e')
        self.orientation_plot.setLabel('left', 'Angle', units='deg', color='#eee')
        self.orientation_plot.setLabel('bottom', 'Time', units='s', color='#eee')
        self.orientation_plot.addLegend()
        self.orientation_plot.showGrid(x=True, y=True, alpha=0.3)
        
        self.roll_curve = self.orientation_plot.plot(pen=pg.mkPen('#ff3333', width=2), name='Roll')
        self.pitch_curve = self.orientation_plot.plot(pen=pg.mkPen('#33ff33', width=2), name='Pitch')
        self.yaw_curve = self.orientation_plot.plot(pen=pg.mkPen('#3333ff', width=2), name='Yaw')
        
        plot_layout.addWidget(self.orientation_plot)
        
        # Altitude plot
        self.altitude_plot = pg.PlotWidget(title="<span style='color: #eee'>ALTITUDE & VELOCITY</span>")
        self.altitude_plot.setBackground('#16213e')
        self.altitude_plot.setLabel('left', 'Altitude', units='m', color='#eee')
        self.altitude_plot.setLabel('bottom', 'Time', units='s', color='#eee')
        self.altitude_plot.addLegend()
        self.altitude_plot.showGrid(x=True, y=True, alpha=0.3)
        
        self.velocity_axis = pg.ViewBox()
        self.altitude_plot.scene().addItem(self.velocity_axis)
        self.altitude_plot.getAxis('right').linkToView(self.velocity_axis)
        self.velocity_axis.setXLink(self.altitude_plot)
        self.altitude_plot.getAxis('right').setLabel('Velocity', units='m/s', color='#eee')
        self.altitude_plot.showAxis('right')
        
        self.altitude_curve = pg.PlotCurveItem(pen=pg.mkPen('#33ffff', width=2), name='Altitude')
        self.altitude_plot.addItem(self.altitude_curve)
        
        self.velocity_curve = pg.PlotCurveItem(pen=pg.mkPen('#ffff33', width=2), name='Velocity')
        self.velocity_axis.addItem(self.velocity_curve)
        
        def updateViews():
            self.velocity_axis.setGeometry(self.altitude_plot.getViewBox().sceneBoundingRect())
            self.velocity_axis.linkedViewChanged(self.altitude_plot.getViewBox(), self.velocity_axis.XAxis)
        
        updateViews()
        self.altitude_plot.getViewBox().sigResized.connect(updateViews)
        
        plot_layout.addWidget(self.altitude_plot)
        middle_layout.addLayout(plot_layout, 2)
        
        # Right - 3D Rocket
        right_layout = QVBoxLayout()
        
        orientation_group = QGroupBox("🚀 3D VEHICLE VISUALIZATION")
        orientation_layout = QVBoxLayout()
        
        self.rocket_widget = Rocket3DWidget()
        orientation_layout.addWidget(self.rocket_widget)
        
        # Camera controls hint
        hint_label = QLabel("🖱️ Drag to rotate | Scroll to zoom")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint_label.setStyleSheet("color: #888; font-size: 10px;")
        orientation_layout.addWidget(hint_label)
        
        orientation_group.setLayout(orientation_layout)
        right_layout.addWidget(orientation_group)
        
        # Telemetry values
        telemetry_group = QGroupBox("📊 TELEMETRY")
        telemetry_layout = QGridLayout()
        
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        
        self.roll_label = QLabel("Roll: 0.0°")
        self.pitch_label = QLabel("Pitch: 0.0°")
        self.yaw_label = QLabel("Yaw: 0.0°")
        self.altitude_label = QLabel("Altitude: 0.0 m")
        self.velocity_label = QLabel("Velocity: 0.0 m/s")
        
        for label in [self.roll_label, self.pitch_label, self.yaw_label, 
                     self.altitude_label, self.velocity_label]:
            label.setFont(font)
            label.setStyleSheet("color: #33ffff;")
        
        telemetry_layout.addWidget(self.roll_label, 0, 0)
        telemetry_layout.addWidget(self.pitch_label, 0, 1)
        telemetry_layout.addWidget(self.yaw_label, 1, 0)
        telemetry_layout.addWidget(self.altitude_label, 1, 1)
        telemetry_layout.addWidget(self.velocity_label, 2, 0, 1, 2)
        
        telemetry_group.setLayout(telemetry_layout)
        right_layout.addWidget(telemetry_group)
        
        # Sensor health
        health_group = QGroupBox("🔧 SENSOR HEALTH")
        health_layout = QGridLayout()
        
        self.bno_status = QLabel("BNO055: UNKNOWN")
        self.adxl1_status = QLabel("ADXL345 #1: UNKNOWN")
        self.adxl2_status = QLabel("ADXL345 #2: UNKNOWN")
        self.bmp_status = QLabel("BMP390: UNKNOWN")
        
        for label in [self.bno_status, self.adxl1_status, self.adxl2_status, self.bmp_status]:
            label.setFont(font)
        
        health_layout.addWidget(self.bno_status, 0, 0)
        health_layout.addWidget(self.adxl1_status, 1, 0)
        health_layout.addWidget(self.adxl2_status, 2, 0)
        health_layout.addWidget(self.bmp_status, 3, 0)
        
        health_group.setLayout(health_layout)
        right_layout.addWidget(health_group)
        
        middle_layout.addLayout(right_layout, 1)
        main_layout.addLayout(middle_layout)
        
    def create_control_panel(self):
        control_group = QGroupBox("🔌 CONNECTION & DATA LOGGING")
        layout = QHBoxLayout()
        
        # Connection controls
        layout.addWidget(QLabel("COM Port:"))
        self.port_combo = QComboBox()
        self.port_combo.addItems(self.serial_handler.get_available_ports())
        layout.addWidget(self.port_combo)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_ports)
        layout.addWidget(self.refresh_btn)
        
        self.connect_btn = QPushButton("⚡ Connect")
        self.connect_btn.clicked.connect(self.toggle_connection)
        layout.addWidget(self.connect_btn)
        
        # Data logging controls
        layout.addWidget(QLabel(" | "))
        
        self.log_checkbox = QCheckBox("📝 Auto-log data")
        self.log_checkbox.setChecked(True)
        layout.addWidget(self.log_checkbox)
        
        self.log_btn = QPushButton("💾 Start Logging")
        self.log_btn.clicked.connect(self.toggle_logging)
        layout.addWidget(self.log_btn)
        
        self.clear_btn = QPushButton("🗑️ Clear Data")
        self.clear_btn.clicked.connect(self.clear_data)
        layout.addWidget(self.clear_btn)
        
        # Status
        self.status_label = QLabel("Status: DISCONNECTED")
        self.status_label.setStyleSheet("color: #ff3333; font-weight: bold; font-size: 14px;")
        layout.addWidget(self.status_label)
        
        self.log_status_label = QLabel("Log: OFF")
        self.log_status_label.setStyleSheet("color: #888; font-weight: bold; font-size: 14px;")
        layout.addWidget(self.log_status_label)
        
        layout.addStretch()
        
        control_group.setLayout(layout)
        return control_group
    
    def refresh_ports(self):
        self.port_combo.clear()
        self.port_combo.addItems(self.serial_handler.get_available_ports())
    
    def toggle_connection(self):
        if not self.serial_handler.is_connected:
            port = self.port_combo.currentText()
            if self.serial_handler.connect(port):
                self.connect_btn.setText("⚡ Disconnect")
                self.status_label.setText("Status: CONNECTED")
                self.status_label.setStyleSheet("color: #33ff33; font-weight: bold; font-size: 14px;")
                self.timer.start(50)
                
                # Auto-start logging if enabled
                if self.log_checkbox.isChecked() and not self.data_logger.is_logging:
                    self.data_logger.start_logging()
                    self.log_btn.setText("💾 Stop Logging")
                    self.log_status_label.setText("Log: RECORDING")
                    self.log_status_label.setStyleSheet("color: #ff3333; font-weight: bold; font-size: 14px;")
            else:
                self.status_label.setText("Status: CONNECTION FAILED")
                self.status_label.setStyleSheet("color: #ff3333; font-weight: bold; font-size: 14px;")
        else:
            self.serial_handler.disconnect()
            self.connect_btn.setText("⚡ Connect")
            self.status_label.setText("Status: DISCONNECTED")
            self.status_label.setStyleSheet("color: #ff3333; font-weight: bold; font-size: 14px;")
            self.timer.stop()
            
            # Auto-stop logging
            if self.data_logger.is_logging:
                self.data_logger.stop_logging()
                self.log_btn.setText("💾 Start Logging")
                self.log_status_label.setText("Log: STOPPED")
                self.log_status_label.setStyleSheet("color: #888; font-weight: bold; font-size: 14px;")
                self.show_log_stats()
    
    def toggle_logging(self):
        if not self.data_logger.is_logging:
            self.data_logger.start_logging()
            self.log_btn.setText("💾 Stop Logging")
            self.log_status_label.setText("Log: RECORDING")
            self.log_status_label.setStyleSheet("color: #ff3333; font-weight: bold; font-size: 14px;")
        else:
            self.data_logger.stop_logging()
            self.log_btn.setText("💾 Start Logging")
            self.log_status_label.setText("Log: STOPPED")
            self.log_status_label.setStyleSheet("color: #888; font-weight: bold; font-size: 14px;")
            self.show_log_stats()
    
    def show_log_stats(self):
        stats = self.data_logger.get_stats()
        if stats:
            msg = f"""
Logging Statistics:

📊 Total Samples: {stats['samples']}
⏱️ Duration: {stats['duration']:.1f} seconds
📏 Max Altitude: {stats['max_altitude']:.2f} m
🔄 Max Roll: {stats['max_roll']:.1f}°
⬆️ Max Pitch: {stats['max_pitch']:.1f}°

Files saved in 'logs/' directory
            """
            QMessageBox.information(self, "Logging Complete", msg)
    
    def update_data(self):
        data = self.serial_handler.read_data()
        
        if data:
            if all(key in data for key in ['roll', 'pitch', 'yaw', 'altitude']):
                # Log data if logging is active
                if self.data_logger.is_logging:
                    self.data_logger.log_data(data.copy())
                
                # Update storage
                self.time_data.append(data['time'])
                self.roll_data.append(data['roll'])
                self.pitch_data.append(data['pitch'])
                self.yaw_data.append(data['yaw'])
                self.altitude_data.append(data['altitude'])
                
                if 'velocity' in data:
                    self.velocity_data.append(data['velocity'])
                else:
                    self.velocity_data.append(0)
                
                # Limit buffer size
                max_points = 500
                if len(self.time_data) > max_points:
                    self.time_data = self.time_data[-max_points:]
                    self.roll_data = self.roll_data[-max_points:]
                    self.pitch_data = self.pitch_data[-max_points:]
                    self.yaw_data = self.yaw_data[-max_points:]
                    self.altitude_data = self.altitude_data[-max_points:]
                    self.velocity_data = self.velocity_data[-max_points:]
                
                # Update plots
                self.roll_curve.setData(self.time_data, self.roll_data)
                self.pitch_curve.setData(self.time_data, self.pitch_data)
                self.yaw_curve.setData(self.time_data, self.yaw_data)
                self.altitude_curve.setData(self.time_data, self.altitude_data)
                self.velocity_curve.setData(self.time_data, self.velocity_data)
                
                # Update 3D rocket
                self.rocket_widget.update_orientation(
                    data['roll'], 
                    data['pitch'], 
                    data['yaw'],
                    data['altitude']
                )
                
                # Update labels
                self.roll_label.setText(f"Roll: {data['roll']:.1f}°")
                self.pitch_label.setText(f"Pitch: {data['pitch']:.1f}°")
                self.yaw_label.setText(f"Yaw: {data['yaw']:.1f}°")
                self.altitude_label.setText(f"Altitude: {data['altitude']:.1f} m")
                
                if 'velocity' in data:
                    self.velocity_label.setText(f"Velocity: {data['velocity']:.2f} m/s")
                
                self.update_sensor_health(data)
    
    def update_sensor_health(self, data):
        if 'bno_status' in data:
            status = data['bno_status']
            color = "#33ff33" if status == "OK" else "#ff3333"
            self.bno_status.setText(f"BNO055: {status}")
            self.bno_status.setStyleSheet(f"color: {color}; font-weight: bold;")
        
        if 'adxl1_status' in data:
            status = data['adxl1_status']
            color = "#33ff33" if status == "OK" else "#ff3333"
            self.adxl1_status.setText(f"ADXL345 #1: {status}")
            self.adxl1_status.setStyleSheet(f"color: {color}; font-weight: bold;")
        
        if 'adxl2_status' in data:
            status = data['adxl2_status']
            color = "#33ff33" if status == "OK" else "#ff3333"
            self.adxl2_status.setText(f"ADXL345 #2: {status}")
            self.adxl2_status.setStyleSheet(f"color: {color}; font-weight: bold;")
        
        if 'bmp_status' in data:
            status = data['bmp_status']
            color = "#33ff33" if status == "OK" else "#ff3333"
            self.bmp_status.setText(f"BMP390: {status}")
            self.bmp_status.setStyleSheet(f"color: {color}; font-weight: bold;")
    
    def clear_data(self):
        self.time_data.clear()
        self.roll_data.clear()
        self.pitch_data.clear()
        self.yaw_data.clear()
        self.altitude_data.clear()
        self.velocity_data.clear()
        
        self.roll_curve.setData([], [])
        self.pitch_curve.setData([], [])
        self.yaw_curve.setData([], [])
        self.altitude_curve.setData([], [])
        self.velocity_curve.setData([], [])
    
    def closeEvent(self, event):
        if self.serial_handler.is_connected:
            self.serial_handler.disconnect()
        if self.data_logger.is_logging:
            self.data_logger.stop_logging()
        event.accept()
"""
Serial Communication Handler for receiving telemetry data from Arduino
"""
import serial
import serial.tools.list_ports
import time
import json


class SerialHandler:
    def __init__(self, baudrate=115200, timeout=0.1):
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_port = None
        self.is_connected = False
        self.start_time = None
        
    def get_available_ports(self):
        """Get list of available COM ports"""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    
    def connect(self, port):
        """Connect to specified COM port"""
        try:
            self.serial_port = serial.Serial(
                port=port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            self.is_connected = True
            self.start_time = time.time()
            time.sleep(2)  # Wait for Arduino to reset
            print(f"Connected to {port}")
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Disconnect from COM port"""
        if self.serial_port and self.is_connected:
            self.serial_port.close()
            self.is_connected = False
            print("Disconnected")
    
    def read_data(self):
        """Read and parse data from serial port"""
        if not self.is_connected or not self.serial_port:
            return None
        
        try:
            if self.serial_port.in_waiting > 0:
                line = self.serial_port.readline().decode('utf-8').strip()
                
                # Try to parse JSON data
                if line.startswith('{') and line.endswith('}'):
                    data = json.loads(line)
                    
                    # Calculate elapsed time
                    data['time'] = time.time() - self.start_time
                    
                    return data
                
        except Exception as e:
            print(f"Read error: {e}")
            return None
        
        return None
    
    def write_data(self, data):
        """Send data to Arduino"""
        if self.is_connected and self.serial_port:
            try:
                self.serial_port.write(data.encode('utf-8'))
                return True
            except Exception as e:
                print(f"Write error: {e}")
                return False
        return False
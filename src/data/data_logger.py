"""
Data logging for telemetry
Supports CSV and JSON formats
"""
import csv
import json
from datetime import datetime
from pathlib import Path


class DataLogger:
    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.csv_filename = self.log_dir / f"telemetry_{timestamp}.csv"
        self.json_filename = self.log_dir / f"telemetry_{timestamp}.json"
        
        self.csv_file = None
        self.csv_writer = None
        self.json_data = []
        
        self.is_logging = False
        
    def start_logging(self):
        """Start logging to CSV and JSON"""
        if self.is_logging:
            return
        
        # Open CSV file
        self.csv_file = open(self.csv_filename, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        
        # Write CSV header
        self.csv_writer.writerow([
            'timestamp',
            'time_seconds',
            'roll',
            'pitch',
            'yaw',
            'altitude',
            'velocity',
            'bno_status',
            'adxl1_status',
            'adxl2_status',
            'bmp_status',
            'bno_ax',
            'bno_ay',
            'bno_az'
        ])
        
        self.is_logging = True
        print(f"✅ Data logging started:")
        print(f"   CSV: {self.csv_filename}")
        print(f"   JSON: {self.json_filename}")
        
    def log_data(self, data):
        """Log a data point"""
        if not self.is_logging:
            return
        
        try:
            # Add timestamp
            data['timestamp'] = datetime.now().isoformat()
            
            # Write to CSV
            self.csv_writer.writerow([
                data.get('timestamp', ''),
                data.get('time', 0.0),
                data.get('roll', 0.0),
                data.get('pitch', 0.0),
                data.get('yaw', 0.0),
                data.get('altitude', 0.0),
                data.get('velocity', 0.0),
                data.get('bno_status', 'UNKNOWN'),
                data.get('adxl1_status', 'UNKNOWN'),
                data.get('adxl2_status', 'UNKNOWN'),
                data.get('bmp_status', 'UNKNOWN'),
                data.get('bno_ax', 0.0),
                data.get('bno_ay', 0.0),
                data.get('bno_az', 0.0)
            ])
            
            # Add to JSON buffer
            self.json_data.append(data)
            
            # Flush CSV periodically
            if len(self.json_data) % 100 == 0:
                self.csv_file.flush()
                
        except Exception as e:
            print(f"❌ Logging error: {e}")
    
    def stop_logging(self):
        """Stop logging and save JSON"""
        if not self.is_logging:
            return
        
        # Close CSV
        if self.csv_file:
            self.csv_file.close()
            
        # Save JSON
        try:
            with open(self.json_filename, 'w') as f:
                json.dump({
                    'metadata': {
                        'start_time': self.json_data[0]['timestamp'] if self.json_data else None,
                        'end_time': self.json_data[-1]['timestamp'] if self.json_data else None,
                        'total_samples': len(self.json_data)
                    },
                    'data': self.json_data
                }, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving JSON: {e}")
        
        self.is_logging = False
        print(f"✅ Data logging stopped. Saved {len(self.json_data)} samples.")
        
    def get_stats(self):
        """Get logging statistics"""
        if not self.json_data:
            return None
        
        rolls = [d.get('roll', 0) for d in self.json_data]
        pitches = [d.get('pitch', 0) for d in self.json_data]
        altitudes = [d.get('altitude', 0) for d in self.json_data]
        
        return {
            'samples': len(self.json_data),
            'duration': self.json_data[-1]['time'] - self.json_data[0]['time'] if len(self.json_data) > 1 else 0,
            'max_altitude': max(altitudes) if altitudes else 0,
            'max_roll': max(rolls) if rolls else 0,
            'max_pitch': max(pitches) if pitches else 0,
        }
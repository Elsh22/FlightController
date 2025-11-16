"""
3D Orientation Widget for visualizing rocket orientation
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QPolygon, QBrush
from PyQt6.QtCore import QPoint
import math


class OrientationWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 400)
        
        # Current orientation (in degrees)
        self.roll = 0
        self.pitch = 0
        self.yaw = 0
        
    def update_orientation(self, roll, pitch, yaw):
        """Update the orientation angles"""
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw
        self.update()  # Trigger repaint
    
    def paintEvent(self, event):
        """Draw the rocket orientation visualization"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get widget dimensions
        width = self.width()
        height = self.height()
        center_x = width // 2
        center_y = height // 2
        
        # Draw background
        painter.fillRect(0, 0, width, height, QColor(20, 20, 30))
        
        # Draw horizon line (pitch indicator)
        self.draw_horizon(painter, center_x, center_y)
        
        # Draw rocket body (roll indicator)
        self.draw_rocket(painter, center_x, center_y)
        
        # Draw yaw indicator (compass)
        self.draw_compass(painter, width - 100, 80)
        
        # Draw angle text
        self.draw_angle_text(painter)
        
    def draw_horizon(self, painter, center_x, center_y):
        """Draw artificial horizon showing pitch"""
        # Pitch offset (pixels per degree)
        pitch_scale = 3
        pitch_offset = int(self.pitch * pitch_scale)
        
        # Sky (blue)
        painter.setBrush(QBrush(QColor(135, 206, 235)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(0, 0, self.width(), center_y - pitch_offset)
        
        # Ground (brown)
        painter.setBrush(QBrush(QColor(139, 90, 43)))
        painter.drawRect(0, center_y - pitch_offset, self.width(), self.height())
        
        # Horizon line
        painter.setPen(QPen(QColor(255, 255, 255), 3))
        painter.drawLine(0, center_y - pitch_offset, self.width(), center_y - pitch_offset)
        
        # Pitch ladder
        self.draw_pitch_ladder(painter, center_x, center_y, pitch_offset)
        
    def draw_pitch_ladder(self, painter, center_x, center_y, pitch_offset):
        """Draw pitch ladder marks"""
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        pitch_scale = 3
        
        # Draw ladder lines every 10 degrees
        for angle in range(-90, 100, 10):
            if angle == 0:
                continue
            
            y_pos = center_y - pitch_offset - int(angle * pitch_scale)
            
            if 0 <= y_pos <= self.height():
                line_length = 40 if angle % 20 == 0 else 20
                painter.drawLine(center_x - line_length, y_pos, 
                               center_x + line_length, y_pos)
                
                # Draw angle text
                painter.drawText(center_x + line_length + 5, y_pos + 5, f"{angle}°")
    
    def draw_rocket(self, painter, center_x, center_y):
        """Draw rocket body with roll indication"""
        # Save painter state
        painter.save()
        
        # Translate to center and rotate by roll angle
        painter.translate(center_x, center_y)
        painter.rotate(self.roll)
        
        # Draw center reference aircraft symbol
        painter.setPen(QPen(QColor(255, 255, 0), 4))
        
        # Center dot
        painter.setBrush(QBrush(QColor(255, 255, 0)))
        painter.drawEllipse(QPoint(0, 0), 8, 8)
        
        # Left wing
        painter.drawLine(-80, 0, -20, 0)
        painter.drawLine(-80, 0, -70, -10)
        
        # Right wing
        painter.drawLine(20, 0, 80, 0)
        painter.drawLine(80, 0, 70, -10)
        
        # Nose indicator
        painter.setBrush(QBrush(QColor(255, 0, 0)))
        points = [
            QPoint(0, -20),
            QPoint(-10, 0),
            QPoint(10, 0)
        ]
        painter.drawPolygon(QPolygon(points))
        
        # Restore painter state
        painter.restore()
    
    def draw_compass(self, painter, center_x, center_y):
        """Draw compass rose showing yaw"""
        radius = 60
        
        # Save painter state
        painter.save()
        
        # Draw compass circle
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setBrush(QBrush(QColor(50, 50, 70, 200)))
        painter.drawEllipse(QPoint(center_x, center_y), radius, radius)
        
        # Draw cardinal directions
        painter.translate(center_x, center_y)
        
        directions = ['N', 'E', 'S', 'W']
        for i, direction in enumerate(directions):
            angle = i * 90
            x = int(radius * 0.8 * math.sin(math.radians(angle)))
            y = int(-radius * 0.8 * math.cos(math.radians(angle)))
            
            painter.setPen(QPen(QColor(255, 255, 255), 2))
            painter.drawText(x - 10, y + 5, direction)
        
        # Draw heading indicator (rotates with yaw)
        painter.rotate(self.yaw)
        painter.setPen(QPen(QColor(255, 0, 0), 3))
        painter.drawLine(0, 0, 0, -radius + 10)
        
        # Arrow head
        points = [
            QPoint(0, -radius + 10),
            QPoint(-8, -radius + 25),
            QPoint(8, -radius + 25)
        ]
        painter.setBrush(QBrush(QColor(255, 0, 0)))
        painter.drawPolygon(QPolygon(points))
        
        painter.restore()
        
        # Draw yaw value
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.drawText(center_x - 30, center_y + radius + 20, f"HDG: {self.yaw:.0f}°")
    
    def draw_angle_text(self, painter):
        """Draw angle values as text"""
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        
        # Draw in top-left corner
        y_offset = 20
        painter.drawText(10, y_offset, f"Roll: {self.roll:.1f}°")
        painter.drawText(10, y_offset + 20, f"Pitch: {self.pitch:.1f}°")
        painter.drawText(10, y_offset + 40, f"Yaw: {self.yaw:.1f}°")
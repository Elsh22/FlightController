"""
True 3D Rocket Visualization using OpenGL
Supports real-time orientation updates and altitude display
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy as np


class Rocket3DWidget(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 700)
        
        # Current orientation (degrees)
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        self.altitude = 0.0
        
        # Camera settings
        self.camera_distance = 5.0
        self.camera_rotation_x = 20.0
        self.camera_rotation_y = 0.0
        
        # Animation
        self.rotation_speed = 1.0
        
    def update_orientation(self, roll, pitch, yaw, altitude=0.0):
        """Update rocket orientation and altitude"""
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw
        self.altitude = altitude
        self.update()
    
    def initializeGL(self):
        """Initialize OpenGL settings"""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Set up lighting
        glLightfv(GL_LIGHT0, GL_POSITION, [5.0, 5.0, 5.0, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        
        # Background color (space black)
        glClearColor(0.05, 0.05, 0.15, 1.0)
        
    def resizeGL(self, w, h):
        """Handle window resize"""
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w / h if h > 0 else 1, 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)
        
    def paintGL(self):
        """Render the 3D scene"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Position camera
        gluLookAt(
            self.camera_distance * math.sin(math.radians(self.camera_rotation_y)),
            self.camera_distance * math.sin(math.radians(self.camera_rotation_x)),
            self.camera_distance * math.cos(math.radians(self.camera_rotation_y)),
            0, 0, 0,
            0, 1, 0
        )
        
        # Draw reference grid
        self.draw_grid()
        
        # Draw horizon line
        self.draw_horizon()
        
        # Apply altitude translation
        altitude_scale = 0.01  # Scale altitude to reasonable visual range
        glTranslatef(0, self.altitude * altitude_scale, 0)
        
        # Apply rotations (order matters: yaw, pitch, roll)
        glRotatef(self.yaw, 0, 1, 0)      # Yaw (around Y-axis)
        glRotatef(self.pitch, 1, 0, 0)    # Pitch (around X-axis)
        glRotatef(self.roll, 0, 0, 1)     # Roll (around Z-axis)
        
        # Draw the rocket
        self.draw_rocket()
        
        # Draw orientation axes
        self.draw_axes()
        
    def draw_grid(self):
        """Draw reference grid on ground plane"""
        glDisable(GL_LIGHTING)
        glColor3f(0.2, 0.2, 0.3)
        glBegin(GL_LINES)
        
        grid_size = 10
        for i in range(-grid_size, grid_size + 1):
            # Lines parallel to X-axis
            glVertex3f(i, -2, -grid_size)
            glVertex3f(i, -2, grid_size)
            # Lines parallel to Z-axis
            glVertex3f(-grid_size, -2, i)
            glVertex3f(grid_size, -2, i)
        
        glEnd()
        glEnable(GL_LIGHTING)
        
    def draw_horizon(self):
        """Draw horizon reference"""
        glDisable(GL_LIGHTING)
        glColor3f(1.0, 0.8, 0.0)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        
        segments = 50
        radius = 8
        for i in range(segments):
            angle = 2.0 * math.pi * i / segments
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            glVertex3f(x, -2, z)
        
        glEnd()
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)
        
    def draw_rocket(self):
        """Draw detailed 3D rocket model"""
        # Body (cylinder)
        glColor3f(0.9, 0.9, 0.95)  # Metallic silver
        self.draw_cylinder(0.0, -1.5, 0.0, 0.2, 3.0, 20)
        
        # Nose cone
        glColor3f(0.95, 0.95, 1.0)  # Slightly brighter
        self.draw_cone(0.0, 1.5, 0.0, 0.2, 0.8, 20)
        
        # Engine nozzle
        glColor3f(0.3, 0.3, 0.4)  # Dark gray
        self.draw_cone(0.0, -1.5, 0.0, 0.15, -0.4, 20, bottom_radius=0.18)
        
        # Grid fins (4 fins)
        glColor3f(0.2, 0.2, 0.3)
        fin_positions = [0, 90, 180, 270]
        for angle in fin_positions:
            glPushMatrix()
            glRotatef(angle, 0, 1, 0)
            self.draw_fin(0.2, 0.5, 0.0, 0.4, 0.6, 0.05)
            glPopMatrix()
        
        # Engine flame (if altitude > 0, showing thrust)
        if self.altitude > 0.1:
            self.draw_flame()
        
        # Stripes/Details
        glDisable(GL_LIGHTING)
        glColor3f(0.0, 0.0, 0.0)
        glLineWidth(2.0)
        
        # Draw ring details
        for y_pos in [-0.5, 0.0, 0.5]:
            glBegin(GL_LINE_LOOP)
            segments = 30
            for i in range(segments):
                angle = 2.0 * math.pi * i / segments
                x = 0.21 * math.cos(angle)
                z = 0.21 * math.sin(angle)
                glVertex3f(x, y_pos, z)
            glEnd()
        
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)
        
    def draw_cylinder(self, x, y, z, radius, height, segments):
        """Draw a cylinder"""
        glPushMatrix()
        glTranslatef(x, y, z)
        
        # Draw side
        glBegin(GL_QUAD_STRIP)
        for i in range(segments + 1):
            angle = 2.0 * math.pi * i / segments
            x_pos = radius * math.cos(angle)
            z_pos = radius * math.sin(angle)
            
            glNormal3f(math.cos(angle), 0, math.sin(angle))
            glVertex3f(x_pos, 0, z_pos)
            glVertex3f(x_pos, height, z_pos)
        glEnd()
        
        # Draw top cap
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, 1, 0)
        glVertex3f(0, height, 0)
        for i in range(segments + 1):
            angle = 2.0 * math.pi * i / segments
            glVertex3f(radius * math.cos(angle), height, radius * math.sin(angle))
        glEnd()
        
        # Draw bottom cap
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, -1, 0)
        glVertex3f(0, 0, 0)
        for i in range(segments + 1):
            angle = 2.0 * math.pi * i / segments
            glVertex3f(radius * math.cos(angle), 0, radius * math.sin(angle))
        glEnd()
        
        glPopMatrix()
        
    def draw_cone(self, x, y, z, radius, height, segments, bottom_radius=0.0):
        """Draw a cone"""
        glPushMatrix()
        glTranslatef(x, y, z)
        
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, 1, 0)
        glVertex3f(0, height, 0)
        
        for i in range(segments + 1):
            angle = 2.0 * math.pi * i / segments
            x_pos = radius * math.cos(angle)
            z_pos = radius * math.sin(angle)
            
            # Normal pointing outward
            normal_length = math.sqrt(x_pos**2 + height**2 + z_pos**2)
            if normal_length > 0:
                glNormal3f(x_pos/normal_length, height/normal_length, z_pos/normal_length)
            
            glVertex3f(x_pos, 0, z_pos)
        glEnd()
        
        # Bottom cap
        if bottom_radius > 0:
            glBegin(GL_TRIANGLE_FAN)
            glNormal3f(0, -1, 0)
            glVertex3f(0, 0, 0)
            for i in range(segments + 1):
                angle = 2.0 * math.pi * i / segments
                glVertex3f(bottom_radius * math.cos(angle), 0, bottom_radius * math.sin(angle))
            glEnd()
        
        glPopMatrix()
        
    def draw_fin(self, x, y, z, width, height, thickness):
        """Draw a rectangular fin"""
        glPushMatrix()
        glTranslatef(x, y, z)
        
        # Front face
        glBegin(GL_QUADS)
        glNormal3f(0, 0, 1)
        glVertex3f(0, 0, thickness/2)
        glVertex3f(width, 0, thickness/2)
        glVertex3f(width, height, thickness/2)
        glVertex3f(0, height, thickness/2)
        glEnd()
        
        # Back face
        glBegin(GL_QUADS)
        glNormal3f(0, 0, -1)
        glVertex3f(0, 0, -thickness/2)
        glVertex3f(0, height, -thickness/2)
        glVertex3f(width, height, -thickness/2)
        glVertex3f(width, 0, -thickness/2)
        glEnd()
        
        # Side faces
        glBegin(GL_QUADS)
        # Top
        glNormal3f(0, 1, 0)
        glVertex3f(0, height, -thickness/2)
        glVertex3f(0, height, thickness/2)
        glVertex3f(width, height, thickness/2)
        glVertex3f(width, height, -thickness/2)
        
        # Bottom
        glNormal3f(0, -1, 0)
        glVertex3f(0, 0, -thickness/2)
        glVertex3f(width, 0, -thickness/2)
        glVertex3f(width, 0, thickness/2)
        glVertex3f(0, 0, thickness/2)
        
        # Outer edge
        glNormal3f(1, 0, 0)
        glVertex3f(width, 0, -thickness/2)
        glVertex3f(width, height, -thickness/2)
        glVertex3f(width, height, thickness/2)
        glVertex3f(width, 0, thickness/2)
        
        # Inner edge
        glNormal3f(-1, 0, 0)
        glVertex3f(0, 0, -thickness/2)
        glVertex3f(0, 0, thickness/2)
        glVertex3f(0, height, thickness/2)
        glVertex3f(0, height, -thickness/2)
        glEnd()
        
        glPopMatrix()
        
    def draw_flame(self):
        """Draw engine flame"""
        glDisable(GL_LIGHTING)
        
        # Outer flame (orange)
        glColor4f(1.0, 0.5, 0.0, 0.7)
        glPushMatrix()
        glTranslatef(0, -1.5, 0)
        glRotatef(-90, 1, 0, 0)
        self.draw_cone(0, 0, 0, 0.15, -0.6, 15)
        glPopMatrix()
        
        # Inner flame (yellow-white)
        glColor4f(1.0, 1.0, 0.3, 0.9)
        glPushMatrix()
        glTranslatef(0, -1.5, 0)
        glRotatef(-90, 1, 0, 0)
        self.draw_cone(0, 0, 0, 0.08, -0.4, 15)
        glPopMatrix()
        
        glEnable(GL_LIGHTING)
        
    def draw_axes(self):
        """Draw orientation axes"""
        glDisable(GL_LIGHTING)
        glLineWidth(3.0)
        
        length = 1.5
        
        glBegin(GL_LINES)
        # X-axis (Red)
        glColor3f(1, 0, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(length, 0, 0)
        
        # Y-axis (Green)
        glColor3f(0, 1, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, length, 0)
        
        # Z-axis (Blue)
        glColor3f(0, 0, 1)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, length)
        glEnd()
        
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)
        
    def mousePressEvent(self, event):
        """Handle mouse press for camera control"""
        self.last_mouse_pos = event.pos()
        
    def mouseMoveEvent(self, event):
        """Handle mouse drag for camera rotation"""
        if event.buttons():
            dx = event.pos().x() - self.last_mouse_pos.x()
            dy = event.pos().y() - self.last_mouse_pos.y()
            
            self.camera_rotation_y += dx * 0.5
            self.camera_rotation_x += dy * 0.5
            
            # Clamp vertical rotation
            self.camera_rotation_x = max(-89, min(89, self.camera_rotation_x))
            
            self.last_mouse_pos = event.pos()
            self.update()
            
    def wheelEvent(self, event):
        """Handle mouse wheel for camera zoom"""
        delta = event.angleDelta().y()
        self.camera_distance -= delta * 0.01
        self.camera_distance = max(2.0, min(15.0, self.camera_distance))
        self.update()
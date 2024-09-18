from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QPainter, QPainterPath, QColor, QPen, QFont
from PySide6.QtCore import QRectF, QPointF, Qt
import math

class HexTile(QGraphicsItem):
    def __init__(self, x_coord, y_coord, terrain_type, hex_map_view, units=None):
        super().__init__()
        self.x_coord = x_coord  # Column (q)
        self.y_coord = y_coord  # Row (r)
        self.terrain_type = terrain_type
        self.hex_map_view = hex_map_view  # Reference to the HexMapView
        self.units = units if units is not None else []  # List of units in this hex
        self.size = 40  # Adjust size as needed
        self.highlighted = False  # Track whether the hex tile is highlighted
        self.setPos(self.calculate_position())

        # Initialize markers as None
        self.unit_marker = None
        self.settlement_marker = None

    def calculate_position(self):
        size = self.size
        width = size * 3 / 2  # Horizontal distance between hex centers
        height = (math.sqrt(3) * size) / 2  # Vertical distance between hex centers

        x = width * self.x_coord
        # Apply vertical offset for odd columns to stagger the hexes
        if self.x_coord % 2 != 0:
            y = height * (self.y_coord)
        else:
            y = height * self.y_coord

        return QPointF(x, y)

    def boundingRect(self):
        size = self.size
        width = size * 2
        height = math.sqrt(3) * size
        return QRectF(-width / 2, -height / 2, width, height)

    def paint(self, painter, option, widget):
        # Draw hexagon
        path = QPainterPath()
        for i in range(6):
            angle_deg = 60 * i  # Flat-top hex
            angle_rad = math.pi / 180 * angle_deg
            x = self.size * math.cos(angle_rad)
            y = self.size * math.sin(angle_rad)
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        path.closeSubpath()

        # Set color based on terrain
        terrain_colors = {
            'plain': QColor('forestgreen'),
            'forest': QColor('darkgreen'),
            'mountain': QColor('gray'),
            'swamp': QColor('darkolivegreen'),
            'jungle': QColor('olivedrab'),
            'desert': QColor('sandybrown'),
            'tundra': QColor('lightblue'),
            'nexus': QColor('purple'),
            'ocean': QColor('blue'),
            # Add other terrains as needed
        }
        color = terrain_colors.get(self.terrain_type, QColor('white'))

        painter.setBrush(color)
        painter.setPen(QPen(QColor('black')))
        painter.drawPath(path)

        # Draw highlight border if highlighted
        if self.highlighted:
            painter.setPen(QPen(QColor('darkred'), 2))
            painter.drawPath(path)


        # Set text color based on terrain type
        if self.terrain_type == 'ocean':
            text_color = QColor('#B0B0B0')  # White text for ocean terrain
        else:
            text_color = QColor('black')  # Default text color

        # Draw coordinate labels only if label_visible is True
        if self.hex_map_view.show_coords:
            painter.setPen(QPen(QColor(text_color)))
            painter.setFont(QFont('Arial', 8))
            painter.drawText(self.boundingRect(), Qt.AlignCenter, f"({self.x_coord},{self.y_coord})")

    def set_highlight(self, highlight):
        self.highlighted = highlight
        self.update()  # Trigger a repaint to show/hide the highlight
    
    def set_show_coords(self, show):
        """Toggle the display of hex coordinates."""
        self.hex_map_view.show_coords = False
        
        self.update()  # Trigger a repaint to update the coordinate label visibility

    def set_terrain(self, terrain_type):
        """Update the terrain type and repaint."""
        if self.terrain_type != terrain_type:
            self.terrain_type = terrain_type
            self.update()

    def set_units(self, units):
        """Update the units and repaint."""
        if self.units != units:
            self.units = units
            self.update()

    def update_from_data(self, data):
        if 'terrain' in data:
            self.set_terrain(data['terrain'])
        if 'units' in data:
            self.set_units(data['units'])
        # Add more updates as needed
        self.update()

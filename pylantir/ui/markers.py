from PySide6.QtWidgets import QGraphicsItemGroup, QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsPolygonItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QPolygonF


class Markers:
    def create_triangle_marker(self, color='white', size=10, circle_color='white', circle_size=4):
            """
            Create a triangle marker with a small circle at the top.

            Args:
                color (str): Color of the triangle.
                size (int): Size of the triangle.
                circle_color (str): Color of the circle.
                circle_size (int): Diameter of the circle.

            Returns:
                QGraphicsItemGroup: A group containing the triangle and the circle.
            """
            # 1. Define the points for the triangle
            points = [
                QPointF(0, -size / 2),            # Top point
                QPointF(size / 2, size / 2),     # Bottom right point
                QPointF(-size / 2, size / 2)     # Bottom left point
            ]
            triangle = QGraphicsPolygonItem(QPolygonF(points))
            triangle.setBrush(QBrush(QColor(color)))
            triangle.setPen(QPen(Qt.NoPen))  # No border

            # Set the triangle's origin to the center
            triangle.setTransformOriginPoint(0, 0)

            # Set the Z-value for the triangle to control the stacking order
            triangle.setZValue(2)

            # 2. Create the small circle at the top of the triangle
            # Calculate the position so that the center of the circle is at (0, -size / 2)
            # The ellipse's top-left corner is offset by half the circle size
            circle = QGraphicsEllipseItem(
                -circle_size / 2,
                -size / 2 - circle_size / 2,
                circle_size,
                circle_size
            )
            circle.setBrush(QBrush(QColor(circle_color)))
            circle.setPen(QPen(Qt.NoPen))  # No border

            # Set the circle's origin to the center
            circle.setTransformOriginPoint(0, 0)

            # Set the Z-value for the circle to ensure it appears above the triangle
            circle.setZValue(3)

            # 3. Group the triangle and circle into a single QGraphicsItemGroup
            group = QGraphicsItemGroup()
            group.addToGroup(triangle)
            group.addToGroup(circle)

            # Set the group's origin to the center
            group.setTransformOriginPoint(0, 0)

            # Optionally, set the group's Z-value if needed
            group.setZValue(2)

            return group


    def create_ring_with_dot_marker(self, ring_color='white', dot_color='white', outer_diameter=10, ring_thickness=2, dot_diameter=2):
        """
        Create a ring with a small dot in the center, leaving a transparent space between the ring and the dot.
        
        Args:
            ring_color (str): Color of the outer ring.
            dot_color (str): Color of the dot in the center.
            outer_diameter (int): Diameter of the outer ring.
            ring_thickness (int): Thickness of the ring.
            dot_diameter (int): Diameter of the center dot.
            
        Returns:
            QGraphicsItemGroup: The ring with a dot marker.
        """
        # Create the outer ring (with transparent center)
        outer_ring = QGraphicsEllipseItem(-outer_diameter / 2, -outer_diameter / 2, outer_diameter, outer_diameter)
        outer_ring.setBrush(Qt.NoBrush)  # No fill to create the transparent center
        outer_ring.setPen(QPen(QColor(ring_color), ring_thickness))  # Ring outline with specified thickness
            
        # Create the center dot
        center_dot = QGraphicsEllipseItem(-dot_diameter / 2, -dot_diameter / 2, dot_diameter, dot_diameter)
        center_dot.setBrush(QBrush(QColor(dot_color)))  # Set the color of the center dot
        center_dot.setPen(QPen(Qt.NoPen))  # No border
            
        # Create a group item to combine the ring and dot
        group = QGraphicsItemGroup()
        group.addToGroup(outer_ring)   # Add the outer ring
        group.addToGroup(center_dot)   # Add the center dot

        # Set the Z-value to ensure it's drawn above the hex
        group.setZValue(2)

        return group

    def create_hollow_box_marker(self, box_color='white', outer_size=10, box_thickness=2):
        """
        Create a hollow box/square marker with specified color, size, and thickness.
            
        Args:
            box_color (str): Color of the box outline.
            outer_size (int): Size (width and height) of the outer box.
            box_thickness (int): Thickness of the box outline.
                
        Returns:
            QGraphicsItemGroup: The hollow box marker.
        """
        # Create the outer box (with transparent center)
        outer_box = QGraphicsRectItem(-outer_size / 2, -outer_size / 2, outer_size, outer_size)
        outer_box.setBrush(Qt.NoBrush)  # No fill to create the transparent center
        outer_box.setPen(QPen(QColor(box_color), box_thickness))  # Box outline with specified thickness
        
        # Create a group item to combine the box
        group = QGraphicsItemGroup()
        group.addToGroup(outer_box)   # Add the outer box
        
        # Add a center dot (similar to the ring with a dot)
                
        dot_color = 'white'  # You can parameterize this if needed
        dot_diameter = outer_size / 4  # Adjust size as needed
        center_dot = QGraphicsEllipseItem(-dot_diameter / 2, -dot_diameter / 2, dot_diameter, dot_diameter)
        center_dot.setBrush(QBrush(QColor(dot_color)))  # Set the color of the center dot
        center_dot.setPen(QPen(Qt.NoPen))  # No border for the dot
        group.addToGroup(center_dot)  # Add the center dot to the group
        
        # Set the Z-value to ensure it's drawn above other items
        group.setZValue(2)
        
        return group

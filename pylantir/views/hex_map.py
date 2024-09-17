# hex_map.py

from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QTableWidget, QTableWidgetItem, QHeaderView, QGraphicsPolygonItem, QGraphicsEllipseItem, QGraphicsItemGroup
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QPolygonF
from PySide6.QtCore import Qt, QPointF, Signal, QObject, QRectF
from collections import defaultdict
from pylantir.views.hex_tile import HexTile

class HexMapView(QGraphicsView):
    # Define custom signals
    report_loaded = Signal(str)
    hex_selected = Signal(dict)  # Emits the full region data

    def __init__(self, data_manager, data_table):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.data_manager = data_manager  # DataManager instance passed in constructor
        self.data_table = data_table
        self.dragging = False  # Track if we are dragging for panning
        self.last_mouse_pos = QPointF()  # Last mouse position during dragging
        self.selected_hex_tile = None  # Initialize selected_hex_tile
        self.hex_map_tile_to_region = {}  # Mapping from HexTile to region data
        self.coordinates_to_hex_tile = {}  # mapping from (x, y) to HexTile
        # self.hex_to_unit_marker = {}  # mapping from HexTile to unit marker
        self.hex_to_settlement_marker = {}  # mapping from HexTile to settlement marker
        self.show_coords = True  # Boolean flag to track if hex coordinates are shown
        self.init_ui()
        print(f"HexMapView initialized with data_table: {self.data_table}")

    def init_ui(self):
        # Enable antialiasing for smoother graphics
        self.setRenderHint(QPainter.Antialiasing)
        # Enable zooming functionality
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

    def toggle_hex_labels(self):
        """Toggle the visibility of hex coordinate labels."""
        self.show_coords = not self.show_coords  # Flip the flag
        print(f"Toggling hex labels. New state: {self.show_coords}")  # Debugging
        for item in self.scene.items():
            if isinstance(item, HexTile):
                item.set_show_coords(self.show_coords)  # Update the visibility of labels
                print(f"Toggled hex at ({item.x_coord}, {item.y_coord})")  # Debugging


    def create_triangle_marker(self, color='white', size=10):
        """
        Create a small triangle marker.
        
        Args:
            color (str): Color of the triangle.
            size (int): Size of the triangle.
        
        Returns:
            QGraphicsPolygonItem: The triangle marker.
        """
        # Define the points for the triangle
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

        return triangle


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



    def load_map_data(self, regions_data):
        try:
            print("Loading map data...")
            print(f"Total regions to load: {len(regions_data)}")

            # Retrieve faction info
            faction_info = self.data_manager.get_faction_info()
            faction_number = faction_info.get("number")

            # Clear all existing unit markers and data
            self.clear_all_unit_markers()
            self.clear_data_table()

            # Group regions by x_coord
            columns = defaultdict(list)
            for region in regions_data:
                x = region['coordinates']['x']
                columns[x].append(region)

            # Process regions
            for x in sorted(columns.keys()):
                sorted_regions = sorted(columns[x], key=lambda r: r['coordinates']['y'])
                print(f"Column {x} sorted y-coordinates: {[r['coordinates']['y'] for r in sorted_regions]}")
                for region in sorted_regions:
                    x = region['coordinates']['x']
                    y = region['coordinates']['y']
                    terrain = region['terrain']
                    units = region.get('units', [])

                    # Validate coordinates
                    if not self.is_valid_hex_coordinate(x, y):
                        continue

                    coord_key = (x, y)

                    if coord_key in self.coordinates_to_hex_tile:
                        # Update existing HexTile
                        hex_tile = self.coordinates_to_hex_tile[coord_key]
                        hex_tile.set_terrain(terrain)
                        hex_tile.set_units(units)
                        self.hex_map_tile_to_region[hex_tile] = region  # Update the region data
                    else:
                        # Create new HexTile
                        hex_tile = HexTile(x, y, terrain, hex_map_view=self, units=units)
                        self.scene.addItem(hex_tile)
                        self.hex_map_tile_to_region[hex_tile] = region
                        self.coordinates_to_hex_tile[coord_key] = hex_tile

                    # Handle unit markers
                    self.update_unit_marker(hex_tile, units, faction_number)

                    # Handle settlement markers
                    self.update_settlement_marker(hex_tile, region.get('settlement'))

            # Process exits and ensure neighbors are placed
            self.process_exits(regions_data)

            # Adjust the scene
            self.setSceneRect(self.scene.itemsBoundingRect())
            self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
            print("Map data loaded successfully.")
            
            # Emit a signal when the map data is successfully loaded
            self.report_loaded.emit("Map data loaded successfully.")
        except Exception as e:
            print(f"Error loading map data: {e}")
            self.report_loaded.emit("Error loading map data. (see console for details)")

    def clear_all_unit_markers(self):
        for hex_tile in self.coordinates_to_hex_tile.values():
            if hex_tile.unit_marker:
                self.scene.removeItem(hex_tile.unit_marker)
                hex_tile.unit_marker = None
            hex_tile.units = []

    def clear_data_table(self):
        self.data_table.setRowCount(0)

    def update_hex_data(self, x, y, data):
        self.data_manager.update_region(x, y, data)
        hex_tile = self.coordinates_to_hex_tile.get((x, y))
        if hex_tile:
            hex_tile.update_from_data(data)

    def process_exits(self, regions_data):
        for region in regions_data:
            x = region['coordinates']['x']
            y = region['coordinates']['y']
            for exit in region.get('exits', []):
                neighbor_coords = exit['region']['coordinates']
                nx, ny = neighbor_coords['x'], neighbor_coords['y']
                neighbor_coord_key = (nx, ny)
                if not self.is_valid_hex_coordinate(nx, ny):
                    continue
                if neighbor_coord_key not in self.coordinates_to_hex_tile:
                    neighbor_terrain = exit['region'].get('terrain', 'unknown')
                    neighbor_hex_tile = self.create_and_place_hex(nx, ny, neighbor_terrain, [])
                    self.hex_map_tile_to_region[neighbor_hex_tile] = exit['region']
                    self.coordinates_to_hex_tile[neighbor_coord_key] = neighbor_hex_tile

    def update_unit_marker(self, hex_tile, units, faction_number):
        has_faction_units = any(
            unit.get('faction', {}).get('number') == faction_number
            for unit in units
        )

        if has_faction_units:
            if hex_tile.unit_marker is None:
                triangle = self.create_triangle_marker(color='white', size=8)
                triangle.setParentItem(hex_tile)
                triangle.setPos(0, 20)
                hex_tile.unit_marker = triangle
        else:
            if hex_tile.unit_marker:
                hex_tile.unit_marker.setParentItem(None)
                self.scene.removeItem(hex_tile.unit_marker)
                hex_tile.unit_marker = None

    def update_settlement_marker(self, hex_tile, settlement):
        if settlement:
            if hex_tile.settlement_marker is None:
                ring_with_dot = self.create_ring_with_dot_marker(
                    ring_color='white', 
                    dot_color='white', 
                    outer_diameter=12, 
                    ring_thickness=2, 
                    dot_diameter=4
                )
                ring_with_dot.setParentItem(hex_tile)
                ring_with_dot.setPos(0, -20)
                hex_tile.settlement_marker = ring_with_dot
        else:
            if hex_tile.settlement_marker:
                hex_tile.settlement_marker.setParentItem(None)
                self.scene.removeItem(hex_tile.settlement_marker)
                hex_tile.settlement_marker = None

    def create_and_place_hex(self, x, y, terrain, regions_data):
        hex_tile = HexTile(x, y, terrain, self, [])
        self.scene.addItem(hex_tile)
        print(f"Neighbor HexTile created at ({x}, {y}) with terrain: {terrain}")
        return hex_tile

    def is_valid_hex_coordinate(self, x, y):
        # Define valid coordinate rules based on your map's design
        if x < 0 or y < 0:
            return False
        if x % 2 == 0:
            return y % 2 == 0
        else:
            return y % 2 == 1

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            # Start panning on right-click
            self.dragging = True
            self.last_mouse_pos = event.pos()
            event.accept()
        elif event.button() == Qt.LeftButton:
            # Handle left-click events (hex selection)
            scene_pos = self.mapToScene(event.pos())
            items = self.scene.items(scene_pos)
            for item in items:
                if isinstance(item, HexTile):
                    self.highlight_hex_tile(item)
                    self.update_data_table(item)
                    # Emit the full region data when a hex is selected
                    region = self.hex_map_tile_to_region.get(item)
                    if region:
                        print(f"Debug: Emitting hex_selected with data: {region}")  # Debug statement
                        self.hex_selected.emit(region)
                    break
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging:
            # Right-click dragging for panning
            delta = event.pos() - self.last_mouse_pos
            self.last_mouse_pos = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton and self.dragging:
            # End panning on right-click release
            self.dragging = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        self.scale(zoom_factor, zoom_factor)

    def highlight_hex_tile(self, hex_tile):
        if self.selected_hex_tile:
            self.selected_hex_tile.set_highlight(False)
            self.selected_hex_tile.setZValue(0)  # Reset z-value of previously selected hex tile
        self.selected_hex_tile = hex_tile
        self.selected_hex_tile.set_highlight(True)
        self.selected_hex_tile.setZValue(1)  # Bring the selected hex tile to the foreground

    def update_data_table(self, hex_tile):
        print(f"Updating data table with units: {hex_tile.units}")
        self.data_table.setRowCount(0)
        self.data_table.setColumnCount(0)

        if not hex_tile.units:
            print("No units to display.")
            return

        # Define the columns you want to display
        columns = [
            "Unit Name",
            "Faction Name",
            "Status",
            "Avoid",
            "Guard",
            "Contains",
        ]

        # Set table headers
        self.data_table.setColumnCount(len(columns))
        self.data_table.setHorizontalHeaderLabels(columns)

        # Determine the number of rows based on units
        self.data_table.setRowCount(len(hex_tile.units))

        for row, unit in enumerate(hex_tile.units):
            # Extract and format each piece of data

            # Status (from 'attitude')
            status = str( ' ' + unit.get('attitude', 'neutral') + ' ')

            # Faction Information
            faction_info = unit.get('faction', {}).get('name', 'Unknown Faction')
            faction_number = str(unit.get('faction', {}).get('number', ''))

            # Flags (from 'flags')
            flags = unit.get('flags', {})
            avoid = flags.get('avoid', False)
            guard = flags.get('guard', False)

            # Units Details (from 'items')
            units_details = unit.get('units') or unit.get('items') or []

            # Role
            role = str( ' ' + unit.get('name', '')) + ' (' + str(unit.get('number', '')) + ') '
     
            # Faction Display
            faction_display = f" {faction_info} (#{faction_number}) " if faction_number else faction_info

            # Flags Display
            avoid_display = " Yes " if avoid else " No "
            guard_display = " Yes " if guard else " No "

            # Units Display
            if isinstance(units_details, list):
                # Convert list of dictionaries to a readable string
                units_display = " ; ".join([f"{item.get('amount', '')}x {item.get('name', '')} " for item in units_details])
                # Optional: Create a detailed tooltip
                detailed_units = "\n".join([f"{item.get('amount', '')}x {item.get('name', '')} ({item.get('tag', '')})" for item in units_details])
            elif isinstance(units_details, dict):
                units_display = f"Avoid: {avoid_display}, Guard: {guard_display}"
                detailed_units = units_display
            else:
                units_display = str(units_details)
                detailed_units = units_display

            # Role Display
            role_display = role

            # Compile Table Data
            table_data = [
                role_display,
                faction_display,
                status,
                avoid_display,
                guard_display,
                units_display,         
            ]

            for col, data in enumerate(table_data):
                item = QTableWidgetItem(data)
                if col == 5:  # 'Units' column
                    item.setToolTip(detailed_units)
                self.data_table.setItem(row, col, item)
                print(f"Set row {row}, column {col} to {data}")

        # Adjust the table for better readability
        self.data_table.resizeColumnsToContents()
        self.data_table.horizontalHeader().setStretchLastSection(True)
        self.data_table.setSortingEnabled(True)

        # Optionally, set alignment for all cells
        for row in range(self.data_table.rowCount()):
            for col in range(self.data_table.columnCount()):
                item = self.data_table.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # Align left and vertically center

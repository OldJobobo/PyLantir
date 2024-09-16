# hex_map.py

from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QTableWidget, QTableWidgetItem
from PySide6.QtGui import QPainter, QPen
from PySide6.QtCore import Qt, QPointF, Signal, QObject
from collections import defaultdict
from .hex_tile import HexTile

class HexMapView(QGraphicsView):
    # Define custom signals
    report_loaded = Signal(str)
    hex_selected = Signal(dict)  # Emits the full region data

    def __init__(self, data_table):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.data_table = data_table
        self.dragging = False  # Track if we are dragging for panning
        self.last_mouse_pos = QPointF()  # Last mouse position during dragging
        self.selected_hex_tile = None  # Initialize selected_hex_tile
        self.hex_map_tile_to_region = {}  # Mapping from HexTile to region data
        self.init_ui()
        print(f"HexMapView initialized with data_table: {self.data_table}")

    def init_ui(self):
        # Enable antialiasing for smoother graphics
        self.setRenderHint(QPainter.Antialiasing)
        # Enable zooming functionality
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

    def load_map_data(self, regions_data):
        try:
            print("Loading map data...")
            self.scene.clear()
            print(f"Total regions to load: {len(regions_data)}")
            hex_map = {}  # Dictionary to store hex tiles by coordinates

            # Group regions by x_coord for placement
            columns = defaultdict(list)
            for region in regions_data:
                x = region['coordinates']['x']
                columns[x].append(region)

            # Process regions and assign y_index for each column
            for x in sorted(columns.keys()):
                sorted_regions = sorted(columns[x], key=lambda r: r['coordinates']['y'])
                print(f"Column {x} sorted y-coordinates: {[r['coordinates']['y'] for r in sorted_regions]}")
                for region in sorted_regions:
                    x = region['coordinates']['x']
                    y = region['coordinates']['y']
                    terrain = region['terrain']
                    units = region.get('units', [])

                    # Skip invalid coordinates
                    if not self.is_valid_hex_coordinate(x, y):
                        continue

                    # Place the hex tile
                    hex_tile = HexTile(x, y, terrain, units)
                    self.scene.addItem(hex_tile)
                    self.hex_map_tile_to_region[hex_tile] = region  # Map HexTile to region

                    # Process exits and ensure neighbors are placed
                    for exit in region.get('exits', []):
                        neighbor_coords = exit['region']['coordinates']
                        nx = neighbor_coords['x']
                        ny = neighbor_coords['y']

                        # Check if the neighbor is already placed
                        if not self.is_valid_hex_coordinate(nx, ny):
                            continue
                        if any(
                            neighbor_hex.x_coord == nx and neighbor_hex.y_coord == ny
                            for neighbor_hex in self.hex_map_tile_to_region
                        ):
                            continue

                        neighbor_terrain = exit['region'].get('terrain', 'unknown')
                        # Place neighboring hex
                        neighbor_hex_tile = self.create_and_place_hex(nx, ny, neighbor_terrain, regions_data)
                        self.hex_map_tile_to_region[neighbor_hex_tile] = exit['region']  # Map neighbor hex

            # Adjust the scene
            self.setSceneRect(self.scene.itemsBoundingRect())
            self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
            print("Map data loaded successfully.")
            
            # Emit a signal when the map data is successfully loaded
            self.report_loaded.emit("Map data loaded successfully.")
        except Exception as e:
            print(f"Error loading map data: {e}")
            self.report_loaded.emit("Error loading map data. (see console for details)")

    def create_and_place_hex(self, x, y, terrain, regions_data):
        hex_tile = HexTile(x, y, terrain, [])
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
            "Status",
            "Faction Name",
            "Faction Number",
            "Avoid",
            "Guard",
            "Units",
            "Role",
            "Number"
        ]

        # Set table headers
        self.data_table.setColumnCount(len(columns))
        self.data_table.setHorizontalHeaderLabels(columns)

        # Determine the number of rows based on units
        self.data_table.setRowCount(len(hex_tile.units))

        for row, unit in enumerate(hex_tile.units):
            # Extract and format each piece of data

            # Status (from 'attitude')
            status = unit.get('attitude', 'neutral')

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
            role = unit.get('name', '')

            # Number
            number = str(unit.get('number', ''))

            # Faction Display
            faction_display = f"{faction_info} (#{faction_number})" if faction_number else faction_info

            # Flags Display
            avoid_display = "Yes" if avoid else "No"
            guard_display = "Yes" if guard else "No"

            # Units Display
            if isinstance(units_details, list):
                # Convert list of dictionaries to a readable string
                units_display = "; ".join([f"{item.get('amount', '')}x {item.get('name', '')}" for item in units_details])
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

            # Number Display
            number_display = number

            # Compile Table Data
            table_data = [
                status,
                faction_display,
                faction_number,
                avoid_display,
                guard_display,
                units_display,
                role_display,
                number_display
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

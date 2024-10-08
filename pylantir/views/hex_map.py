# hex_map.py

from PySide6.QtWidgets import (
    QGraphicsRectItem, QGraphicsView, QGraphicsScene, QTableWidgetItem, QGraphicsPolygonItem,
    QGraphicsEllipseItem, QGraphicsItemGroup, QTableWidget
    )
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QPolygonF
from PySide6.QtCore import Qt, QPointF, Signal, QObject, QRectF
from collections import defaultdict
from pylantir.views.hex_tile import HexTile
from pylantir.ui.markers import Markers
from pylantir.data.data_manager import DataManager  # Add this import
from pylantir.data.map_manager import MapManager
class HexMapView(QGraphicsView):
    # Define custom signals
    report_loaded = Signal(str)
    hex_selected = Signal(dict)  # Emits the full region data

    def __init__(self, map_manager: MapManager, data_manager: DataManager, data_table: QTableWidget):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.map_manager = map_manager  # MapManager instance passed in constructor
        self.data_manager = data_manager  # DataMngr instance passed in constructor
        self.data_table = data_table
        self.markers = Markers()
        self.dragging = False  # Track if we are dragging for panning
        self.last_mouse_pos = QPointF()  # Last mouse position during dragging
        self.selected_hex_tile = None  # Initialize selected_hex_tile
        self.hex_map_tile_to_region = {}  # Mapping from HexTile to region data
        self.coordinates_to_hex_tile = {}  # mapping from (x, y) to HexTile
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

            # self.update_map_data(regions_data)

            # Group regions by x_coord
            columns = defaultdict(list)
            for region in regions_data:
                if not isinstance(region, dict):
                    print(f"Warning: Invalid region data: {region}")
                    continue
                x = region.get('coordinates', {}).get('x')
                if x is not None:
                    columns[x].append(region)

            # Process regions
            for x in sorted(columns.keys()):
                sorted_regions = sorted(columns[x], key=lambda r: r.get('coordinates', {}).get('y'))
                print(f"Column {x} sorted y-coordinates: {[r.get('coordinates', {}).get('y') for r in sorted_regions]}")
                for region in sorted_regions:
                    coordinates = region.get('coordinates', {})
                    x, y = coordinates.get('x'), coordinates.get('y')
                    terrain = region.get('terrain', 'unknown')
                    structures = region.get('structures')
                    settlement = region.get('settlement')
                    print(f"Processing region at ({x}, {y}) with terrain: {terrain}, structures: {structures}, settlement: {settlement}")

                    units = region.get('units', [])
                    if units is None:
                        units = []
                    print(f"Units in region: {len(units)}")

                    # Validate coordinates
                    if x is None or y is None or not self.is_valid_hex_coordinate(x, y):
                        print(f"Invalid coordinates: ({x}, {y})")
                        continue

                    # Create and place hex tile
                    hex_tile = self.create_and_place_hex(x, y, terrain, units)
                    self.hex_map_tile_to_region[hex_tile] = region
                    self.coordinates_to_hex_tile[(x, y)] = hex_tile

                    # Handle unit markers
                    self.update_unit_marker(hex_tile, units, faction_number)

                    # Update settlement marker
                    self.update_settlement_marker(hex_tile, settlement)

                    # Handle structure markers
                    self.update_structure_marker(hex_tile, structures)

                    # Update the persistent map data
                    self.update_hex_data(x, y, region)

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
            import traceback
            traceback.print_exc()
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
        self.map_manager.update_region(x, y, data)  # Use map_manager instead of data_manager
        hex_tile = self.coordinates_to_hex_tile.get((x, y))
        if hex_tile:
            hex_tile.update_from_data(data)

    def update_map_data(self, regions_data):
         # Group regions by x_coord
            columns = defaultdict(list)
            for region in regions_data:
                if not isinstance(region, dict):
                    print(f"Warning: Invalid region data: {region}")
                    continue
                x = region.get('coordinates', {}).get('x')
                if x is not None:
                    columns[x].append(region)

            # Process regions
            for x in sorted(columns.keys()):
                sorted_regions = sorted(columns[x], key=lambda r: r.get('coordinates', {}).get('y'))
                print(f"Column {x} sorted y-coordinates: {[r.get('coordinates', {}).get('y') for r in sorted_regions]}")
                for region in sorted_regions:
                    coordinates = region.get('coordinates', {})
                    x, y = coordinates.get('x'), coordinates.get('y')
                    terrain = region.get('terrain', 'unknown')
                    structures = region.get('structures')
                    settlement = region.get('settlement')
                    print(f"Processing region at ({x}, {y}) with terrain: {terrain}, structures: {structures}, settlement: {settlement}")

                    units = region.get('units', [])
                    if units is None:
                        units = []
                    print(f"Units in region: {len(units)}")

                    # Validate coordinates
                    if x is None or y is None or not self.is_valid_hex_coordinate(x, y):
                        print(f"Invalid coordinates: ({x}, {y})")
                        continue

                    # Create and place hex tile
                    hex_tile = self.create_and_place_hex(x, y, terrain, units)
                    self.hex_map_tile_to_region[hex_tile] = region
                    self.coordinates_to_hex_tile[(x, y)] = hex_tile

                    # Update settlement marker
                    self.update_settlement_marker(hex_tile, settlement)

                    # Handle structure markers
                    self.update_structure_marker(hex_tile, structures)

                    # Update the persistent map data
                    self.update_hex_data(x, y, region)


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
                    neighbor_terrain = exit['region'].get('terrain')
                    neighbor_hex_tile = self.create_and_place_hex(nx, ny, neighbor_terrain, [])
                    self.hex_map_tile_to_region[neighbor_hex_tile] = exit['region']
                    self.coordinates_to_hex_tile[neighbor_coord_key] = neighbor_hex_tile

    def update_unit_marker(self, hex_tile, units, faction_number):
        has_faction_units = any(
            unit.get('faction', {}).get('number', 'Hidden') == faction_number
            for unit in units
        )

        if has_faction_units:
            if hex_tile.unit_marker is None:
                triangle = self.markers.create_triangle_marker(color='white', size=8, circle_color='white', circle_size=5)
                triangle.setParentItem(hex_tile)
                triangle.setPos(0, 20)
                hex_tile.unit_marker = triangle
        else:
            if hex_tile.unit_marker:
                hex_tile.unit_marker.setParentItem(None)
                self.scene.removeItem(hex_tile.unit_marker)
                hex_tile.unit_marker = None

        # Update the persistent map data
        self.update_hex_data(hex_tile.x_coord, hex_tile.y_coord, {'units': units})
        
    def update_settlement_marker(self, hex_tile, settlement):
        if settlement:
            if hex_tile.settlement_marker is None:
                ring_with_dot = self.markers.create_ring_with_dot_marker(
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

        # Update the persistent map data
        self.update_hex_data(hex_tile.x_coord, hex_tile.y_coord, {'settlement': settlement})

    def update_structure_marker(self, hex_tile, structures):
        """
        Update the structure marker on the given hex_tile.

        Args:
            hex_tile: The hex tile object to update.
            structures: The structure data associated with the hex.
        """
        if structures and isinstance(structures, list) and len(structures) > 0:
            if not hasattr(hex_tile, 'structure_marker') or hex_tile.structure_marker is None:
                # Create the hollow box marker
                hollow_box = self.markers.create_hollow_box_marker(
                    box_color='white',      # Color of the box outline
                    outer_size=12,         # Size of the box
                    box_thickness=2        # Thickness of the box outline
                )
                # Set the marker as a child of the hex_tile for proper positioning
                hollow_box.setParentItem(hex_tile)
                # Position the marker 20px to the right of the hex center
                hollow_box.setPos(25, 0)
                # Assign the marker to the hex_tile for future reference
                hex_tile.structure_marker = hollow_box
                print(f"Added structure marker to hex ({hex_tile.x_coord}, {hex_tile.y_coord})")
        else:
            if hasattr(hex_tile, 'structure_marker') and hex_tile.structure_marker:
                # Remove the structure marker
                hex_tile.structure_marker.setParentItem(None)
                self.scene.removeItem(hex_tile.structure_marker)
                # Clear the reference
                hex_tile.structure_marker = None
                print(f"Removed structure marker from hex ({hex_tile.x_coord}, {hex_tile.y_coord})")
        
        # Update the persistent map data with the structure information
        if structures:
            self.update_hex_data(hex_tile.x_coord, hex_tile.y_coord, {'structures': structures})
        else:
            self.update_hex_data(hex_tile.x_coord, hex_tile.y_coord, {'structure': None})


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
        """
        Update the data table with units and structures within the selected hex_tile.
        
        Args:
            hex_tile: The selected hex tile object.
        """
        print(f"Updating data table with units: {hex_tile.units}")
        self.data_table.setRowCount(0)
        self.data_table.setColumnCount(0)

        # Retrieve region data associated with the hex_tile
        region = self.hex_map_tile_to_region.get(hex_tile)
        if not region:
            print(f"No region data found for hex_tile: {hex_tile}")
            return

        structures = region.get('structures', [])
        print(f"Structures: {structures}")

        # Check if there are units or structures to display
        if not hex_tile.units and not structures:
            print("No units or structures to display.")
            return
        
        # Define the columns you want to display
        columns = [
            "Structure",
            "Unit Name",
            "Faction Name",
            "Status",
            "Avoid",
            "Guard",
            "Contains",
            "Skills"
        ]

        # Set table headers
        self.data_table.setColumnCount(len(columns))
        self.data_table.setHorizontalHeaderLabels(columns)

        # Calculate total rows needed
        structure_unit_count = sum(len(structure.get('units', [])) for structure in structures)
        total_rows = len(hex_tile.units) + structure_unit_count
        self.data_table.setRowCount(total_rows)

        # Initialize row index
        row_index = 0

        # Process structures and their units
        for structure in structures:
            structure_name = f"{structure.get('name', 'Unknown')} ({structure.get('number', 'N/A')})"
            structure_units = structure.get('units', [])
            
            for unit in structure_units:
                self.add_unit_to_table(row_index, unit, structure_name)
                row_index += 1

        # Process units directly in the hex_tile (not part of any structure)
        for unit in hex_tile.units:
            self.add_unit_to_table(row_index, unit, structure_name=None)  # No structure associated
            row_index += 1

        # Adjust the table for better readability
        self.data_table.resizeColumnsToContents()
        self.data_table.horizontalHeader().setStretchLastSection(True)
        self.data_table.setSortingEnabled(True)
        self.data_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Make the table read-only
        self.data_table.setSelectionBehavior(QTableWidget.SelectRows)  # Make the table read-only
        
        # Optionally, set alignment for all cells
        for row in range(self.data_table.rowCount()):
            for col in range(self.data_table.columnCount()):
                item = self.data_table.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # Align left and vertically center

    def add_unit_to_table(self, row, unit, structure_name=None):
        """
        Add a unit to the data table at the specified row.
        
        Args:
            row (int): The row index in the table.
            unit (dict): The unit data.
            structure_name (str, optional): The name of the structure the unit belongs to. Defaults to None.
        """
        # Structure Display
        structure_display = structure_name if structure_name else "None"

        # Unit Name and Number
        unit_name = unit.get('name', 'Unknown')
        unit_number = unit.get('number', 'N/A')
        role_display = f"{unit_name} ({unit_number})"

        # Faction Information
        faction = unit.get('faction', {})
        faction_info = faction.get('name', 'Unknown Faction')
        faction_number = faction.get('number', 'Hidden')
        faction_display = f"{faction_info} (#{faction_number})" if faction_number else faction_info

        # Status (from 'attitude')
        status = f" {unit.get('attitude', 'neutral')} "

        # Flags (from 'flags')
        flags = unit.get('flags', {})
        avoid = flags.get('avoid', False)
        guard = flags.get('guard', False)
        avoid_display = "Yes" if avoid else "No"
        guard_display = "Yes" if guard else "No"

        # Units Details (from 'items' or 'units')
        units_details = unit.get('units') or unit.get('items') or []
        if isinstance(units_details, list):
            # Convert list of dictionaries to a readable string
            units_display = " ; ".join([
                f"{item.get('amount', '')}x {item.get('name', '')}" for item in units_details
            ])
            # Create a detailed tooltip
            detailed_units = "\n".join([
                f"{item.get('amount', '')}x {item.get('name', '')} ({item.get('tag', '')})" for item in units_details
            ])
        elif isinstance(units_details, dict):
            units_display = f"Avoid: {avoid_display}, Guard: {guard_display}"
            detailed_units = units_display
        else:
            units_display = str(units_details)
            detailed_units = units_display

        # Skills Extraction and Formatting
        skills = unit.get('skills', {})
        known_skills = skills.get('known', [])
        if known_skills:
            # Format: "Skill Name (Level X), Skill Name (Level Y)"
            skills_display = ", ".join([
                f"{skill.get('name', 'Unknown Skill')} (Level {skill.get('level', 'N/A')})" for skill in known_skills
            ])
            # Create a detailed tooltip for skills
            detailed_skills = "\n".join([
                f"{skill.get('name', 'Unknown Skill')}: Level {skill.get('level', 'N/A')}, Days: {skill.get('skill_days', 'N/A')}, Tag: {skill.get('tag', 'N/A')}" for skill in known_skills
            ])
        else:
            skills_display = "None"
            detailed_skills = "No known skills."

        # Compile Table Data
        table_data = [
            structure_display,
            role_display,
            faction_display,
            status,
            avoid_display,
            guard_display,
            units_display,  
            skills_display
        ]

        for col, data in enumerate(table_data):
            item = QTableWidgetItem(data)
            if col == 6:  # 'Contains' column
                item.setToolTip(detailed_units)
            if col == 7:  # 'Skills' column
                item.setToolTip(detailed_skills)
            self.data_table.setItem(row, col, item)
            print(f"Set row {row}, column {col} to {data}")

    def refresh_map(self):
        self.clear_all_unit_markers()
        self.clear_data_table()
        self.load_map_data(self.map_manager.get_map_data())



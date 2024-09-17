import json
from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QLineEdit, QTextEdit, QWidget, QVBoxLayout, QTableWidget, QSplitter
from PySide6.QtGui import QAction, Qt
import os

from pylantir.views.hex_map import HexMapView  # We will create this later
from pylantir.data.data_manager import DataManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
        self.setWindowTitle('PyLantir - Atlantis PBEM Client')
        self.resize(1200, 800)
        self.init_ui()

    def init_ui(self):
        # Create Menu Bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')

        # Open Report Action
        open_action = QAction('&Open Turn Report', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_turn_report)
        file_menu.addAction(open_action)

        # Exit Action
        exit_action = QAction('&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View Menu
        view_menu = menubar.addMenu('&View')

        # Toggle Hex Coordinates Action
        toggle_coords_action = QAction('Draw Coords on Hex', self)
        toggle_coords_action.setCheckable(True)  # Make it checkable so you can see the state
        toggle_coords_action.setChecked(True)    # Set it checked by default
        toggle_coords_action.triggered.connect(self.toggle_hex_coords)  # Connect to the method
        view_menu.addAction(toggle_coords_action)

        # Help Menu
        help_menu = menubar.addMenu('&Help')
        about_action = QAction('&About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # Create central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # Create HexMapView and QTextEdit
        self.data_table = QTableWidget()
        # self.data_table.setRowCount(5)  # Set initial row count
        # self.data_table.setColumnCount(8)  # Set initial column count
        # self.data_table.setHorizontalHeaderLabels(['Status', 'Faction Name', 'Faction Number', 'Avoid', 'Guard', 'Units', 'Role', 'Number'])  # Set initial column headers
        self.data_table.setSortingEnabled(True)

        # Set the grid line color to white
        self.data_table.setStyleSheet("""
            QTableView {
                gridline-color: gray; /* Set the grid line color to light grey */
                background-color: #191919;  /* Set the background color to dark grey */
                border: 1px solid grey;
                padding: 0px;  /* Add padding around the cell content */
            }
        """)

        self.hex_map_view = HexMapView(self.data_manager, self.data_table)
        self.hex_map_view.report_loaded.connect(self.update_status_bar)
        self.hex_map_view.hex_selected.connect(self.display_hex_data)


        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)  # Make the text display read-only

        # Create a vertical splitter for HexMapView (top) and DataTable (bottom)
        left_splitter = QSplitter()
        left_splitter.setOrientation(Qt.Vertical)
        left_splitter.addWidget(self.hex_map_view)
        left_splitter.addWidget(self.data_table)

        # Set initial sizes for the left_splitter (15% for hex map and 25% for data table)
        left_splitter.setSizes([int(self.height() * 0.75), int(self.height() * 0.25)])

        # Create a horizontal splitter to place the left_splitter and text display
        main_splitter = QSplitter()
        main_splitter.setOrientation(Qt.Horizontal)
        main_splitter.addWidget(left_splitter)  # Left side: hex map and data table
        main_splitter.addWidget(self.text_display)  # Right side: text display

        # Set the sizes to give the left part (hex map + data table) more space than the text display
        main_splitter.setSizes([int(self.width() * 0.75), int(self.width() * 0.25)])  # Set proportions (800px to left, 400px to right)

        # Add the main splitter to the central layout
        main_layout.addWidget(main_splitter)

        # Set central widget
        self.setCentralWidget(central_widget)

        # Create and add the status bar
        self.statusBar().showMessage("Ready")  # Show a default message when the app starts

    def toggle_hex_coords(self):
        """Toggle the hex coordinates labels on and off."""
        self.hex_map_view.toggle_hex_labels()

    def update_status_bar(self, message):
        self.statusBar().showMessage(message)
    
    def display_hex_data(self, hex_data):
        """Display hex-specific data (including settlement data) in the text_display widget with debug output."""
        self.text_display.clear()  # Clear previous content
        
        # Print the entire hex data for debugging
        print("Debug: Full hex data being loaded:", hex_data)

        # Display basic hex information
        coordinates = hex_data.get('coordinates', {})
                
        # Access 'x' and 'y' using dictionary keys
        x = coordinates.get('x', 'Unknown')
        y = coordinates.get('y', 'Unknown')
        
        print(f"Debug: Hex Coordinates: {x}, {y}")  # Debug output
        self.text_display.append(f"Hex Coordinates: {x}, {y}")  # Corrected access
        self.statusBar().showMessage(str(f"Hex: {x}, {y}"))  # Show coordinates in status bar
       
        # Display terrain type
        terrain = hex_data.get('terrain', 'Unknown')
        print(f"Debug: Terrain: {terrain}")  # Debug output
        self.text_display.append(f"Terrain: {terrain}")
        
        # Display settlement information
        settlement = hex_data.get('settlement')
        if settlement:
            settlement_name = settlement.get('name', 'Unknown')
            settlement_size = settlement.get('size', 'Unknown')
            print(f"Debug: Settlement: {settlement}")  # Debug output
            self.text_display.append(f"Settlement: {settlement_name} (Size: {settlement_size})")
        else:
            print("Debug: No settlement found")  # Debug output
            self.text_display.append("Settlement: None")

        # Display population information
        population = hex_data.get('population', {})
        population_amount = population.get('amount', 'N/A')
        population_race = population.get('race', 'N/A')
        print(f"Debug: Population: {population}")  # Debug output
        self.text_display.append(f"Population: {population_amount} ({population_race})")
        
        # Display tax information
        tax = hex_data.get('tax', 'N/A')
        print(f"Debug: Tax: {tax}")  # Debug output
        if tax != 'N/A':
            self.text_display.append(f"Tax: {tax}")
        else:
            self.text_display.append("Tax: Not available")
        
         # Display wages information
        wages = hex_data.get('wages', {})
        wages_amount = wages.get('amount', 'N/A')
        wages_max = wages.get('max', 'N/A')
        print(f"Debug: Wages: {wages}")  # Debug output
        if wages_amount != 'N/A' and wages_max != 'N/A':
            self.text_display.append(f"Wages: {wages_amount} (Max: {wages_max})")
        else:
            self.text_display.append("Wages: Not available")

        # Display market information (for_sale and wanted)
        markets = hex_data.get('markets', {})
        print(f"Debug: Markets: {markets}")  # Debug output
        for_sale = markets.get('for_sale', [])
        wanted = markets.get('wanted', [])
        
        if for_sale:
            self.text_display.append("For Sale:")
            for item in for_sale:
                item_name = item.get('name', 'Unknown Item')
                item_amount = item.get('amount', 'N/A')
                item_price = item.get('price', 'N/A')
                print(f"Debug: For Sale Item: {item}")  # Debug output
                self.text_display.append(f"  - {item_amount} {item_name} at {item_price} silver each")
        else:
            print("Debug: No items for sale")  # Debug output
            self.text_display.append("For Sale: None")
        
        if wanted:
            self.text_display.append("Wanted:")
            for item in wanted:
                item_name = item.get('name', 'Unknown Item')
                item_amount = item.get('amount', 'N/A')
                item_price = item.get('price', 'N/A')
                print(f"Debug: Wanted Item: {item}")  # Debug output
                self.text_display.append(f"  - {item_amount} {item_name} at {item_price} silver each")
        else:
            print("Debug: No wanted items")  # Debug output
            self.text_display.append("Wanted: None")
        
       
        
        
        
        # Check if there are exits
        exits = hex_data.get('exits', [])
        print(f"Debug: Exits: {exits}")  # Debug output
        if exits:
            self.text_display.append("Exits:")
            for exit_info in exits:
                direction = exit_info['direction']
                neighboring_region = exit_info['region']
                neighbor_coords = neighboring_region['coordinates']
                neighbor_terrain = neighboring_region.get('terrain', 'Unknown')
                neighbor_province = neighboring_region.get('province', 'Unknown')
                print(f"Debug: Exit {direction} to ({neighbor_coords['x']}, {neighbor_coords['y']}) "
                    f"in {neighbor_province} ({neighbor_terrain})")  # Debug output
                self.text_display.append(f"  - {direction} to ({neighbor_coords['x']}, {neighbor_coords['y']}) "
                                        f"in {neighbor_province} ({neighbor_terrain})")
        else:
            print("Debug: No exits found")  # Debug output
            self.text_display.append("Exits: None")


    
    def open_turn_report(self):
        options = QFileDialog.Options()
        
        # Get the root directory by going up two levels from the current file location
        program_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        reports_directory = os.path.join(program_directory, 'reports')  # Append 'reports' directory

        # Create the directory if it doesn't exist
        if not os.path.exists(reports_directory):
            os.makedirs(reports_directory)

        filename, _ = QFileDialog.getOpenFileName(
            self,
            'Open JSON Turn Report',
            reports_directory,  # Set the initial directory to {programdirectory}/reports
            'JSON Files (*.json);;All Files (*)',
            options=options
        )

        if filename:
            self.data_manager.load_report(filename)
            regions = self.data_manager.get_regions()
            # print(f"Regions obtained: {regions}")  # Add print to check regions
            self.hex_map_view.load_map_data(regions)
            # Update other views as needed

            # Display parsed JSON data
            self.display_parsed_data()

            # QMessageBox.information(self, 'File Loaded', f'Loaded report: {filename}')
        else:
            self.statusBar().showMessage("No file selected")
            QMessageBox.warning(self, 'No File', 'No file was selected.')

    def display_parsed_data(self):
        # Display faction information
        faction_info = self.data_manager.get_faction_info()
        self.text_display.append(f"Faction: {faction_info['name']} [{faction_info['number']}]")

        # Display date information
        date_info = self.data_manager.get_date_info()
        self.text_display.append(f"Date: {date_info['month']}, Year {date_info['year']}")

        # Display engine information
        engine_info = self.data_manager.get_engine_info()
        self.text_display.append(f"Engine: {engine_info['ruleset']} {engine_info['ruleset_version']}, Version {engine_info['version']}")

        # Display attitudes
        attitudes = self.data_manager.get_attitudes()
        self.text_display.append(f"Default Attitude: {attitudes['default']}")

        # Display administrative settings
        admin_settings = self.data_manager.get_administrative_settings()
        self.text_display.append(f"Password Unset: {admin_settings['password_unset']}")
        self.text_display.append(f"Show Unit Attitudes: {admin_settings['show_unit_attitudes']}")
        self.text_display.append(f"Times Sent: {admin_settings['times_sent']}")

    def show_about(self):
        QMessageBox.about(
            self,
            'About PyLantir',
            'PyLantir\n\nAn open-source client for the Atlantis PBEM game.\n\nDeveloped by J. Stuart Brown.'
        )

import json
from PySide6.QtWidgets import (
    QMainWindow, QFileDialog, QMessageBox, QLineEdit, QTextEdit,
    QWidget, QVBoxLayout, QTableWidget, QSplitter, QTabWidget, QTableWidgetItem
)
from PySide6.QtGui import QAction, Qt
import os

from pylantir.views.hex_map import HexMapView  # We will create this later
from pylantir.data.data_manager import DataManager

class MainWindow(QMainWindow):
    def __init__(self):
        """Initialize the main window and its components."""
        super().__init__()
        self.data_manager = DataManager()
        self.data_manager.load_persistent_data('persistent_map_data.json')
        self.setWindowTitle('PyLantir - Atlantis PBEM Client')
        # self.resize(1200, 800)
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface components."""
        # Create Menu Bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')

        # Open Report Action
        open_action = QAction('&Open Turn Report', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_turn_report)
        file_menu.addAction(open_action)
        
        # Save Game Data Action
        save_game_action = QAction('&Save Game Data', self)
        save_game_action.setShortcut('Ctrl+S')
        save_game_action.triggered.connect(self.save_game_data)
        file_menu.addAction(save_game_action)

        # Load Game Data Action
        load_game_action = QAction('&Load Game Data', self)
        load_game_action.setShortcut('Ctrl+L')
        load_game_action.triggered.connect(self.load_game_data)
        file_menu.addAction(load_game_action)

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

       
        self.lower_tab_widget = QTabWidget()

        # Create HexMapView and QTextEdit
        self.data_table = QTableWidget()
        self.data_table.setSortingEnabled(True)
        self.data_table.setSelectionBehavior(QTableWidget.SelectRows)  # Make the table select rows

        # Set the grid line color to white
        self.data_table.setStyleSheet("""
            QTableView {
                gridline-color: gray; /* Set the grid line color to light grey */
                background-color: #191919;  /* Set the background color to dark grey */
                border: 1px solid grey;
                padding: 0px;  /* Add padding around the cell content */
                color: white;  /* Set the text color to white */
            }
        """)
        self.lower_tab_widget.addTab(self.data_table, "Units")

        self.hex_map_view = HexMapView(self.data_manager, self.data_table)
        self.hex_map_view.setStyleSheet("background-color: #1F1F1F; border: 1px solid grey;")
        self.hex_map_view.report_loaded.connect(self.update_status_bar)
        self.hex_map_view.hex_selected.connect(self.display_hex_data)

   

       # Create a QTabWidget instead of a single QTextEdit
        self.tab_widget = QTabWidget()

        # Hex Data Tab
        self.hex_data_tab = QTextEdit()
        self.hex_data_tab.setStyleSheet("background-color: #191919; color: white; border: 1px solid grey; padding: 10px;")
        self.hex_data_tab.setReadOnly(True)
        self.tab_widget.addTab(self.hex_data_tab, "Hex Data")

        # Orders Tab
        self.orders_tab = QTableWidget()
        self.orders_tab.setSortingEnabled(True)
        self.orders_tab.setStyleSheet("""
            QTableView {
                gridline-color: gray;
                background-color: #191919;
                border: 1px solid grey;
                padding: 0px;
                color: white;
            }
        """)

        self.orders_tab.setColumnCount(2)
        self.orders_tab.setHorizontalHeaderLabels(["Unit Name", "Order"])
        self.orders_tab.horizontalHeader().setStretchLastSection(True)
        self.orders_tab.setSelectionBehavior(QTableWidget.SelectRows)  # Make the table select rows
        self.orders_tab.setEditTriggers(QTableWidget.NoEditTriggers)  # Make the table read-only
        self.tab_widget.addTab(self.orders_tab, "Orders")

         # Events Tab
        self.events_tab = QTableWidget()
        self.events_tab.setSortingEnabled(True)
        self.events_tab.setStyleSheet("""
            QTableView {
                gridline-color: gray;
                background-color: #191919;
                border: 1px solid grey;
                padding: 0px;
                color: white;
            }
        """)
        self.events_tab.setColumnCount(3)
        self.events_tab.setHorizontalHeaderLabels(["Unit","Category", "Message"])
        self.events_tab.horizontalHeader().setStretchLastSection(True)
        self.events_tab.setEditTriggers(QTableWidget.NoEditTriggers)  # Make the table read-only
        self.events_tab.setSelectionBehavior(QTableWidget.SelectRows)  # Make the table select rows
        self.lower_tab_widget.addTab(self.events_tab, "Events")

        # Create a vertical splitter for HexMapView (top) and DataTable (bottom)
        left_splitter = QSplitter()
        left_splitter.setOrientation(Qt.Vertical)
        left_splitter.addWidget(self.hex_map_view)
        left_splitter.addWidget(self.lower_tab_widget)

        # Set initial sizes for the left_splitter (15% for hex map and 25% for data table)
        left_splitter.setSizes([int(self.height() * 0.75), int(self.height() * 0.25)])

        # Create a horizontal splitter to place the left_splitter and text display
        main_splitter = QSplitter()
        main_splitter.setOrientation(Qt.Horizontal)
        main_splitter.addWidget(left_splitter)  # Left side: hex map and data table
        main_splitter.addWidget(self.tab_widget)  # Right side: text display

        # Set the sizes to give the left part (hex map + data table) more space than the text display
        main_splitter.setSizes([int(self.width() * 0.75), int(self.width() * 0.25)])  # Set proportions (800px to left, 400px to right)

        # Add the main splitter to the central layout
        main_layout.addWidget(main_splitter)
    

        # Set central widget
        self.setCentralWidget(central_widget)

        # Create and add the status bar
        self.statusBar().showMessage("Ready")  # Show a default message when the app starts

    def save_game_data(self):
        """Open a save file dialog and save the persistent game data."""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            caption="Save Persistent Game Data",
            filter="JSON Files (*.json)"
        )
        if filename:
            self.data_manager.save_persistent_data_to_file(filename)
            # Optionally, show a confirmation message to the user
            QMessageBox.information(self, "Save Successful", f"Game data saved to {filename}.")

    def load_game_data(self):
        """Open a load file dialog and load the persistent game data."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            caption="Load Persistent Game Data",
            filter="JSON Files (*.json)"
        )
        if filename:
            self.data_manager.load_persistent_data_from_file(filename)
            # Update UI components after loading new data
            self.hex_map_view.load_map_data(self.data_manager.get_regions())
            # Optionally refresh other UI elements
            self.refresh_ui()
            # Optionally, show a confirmation message to the user
            QMessageBox.information(self, "Load Successful", f"Game data loaded from {filename}.")

    

    def toggle_hex_coords(self):
        """Toggle the hex coordinates labels on and off."""
        self.hex_map_view.toggle_hex_labels()

    def update_status_bar(self, message):
        """Update the status bar with a message."""
        self.statusBar().showMessage(message)
    
    def display_hex_data(self, hex_data):
        """Display hex-specific data (including settlement data) in the text_display widget with a modern HTML/CSS layout."""
        self.hex_data_tab.clear()  # Clear previous content
        self.orders_tab.setRowCount(0)

        # Read CSS content from the external file
        css_file_path = os.path.join(os.path.dirname(__file__), 'hexdata.css')
        try:
            with open(css_file_path, 'r', encoding='utf-8') as css_file:
                css_content = css_file.read()
        except FileNotFoundError:
            print(f"CSS file not found at {css_file_path}")
            css_content = ""  # Fallback to empty CSS if file not found

        # Start assembling HTML content
        html_content = f"""
        <html>
        <head>
        <style>
        {css_content}
        </style>
        </head>
        <body>
        """

        # Display basic hex information
        coordinates = hex_data.get('coordinates', {})
        x = coordinates.get('x', 'Unknown')
        y = coordinates.get('y', 'Unknown')

        self.statusBar().showMessage(f"Hex: ({x}, {y})")  # Show coordinates in status bar

        # Display terrain type
        terrain = hex_data.get('terrain', 'Unknown')
        province = hex_data.get('province', 'Unknown')
        province = province.capitalize()
        population = hex_data.get('population', {})
        population_amount = population.get('amount', 'N/A')
        population_race = population.get('race', 'N/A')
        tax = hex_data.get('tax', 'N/A')
        wages = hex_data.get('wages', {})
        wages_amount = wages.get('amount', 'N/A')
        wages_max = wages.get('max', 'N/A')
        entertainment = hex_data.get('entertainment', 'N/A')

        

        html_content += f"""
        <div class="section">
            <p><h2>{terrain} ({x}, {y}) in {province}</h2></p>
            <hr>
           
        </div>
        """
        
        # Display settlement information
        settlement = hex_data.get('settlement')
        if settlement:
            settlement_name = settlement.get('name', 'Unknown')
            settlement_size = settlement.get('size', 'Unknown')
            
            html_content += f"""
            <div class="section">
                <p><b>Contains:</b> {settlement_name} ({settlement_size})</p>
            </div>
            """
       
        html_content += f"""
        <div class="section">
            <p><b>Tax Rate:</b> {tax if tax != 'N/A' else 'Not available'}</p>
            <p><b>Max Wages:</b>  {wages_amount} (Max: {wages_max})</p>
            <p><b>Population:</b> {population_amount} ({population_race}))</p>
            <p><b>Entertainment available:</b> {entertainment}</p>
        </div>
        """

       # Display products
        products = hex_data.get('products', [])
        
        if products:
            html_content += """
            <div class="section">
                <h2>Products</h2>
                <table>
                    <tr>
                        <th>Product</th>
                        <th>Amount</th>
                    </tr>
            """
            for product in products:
                product_name = product.get('name', 'Unknown Product')
                product_amount = product.get('amount', 'N/A')
                
                html_content += f"""
                    <tr>
                        <td>{product_name}</td>
                        <td>{product_amount}</td>
                    </tr>
                """
            html_content += """
                </table>
            </div>
            """
        else:
            html_content += """
            <div class="section">
                <h2>Products</h2>
                <p>None</p>
            </div>
            """
            
        # Display market information (for_sale and wanted)
        markets = hex_data.get('markets', {})

        for_sale = markets.get('for_sale', [])
        wanted = markets.get('wanted', [])

        if for_sale or wanted:
            # Remove the side-by-side class from the div
            html_content += """
            <div class="section">
            """
            
            if for_sale:
                html_content += """
                <div class="table-container">
                    <h2>For Sale</h2>
                    <table>
                        <tr>
                            <th>Item</th>
                            <th>Amount</th>
                            <th>Price (silver)</th>
                        </tr>
                """
                for item in for_sale:
                    item_name = item.get('name', 'Unknown Item')
                    item_amount = item.get('amount', 'N/A')
                    item_price = item.get('price', 'N/A')
                    
                    html_content += f"""
                        <tr>
                            <td>{item_name}</td>
                            <td>{item_amount}</td>
                            <td>{item_price}</td>
                        </tr>
                    """
                html_content += """
                    </table>
                </div>
                """
            else:

                html_content += """
                <div class="table-container">
                    <h2>For Sale</h2>
                    <p>None</p>
                </div>
                """
            
            if wanted:
                html_content += """
                <div class="table-container">
                    <h2>Wanted</h2>
                    <table>
                        <tr>
                            <th>Item</th>
                            <th>Amount</th>
                            <th>Price (silver)</th>
                        </tr>
                """
                for item in wanted:
                    item_name = item.get('name', 'Unknown Item')
                    item_amount = item.get('amount', 'N/A')
                    item_price = item.get('price', 'N/A')

                    html_content += f"""
                        <tr>
                            <td>{item_name}</td>
                            <td>{item_amount}</td>
                            <td>{item_price}</td>
                        </tr>
                    """
                html_content += """
                    </table>
                </div>
                """
            else:

                html_content += """
                <div class="table-container">
                    <h2>Wanted</h2>
                    <p>None</p>
                </div>
                """
            
            html_content += """
            </div> <!-- End of section div -->
            """
        else:
            # If neither for_sale nor wanted have items
            html_content += """
            <div class="section">
                <h2>Market</h2>
                <p>No market information available.</p>
            </div>
            """
        


        # Close HTML tags
        html_content += """
        </body>
        </html>
        """

        # Set the HTML content to the text_display widget
        self.hex_data_tab.setHtml(html_content)

        # Now, populate the Orders tab
        self.populate_orders_tab(hex_data)

        # Populate the Events tab
        self.populate_events_tab(hex_data)

    def populate_orders_tab(self, hex_data):
        """Populate the Orders tab with orders from units in the hex."""
        self.orders_tab.setRowCount(0)
        self.orders_tab.setColumnCount(2)
        self.orders_tab.setHorizontalHeaderLabels(["Unit Name", "Order"])

        # Collect all orders from units
        orders = []
        units = hex_data.get('units', [])
        for unit in units:
            unit_name = unit.get('name', 'Unknown Unit')
            unit_orders = unit.get('orders', [])
            for order in unit_orders:
                order_text = order.get('order', 'No Order Description')
                orders.append((unit_name, order_text))

        if orders:
            self.orders_tab.setRowCount(len(orders))
            for row, (unit_name, order_text) in enumerate(orders):
                # Unit Name
                unit_item = QTableWidgetItem(unit_name)
                unit_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.orders_tab.setItem(row, 0, unit_item)

                # Order
                order_item = QTableWidgetItem(order_text)
                order_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.orders_tab.setItem(row, 1, order_item)

                print(f"Set Orders tab row {row}: Unit='{unit_name}', Order='{order_text}'")
        else:
            # No orders to display
            self.orders_tab.setRowCount(1)
            self.orders_tab.setItem(0, 0, QTableWidgetItem("No Orders"))
            self.orders_tab.setItem(0, 1, QTableWidgetItem(""))
            print("No orders to display in Orders tab.")

        # Adjust the table for better readability
        self.orders_tab.resizeColumnsToContents()
        self.orders_tab.horizontalHeader().setStretchLastSection(True)
        self.orders_tab.setSortingEnabled(True)

        # Optionally, set alignment for all cells
        for row in range(self.orders_tab.rowCount()):
            for col in range(self.orders_tab.columnCount()):
                item = self.orders_tab.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    def populate_events_tab(self, hex_data):
        """
        Populate the Events tab with event data from the selected hex.
        
        Args:
            hex_data (dict): The data associated with the selected hex tile.
        """
        coordinates = hex_data.get('coordinates', {})
        x = coordinates.get('x')
        y = coordinates.get('y')
        
        if x is None or y is None:
            print(f"Warning: Invalid coordinates in hex_data: {coordinates}")
            return

        # -----------------------------
        # 1. Fetch Region-Based Events
        # -----------------------------
        region_events = self.data_manager.get_events_for_region(x, y)

        # -----------------------------
        # 2. Fetch Unit-Based Events
        # -----------------------------
        units = hex_data.get('units', [])
        unit_numbers = [unit.get('number') for unit in units if unit.get('number') is not None]
        
        if not unit_numbers:
            print(f"No units found in hex ({x}, {y}).")
            unit_events = []
        else:
            unit_events = self.data_manager.get_events_for_units(unit_numbers)

        # -----------------------------
        # 3. Combine Events
        # -----------------------------
        combined_events = region_events + unit_events

        print(f"Found {len(combined_events)} events for region ({x}, {y})")  # Debug statement

        # -----------------------------
        # 4. Populate the Events Table
        # -----------------------------
        self.events_tab.clearContents()  # Clear previous content
        self.events_tab.setRowCount(0)   # Reset the table

        if combined_events:
            self.events_tab.setRowCount(len(combined_events))
            self.events_tab.setColumnCount(3)  # Category, Message, Unit, Region
            self.events_tab.setHorizontalHeaderLabels([ "Unit", "Category", "Message"])

            for row, event in enumerate(combined_events):
                # Category
                category = event.get('category', 'N/A').capitalize()
                category_item = QTableWidgetItem(category)
                category_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
               

                # Message
                message = event.get('message', 'No message provided.')
                message_item = QTableWidgetItem(message)
                message_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

                # Unit
                unit = event.get('unit')
                if unit:
                    unit_name = unit.get('name', 'Unknown Unit')
                    unit_number = unit.get('number', 'N/A')
                    unit_text = f"{unit_name} (#{unit_number})"
                else:
                    unit_text = "N/A"
                unit_item = QTableWidgetItem(unit_text)
                unit_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                

                # Region
                region = event.get('region')
                if region:
                    terrain = region.get('terrain', 'Unknown Terrain')
                    province = region.get('province', 'Unknown Province')
                    coordinates = region.get('coordinates', {})
                    rx = coordinates.get('x', 'N/A')
                    ry = coordinates.get('y', 'N/A')
                    rz = coordinates.get('z', 'N/A')
                    location_text = f"{terrain.capitalize()} ({rx}, {ry}, {rz}) in {province}"
                else:
                    location_text = "N/A"
                region_item = QTableWidgetItem(location_text)
                region_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                
                self.events_tab.setItem(row, 0, unit_item)
                self.events_tab.setItem(row, 1, category_item)
                self.events_tab.setItem(row, 2, message_item)
                
                print(f"Set Events tab row {row}: Category='{category}', Message='{message}', Unit='{unit_text}', Region='{location_text}'")
        else:
            # No events to display
            self.events_tab.setRowCount(1)
            self.events_tab.setSpan(0, 0, 1, 4)  # Span across all columns
            no_event_item = QTableWidgetItem("No events to display.")
            no_event_item.setTextAlignment(Qt.AlignCenter)
            self.events_tab.setItem(0, 0, no_event_item)

        # -----------------------------
        # 5. Final Adjustments
        # -----------------------------
        self.events_tab.resizeColumnsToContents()
        self.events_tab.horizontalHeader().setStretchLastSection(True)
        self.events_tab.setSortingEnabled(True)

        # Optionally, set alignment for all cells
        for row in range(self.events_tab.rowCount()):
            for col in range(self.events_tab.columnCount()):
                item = self.events_tab.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)


    def open_turn_report(self):
        """Open a turn report file and load its data into the application."""
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
            self.update_views()
        else:
            self.statusBar().showMessage("No file selected")
            QMessageBox.warning(self, 'No File', 'No file was selected.')

    def update_views(self):
        """Update the hex map view with the latest region data."""
        regions = self.data_manager.get_regions()
        self.hex_map_view.load_map_data(regions)
        self.display_parsed_data()

    def display_parsed_data(self):
        """Display faction, date, and engine information in the hex_data_tab widget."""
        # Display faction information
        faction_info = self.data_manager.get_faction_info()
        self.hex_data_tab.append(f"Faction: {faction_info['name']} [{faction_info['number']}]")

        # Display date information
        date_info = self.data_manager.get_date_info()
        self.hex_data_tab.append(f"Date: {date_info['month']}, Year {date_info['year']}")

        # Display engine information
        engine_info = self.data_manager.get_engine_info()
        self.hex_data_tab.append(f"Engine: {engine_info['ruleset']} {engine_info['ruleset_version']}, Version {engine_info['version']}")

        # Display attitudes
        attitudes = self.data_manager.get_attitudes()
        self.hex_data_tab.append(f"Default Attitude: {attitudes['default']}")

        # Display administrative settings
        admin_settings = self.data_manager.get_administrative_settings()
        self.hex_data_tab.append(f"Password Unset: {admin_settings['password_unset']}")
        self.hex_data_tab.append(f"Show Unit Attitudes: {admin_settings['show_unit_attitudes']}")
        self.hex_data_tab.append(f"Times Sent: {admin_settings['times_sent']}")

    def show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            'About PyLantir',
            'PyLantir\n\nAn open-source client for the Atlantis PBEM game.\n\nDeveloped by J. Stuart Brown.'
        )

    def closeEvent(self, event):
        """Save persistent data when the application is closed."""
        self.data_manager.save_persistent_data('persistent_map_data.json')
        super().closeEvent(event)


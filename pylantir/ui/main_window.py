import json
from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QLineEdit, QTextEdit, QWidget, QVBoxLayout, QTableWidget, QSplitter
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
                color: white;  /* Set the text color to white */
            }
        """)

        self.hex_map_view = HexMapView(self.data_manager, self.data_table)
        self.hex_map_view.setStyleSheet("background-color: #1F1F1F; border: 1px solid grey;")
        self.hex_map_view.report_loaded.connect(self.update_status_bar)
        self.hex_map_view.hex_selected.connect(self.display_hex_data)


        self.text_display = QTextEdit()
        self.text_display.setStyleSheet("background-color: #191919; color: white; border: 1px solid grey; padding: 10px;")  # Set the background color to dark grey and text color to white
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
        """Update the status bar with a message."""
        self.statusBar().showMessage(message)
    
    def display_hex_data(self, hex_data):
        """Display hex-specific data (including settlement data) in the text_display widget with a modern HTML/CSS layout."""
        self.text_display.clear()  # Clear previous content

        # Print the entire hex data for debugging
        print("Debug: Full hex data being loaded:", hex_data)

        # Read CSS content from the external file
        css_file_path = os.path.join(os.path.dirname(__file__), 'styles.css')
        try:
            with open(css_file_path, 'r', encoding='utf-8') as css_file:
                css_content = css_file.read()
        except FileNotFoundError:
            print(f"Debug: CSS file not found at {css_file_path}")
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

        print(f"Debug: Hex Coordinates: {x}, {y}")  # Debug output

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
       

        print(f"Debug: Population: {population}")  # Debug output
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
        print(f"Debug: Products: {products}")  # Debug output
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
                print(f"Debug: Product: {product}")  # Debug output
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
        print(f"Debug: Markets: {markets}")  # Debug output
        for_sale = markets.get('for_sale', [])
        wanted = markets.get('wanted', [])

        if for_sale or wanted:
            html_content += """
            <div class="section side-by-side">
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
                    print(f"Debug: For Sale Item: {item}")  # Debug output
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
                print("Debug: No items for sale")  # Debug output
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
                    print(f"Debug: Wanted Item: {item}")  # Debug output
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
                print("Debug: No wanted items")  # Debug output
                html_content += """
                <div class="table-container">
                    <h2>Wanted</h2>
                    <p>None</p>
                </div>
                """
            
            html_content += """
            </div> <!-- End of side-by-side div -->
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
        self.text_display.setHtml(html_content)


    
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
        """Display faction, date, and engine information in the text_display widget."""
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

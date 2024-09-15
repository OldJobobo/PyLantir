import json
from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QLineEdit, QTextEdit, QWidget, QHBoxLayout, QVBoxLayout, QTableWidget, QTableWidgetItem, QSplitter
from PySide6.QtGui import QAction, QIcon, Qt

from ..views.hex_map import HexMapView  # We will create this later
from ..data.data_manager import DataManager

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
        self.data_table.setRowCount(5)  # Set initial row count
        self.data_table.setColumnCount(8)  # Set initial column count
        self.data_table.setHorizontalHeaderLabels(['Faction', 'Faction Nr', 'Unit Nr', 'Unit Name','Men', 'Silver', 'Horses', 'Skills' ])

        self.hex_map_view = HexMapView(self.data_table)
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)  # Make the text display read-only

        # Create a layout for the map and text display
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.hex_map_view)
        top_layout.addWidget(self.text_display)

        # Create a QSplitter for the top layout and data table
        splitter = QSplitter()
        splitter.setOrientation(Qt.Vertical)

        # Create a widget to hold the top layout
        top_widget = QWidget()
        top_widget.setLayout(top_layout)

        # Add the top widget and data table to the splitter
        splitter.addWidget(top_widget)
        splitter.addWidget(self.data_table)

        # Add the splitter to the main layout
        main_layout.addWidget(splitter)

        # Set central widget
        self.setCentralWidget(central_widget)

    def open_turn_report(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(
            self,
            'Open JSON Turn Report',
            '',
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

            QMessageBox.information(self, 'File Loaded', f'Loaded report: {filename}')
        else:
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
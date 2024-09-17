# pylantir/main.py

import sys
from PySide6.QtWidgets import QApplication
from pylantir.ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.showMaximized() 

    sys.exit(app.exec())

if __name__ == '__main__':
    main()

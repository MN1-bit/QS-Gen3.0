import sys
import os

# Add project root to python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtWidgets import QApplication
from qfluentwidgets import setTheme, Theme
from gui.mainwindow import TradingMainWindow

def main():
    app = QApplication(sys.argv)
    
    # Set Theme (Auto sync with system)
    setTheme(Theme.AUTO)
    
    # Create Main Window
    w = TradingMainWindow()
    w.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()


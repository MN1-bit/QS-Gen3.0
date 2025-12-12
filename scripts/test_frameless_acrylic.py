"""
Frameless Acrylic Window Test.
Uses FramelessWindow from qframelesswindow with proper transparency.
"""
import sys
import ctypes

from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from qframelesswindow import FramelessWindow, StandardTitleBar

# DWM API
DWMWA_USE_IMMERSIVE_DARK_MODE = 20
DWMWA_SYSTEMBACKDROP_TYPE = 38
DWMSBT_TRANSIENTWINDOW = 3  # Acrylic


def apply_acrylic(hwnd: int) -> bool:
    try:
        dwmapi = ctypes.windll.dwmapi
        
        # Dark mode
        dark = ctypes.c_int(1)
        dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
                                     ctypes.byref(dark), ctypes.sizeof(dark))
        
        # Acrylic
        backdrop = ctypes.c_int(DWMSBT_TRANSIENTWINDOW)
        result = dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_SYSTEMBACKDROP_TYPE,
                                              ctypes.byref(backdrop), ctypes.sizeof(backdrop))
        print(f"Acrylic applied: {result == 0}")
        return result == 0
    except Exception as e:
        print(f"Error: {e}")
        return False


class AcrylicFramelessWindow(FramelessWindow):
    """Frameless window with Acrylic effect"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QS-Gen3.0 - Frameless Acrylic")
        self.resize(1000, 700)
        
        # Use qframelesswindow's built-in window effect
        self.windowEffect.setAcrylicEffect(self.winId(), "00000050")
        
        # Create UI
        self._createUI()
        
    def _createUI(self):
        # Title bar
        self.setTitleBar(StandardTitleBar(self))
        self.titleBar.setStyleSheet("background: transparent;")
        
        # Central content
        central = QWidget(self)
        central.setStyleSheet("background: transparent;")
        
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 60, 20, 20)  # Top margin for title bar
        
        # Header
        header = QLabel("QS-Gen3.0")
        header.setStyleSheet("color: white; font-size: 32px; font-weight: bold; background: transparent;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Subtitle
        sub = QLabel("Frameless Acrylic Window Test")
        sub.setStyleSheet("color: #aaa; font-size: 16px; background: transparent;")
        sub.setAlignment(Qt.AlignCenter)
        layout.addWidget(sub)
        
        # Buttons
        btn_row = QHBoxLayout()
        for text in ["Dashboard", "Chart", "Positions", "Settings"]:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255,255,255,20);
                    color: white;
                    border: 1px solid rgba(255,255,255,40);
                    border-radius: 6px;
                    padding: 12px 24px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: rgba(255,255,255,40);
                }
            """)
            btn_row.addWidget(btn)
        layout.addLayout(btn_row)
        
        layout.addStretch()
        
        # Info
        info = QLabel("If you see blurred background, Acrylic is working!")
        info.setStyleSheet("color: #666; font-size: 12px; background: transparent;")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)
        
        # Set as central content (below title bar)
        self.hBoxLayout = QVBoxLayout(self)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(central)


def main():
    app = QApplication(sys.argv)
    window = AcrylicFramelessWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

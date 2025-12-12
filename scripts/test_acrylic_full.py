"""
Acrylic Test with Full Window Effect - Not just title bar.
Using transparent window background to let Acrylic show through.
"""
import sys
import ctypes
from ctypes import wintypes

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, 
    QWidget, QHBoxLayout, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette

# DWM API Constants
DWMWA_USE_IMMERSIVE_DARK_MODE = 20
DWMWA_SYSTEMBACKDROP_TYPE = 38
DWMWA_CAPTION_COLOR = 35

# Backdrop types
DWMSBT_MAINWINDOW = 2      # Mica
DWMSBT_TRANSIENTWINDOW = 3  # Acrylic


def apply_acrylic_full(hwnd: int) -> bool:
    """Apply Acrylic effect with proper window setup"""
    try:
        dwmapi = ctypes.windll.dwmapi
        
        # Enable dark mode
        dark_value = ctypes.c_int(1)
        dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(dark_value), ctypes.sizeof(dark_value)
        )
        
        # Apply Acrylic backdrop
        backdrop_value = ctypes.c_int(DWMSBT_TRANSIENTWINDOW)
        result = dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_SYSTEMBACKDROP_TYPE,
            ctypes.byref(backdrop_value), ctypes.sizeof(backdrop_value)
        )
        
        print(f"Acrylic result: {result}")
        return result == 0
    except Exception as e:
        print(f"Error: {e}")
        return False


class AcrylicWindow(QMainWindow):
    """Window with proper Acrylic effect setup"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QS-Gen3.0 - Acrylic Test")
        self.resize(1000, 700)
        
        # CRITICAL: Set window to be translucent
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # Create central widget with semi-transparent background
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)
        
        # Semi-transparent dark background - lets Acrylic show through
        central.setStyleSheet("""
            #centralWidget {
                background-color: rgba(30, 30, 30, 200);
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("QS-Gen3.0 Retail Quant System")
        header.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
                background: transparent;
            }
        """)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Status
        status = QLabel("✓ Acrylic Effect Active")
        status.setStyleSheet("""
            QLabel {
                color: #00ff88;
                font-size: 16px;
                background: transparent;
            }
        """)
        status.setAlignment(Qt.AlignCenter)
        layout.addWidget(status)
        
        # Buttons row
        btn_layout = QHBoxLayout()
        for text in ["Dashboard", "Live Chart", "Settings"]:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 30);
                    color: white;
                    border: 1px solid rgba(255, 255, 255, 50);
                    border-radius: 5px;
                    padding: 10px 20px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 50);
                }
            """)
            btn_layout.addWidget(btn)
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        
        # Info
        info = QLabel("If you can see blurred desktop through this window, Acrylic is working!")
        info.setStyleSheet("color: #888; font-size: 12px; background: transparent;")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)
        
    def showEvent(self, event):
        super().showEvent(event)
        hwnd = int(self.winId())
        print(f"HWND: {hwnd}")
        apply_acrylic_full(hwnd)


def main():
    app = QApplication(sys.argv)
    window = AcrylicWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

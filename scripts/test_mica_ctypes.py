"""
Mica Effect Test using ctypes DWM API directly.
This bypasses FluentWindow and calls Windows DWM API directly.
"""
import sys
import ctypes
from ctypes import wintypes

from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

# DWM API Constants
DWMWA_USE_IMMERSIVE_DARK_MODE = 20
DWMWA_SYSTEMBACKDROP_TYPE = 38

# Backdrop types
DWMSBT_AUTO = 0
DWMSBT_NONE = 1
DWMSBT_MAINWINDOW = 2      # Mica
DWMSBT_TRANSIENTWINDOW = 3  # Acrylic
DWMSBT_TABBEDWINDOW = 4     # Mica Alt


def apply_mica(hwnd: int, dark_mode: bool = True) -> bool:
    """Apply Mica effect using DwmSetWindowAttribute"""
    try:
        dwmapi = ctypes.windll.dwmapi
        
        # Set dark mode first
        dark_value = ctypes.c_int(1 if dark_mode else 0)
        dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(dark_value),
            ctypes.sizeof(dark_value)
        )
        
        # Apply Mica backdrop
        backdrop_value = ctypes.c_int(DWMSBT_MAINWINDOW)
        result = dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_SYSTEMBACKDROP_TYPE,
            ctypes.byref(backdrop_value),
            ctypes.sizeof(backdrop_value)
        )
        
        print(f"DwmSetWindowAttribute result: {result} (0 = success)")
        return result == 0
    except Exception as e:
        print(f"Failed to apply Mica: {e}")
        return False


def apply_acrylic(hwnd: int, dark_mode: bool = True) -> bool:
    """Apply Acrylic effect (alternative to Mica)"""
    try:
        dwmapi = ctypes.windll.dwmapi
        
        # Set dark mode
        dark_value = ctypes.c_int(1 if dark_mode else 0)
        dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(dark_value),
            ctypes.sizeof(dark_value)
        )
        
        # Apply Acrylic backdrop
        backdrop_value = ctypes.c_int(DWMSBT_TRANSIENTWINDOW)
        result = dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_SYSTEMBACKDROP_TYPE,
            ctypes.byref(backdrop_value),
            ctypes.sizeof(backdrop_value)
        )
        
        print(f"Acrylic DwmSetWindowAttribute result: {result}")
        return result == 0
    except Exception as e:
        print(f"Failed to apply Acrylic: {e}")
        return False


class MicaTestWindow(QMainWindow):
    """Simple test window to verify Mica/Acrylic effects"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mica/Acrylic Test - QS-Gen3.0")
        self.resize(800, 600)
        
        # Transparent central widget for Mica to show through
        central = QWidget()
        central.setStyleSheet("background: transparent;")
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        
        label = QLabel("Testing Windows 11 Mica/Acrylic Effect")
        label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }
        """)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        info_label = QLabel("If you see blurred desktop background, the effect is working!")
        info_label.setStyleSheet("color: #aaa; font-size: 14px; background: transparent;")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
    def showEvent(self, event):
        super().showEvent(event)
        hwnd = int(self.winId())
        print(f"Window HWND: {hwnd}")
        
        # Try Acrylic first (more compatible)
        print("Attempting Acrylic effect...")
        if not apply_acrylic(hwnd, dark_mode=True):
            print("Acrylic failed, trying Mica...")
            apply_mica(hwnd, dark_mode=True)


def main():
    app = QApplication(sys.argv)
    
    # Set app-wide transparent palette
    app.setStyle("Fusion")
    
    window = MicaTestWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

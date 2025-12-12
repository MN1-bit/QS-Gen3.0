"""
ConnectionWidget: Displays broker connection status.

Shows connection state with LED indicator and reconnect button.
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QColor


class ConnectionWidget(QWidget):
    """Widget displaying IBKR connection status."""
    
    # Signals
    reconnect_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._status = "disconnected"
        
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        # Status LED indicator
        self._led = QLabel("●")
        self._led.setStyleSheet("font-size: 16px; color: #ff4444;")  # Red = disconnected
        layout.addWidget(self._led)
        
        # Status text
        self._status_label = QLabel("Disconnected")
        self._status_label.setStyleSheet("font-size: 13px; color: #888;")
        layout.addWidget(self._status_label)
        
        layout.addStretch()
        
        # Broker name
        self._broker_label = QLabel("IBKR")
        self._broker_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #aaa;")
        layout.addWidget(self._broker_label)
        
        # Reconnect button
        self._reconnect_btn = QPushButton("Reconnect")
        self._reconnect_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 20);
                color: #aaa;
                border: 1px solid rgba(255, 255, 255, 40);
                border-radius: 4px;
                padding: 5px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 40);
                color: white;
            }
        """)
        self._reconnect_btn.clicked.connect(self.reconnect_requested.emit)
        layout.addWidget(self._reconnect_btn)
        
    @property
    def status(self) -> str:
        return self._status
        
    @Slot(str)
    def set_status(self, status: str):
        """
        Update connection status.
        
        Args:
            status: "connected", "disconnected", or "reconnecting"
        """
        self._status = status
        
        if status == "connected":
            self._led.setStyleSheet("font-size: 16px; color: #44ff44;")  # Green
            self._status_label.setText("Connected")
            self._status_label.setStyleSheet("font-size: 13px; color: #44ff44;")
            self._reconnect_btn.setEnabled(False)
        elif status == "reconnecting":
            self._led.setStyleSheet("font-size: 16px; color: #ffaa44;")  # Orange
            self._status_label.setText("Reconnecting...")
            self._status_label.setStyleSheet("font-size: 13px; color: #ffaa44;")
            self._reconnect_btn.setEnabled(False)
        else:  # disconnected
            self._led.setStyleSheet("font-size: 16px; color: #ff4444;")  # Red
            self._status_label.setText("Disconnected")
            self._status_label.setStyleSheet("font-size: 13px; color: #ff4444;")
            self._reconnect_btn.setEnabled(True)
            
    @Slot()
    def set_connected(self):
        """Shortcut to set connected status."""
        self.set_status("connected")
        
    @Slot()
    def set_disconnected(self):
        """Shortcut to set disconnected status."""
        self.set_status("disconnected")

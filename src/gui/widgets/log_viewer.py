"""
Log Viewer Widget.

Displays application logs in real-time with filtering.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QLabel, QComboBox, QPushButton, QLineEdit
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QTextCharFormat, QColor, QFont
from datetime import datetime
from typing import List


class LogViewer(QWidget):
    """
    Widget for viewing application logs.
    
    Supports filtering by log level and search.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("logViewer")
        self._log_entries: List[dict] = []
        self._setup_ui()
        self._add_demo_logs()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header = QHBoxLayout()
        
        title = QLabel("Log Viewer")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ddd;")
        header.addWidget(title)
        
        header.addStretch()
        
        # Filter by level
        level_label = QLabel("Level:")
        level_label.setStyleSheet("color: #aaa;")
        header.addWidget(level_label)
        
        self._level_combo = QComboBox()
        self._level_combo.addItems(["ALL", "DEBUG", "INFO", "WARNING", "ERROR"])
        self._level_combo.setStyleSheet("""
            QComboBox {
                background: rgba(255, 255, 255, 10);
                color: white;
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 4px;
                padding: 5px 10px;
                min-width: 100px;
            }
        """)
        self._level_combo.currentTextChanged.connect(self._filter_logs)
        header.addWidget(self._level_combo)
        
        # Search
        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText("Search logs...")
        self._search_edit.setStyleSheet("""
            QLineEdit {
                background: rgba(255, 255, 255, 10);
                color: white;
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 4px;
                padding: 5px 10px;
                min-width: 200px;
            }
        """)
        self._search_edit.textChanged.connect(self._filter_logs)
        header.addWidget(self._search_edit)
        
        # Clear button
        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet("""
            QPushButton {
                background: rgba(239, 83, 80, 80);
                color: #ef5350;
                border: 1px solid #ef5350;
                border-radius: 4px;
                padding: 5px 12px;
            }
            QPushButton:hover {
                background: rgba(239, 83, 80, 120);
            }
        """)
        clear_btn.clicked.connect(self._clear_logs)
        header.addWidget(clear_btn)
        
        layout.addLayout(header)
        
        # Log display
        self._log_display = QTextEdit()
        self._log_display.setReadOnly(True)
        self._log_display.setStyleSheet("""
            QTextEdit {
                background: #0d0d14;
                color: #ddd;
                border: 1px solid rgba(255, 255, 255, 20);
                border-radius: 4px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                padding: 10px;
            }
        """)
        layout.addWidget(self._log_display)
        
    def _add_demo_logs(self):
        """Add demo log entries."""
        demo_logs = [
            {"level": "INFO", "message": "Application started", "source": "main"},
            {"level": "INFO", "message": "Connecting to TWS at 127.0.0.1:7497", "source": "ibkr_bridge"},
            {"level": "INFO", "message": "Connection established", "source": "ibkr_bridge"},
            {"level": "DEBUG", "message": "Received nextValidId: 1", "source": "ibkr_bridge"},
            {"level": "INFO", "message": "Account: DUM425288", "source": "ibkr_bridge"},
            {"level": "WARNING", "message": "Market data farm connection is slow", "source": "ibkr_bridge"},
            {"level": "ERROR", "message": "Order rejected: Insufficient funds", "source": "order_manager"},
            {"level": "INFO", "message": "Strategy 'MeanReversion' started", "source": "strategy"},
        ]
        
        for log in demo_logs:
            self.add_log(log["level"], log["message"], log["source"])
            
    def _get_level_color(self, level: str) -> str:
        """Get color for log level."""
        colors = {
            "DEBUG": "#888888",
            "INFO": "#26a69a",
            "WARNING": "#ffb74d",
            "ERROR": "#ef5350",
        }
        return colors.get(level, "#ddd")
        
    @Slot(str, str, str)
    def add_log(self, level: str, message: str, source: str = "app"):
        """
        Add a new log entry.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR)
            message: Log message
            source: Log source/module
        """
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message,
            "source": source,
        }
        self._log_entries.append(entry)
        self._display_log(entry)
        
    def _display_log(self, entry: dict):
        """Display a log entry in the text area."""
        color = self._get_level_color(entry["level"])
        formatted = f'<span style="color:#666">[{entry["timestamp"]}]</span> '
        formatted += f'<span style="color:{color}">[{entry["level"]:>7}]</span> '
        formatted += f'<span style="color:#888">{entry["source"]:>15}</span> | '
        formatted += f'<span style="color:#ddd">{entry["message"]}</span>'
        
        self._log_display.append(formatted)
        
    def _filter_logs(self):
        """Filter logs based on level and search text."""
        level_filter = self._level_combo.currentText()
        search_text = self._search_edit.text().lower()
        
        self._log_display.clear()
        
        for entry in self._log_entries:
            if level_filter != "ALL" and entry["level"] != level_filter:
                continue
            if search_text and search_text not in entry["message"].lower():
                continue
            self._display_log(entry)
            
    def _clear_logs(self):
        """Clear all logs."""
        self._log_entries.clear()
        self._log_display.clear()

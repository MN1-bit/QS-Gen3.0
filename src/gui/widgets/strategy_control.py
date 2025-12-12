"""
Strategy Control Widget.

Provides start/stop controls for trading strategies.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGroupBox, QComboBox
)
from PySide6.QtCore import Qt, Signal, Slot


class StrategyControl(QWidget):
    """
    Widget for controlling trading strategies.
    
    Allows starting and stopping strategies.
    """
    
    # Signals
    strategy_start_requested = Signal(str)  # Strategy name
    strategy_stop_requested = Signal(str)   # Strategy name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("strategyControl")
        self._strategy_running = False
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Strategy Control")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ddd;")
        layout.addWidget(title)
        
        # Strategy selection group
        strategy_group = QGroupBox("Active Strategy")
        strategy_group.setStyleSheet("""
            QGroupBox {
                color: #ddd;
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 6px;
                margin-top: 10px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        strategy_layout = QVBoxLayout(strategy_group)
        
        # Strategy selector
        selector_layout = QHBoxLayout()
        selector_label = QLabel("Strategy:")
        selector_label.setStyleSheet("color: #aaa;")
        selector_layout.addWidget(selector_label)
        
        self._strategy_combo = QComboBox()
        self._strategy_combo.addItems([
            "Mean Reversion",
            "Momentum",
            "Breakout",
            "Custom Strategy"
        ])
        self._strategy_combo.setStyleSheet("""
            QComboBox {
                background: rgba(255, 255, 255, 10);
                color: white;
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 4px;
                padding: 8px 15px;
                min-width: 200px;
            }
        """)
        selector_layout.addWidget(self._strategy_combo)
        selector_layout.addStretch()
        strategy_layout.addLayout(selector_layout)
        
        # Status
        self._status_label = QLabel("Status: Stopped")
        self._status_label.setStyleSheet("color: #ef5350; font-size: 14px;")
        strategy_layout.addWidget(self._status_label)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self._start_btn = QPushButton("▶ Start Strategy")
        self._start_btn.setStyleSheet("""
            QPushButton {
                background: rgba(38, 166, 154, 100);
                color: #26a69a;
                border: 1px solid #26a69a;
                border-radius: 6px;
                padding: 12px 25px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(38, 166, 154, 150);
            }
            QPushButton:disabled {
                background: rgba(100, 100, 100, 50);
                color: #666;
                border-color: #666;
            }
        """)
        self._start_btn.clicked.connect(self._on_start_clicked)
        button_layout.addWidget(self._start_btn)
        
        self._stop_btn = QPushButton("■ Stop Strategy")
        self._stop_btn.setEnabled(False)
        self._stop_btn.setStyleSheet("""
            QPushButton {
                background: rgba(239, 83, 80, 100);
                color: #ef5350;
                border: 1px solid #ef5350;
                border-radius: 6px;
                padding: 12px 25px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(239, 83, 80, 150);
            }
            QPushButton:disabled {
                background: rgba(100, 100, 100, 50);
                color: #666;
                border-color: #666;
            }
        """)
        self._stop_btn.clicked.connect(self._on_stop_clicked)
        button_layout.addWidget(self._stop_btn)
        
        button_layout.addStretch()
        strategy_layout.addLayout(button_layout)
        
        layout.addWidget(strategy_group)
        layout.addStretch()
        
    def _on_start_clicked(self):
        """Handle start button click."""
        strategy_name = self._strategy_combo.currentText()
        print(f"[Strategy] Starting: {strategy_name}")
        
        self._strategy_running = True
        self._update_ui_state()
        self.strategy_start_requested.emit(strategy_name)
        
    def _on_stop_clicked(self):
        """Handle stop button click."""
        strategy_name = self._strategy_combo.currentText()
        print(f"[Strategy] Stopping: {strategy_name}")
        
        self._strategy_running = False
        self._update_ui_state()
        self.strategy_stop_requested.emit(strategy_name)
        
    def _update_ui_state(self):
        """Update UI based on running state."""
        self._start_btn.setEnabled(not self._strategy_running)
        self._stop_btn.setEnabled(self._strategy_running)
        self._strategy_combo.setEnabled(not self._strategy_running)
        
        if self._strategy_running:
            self._status_label.setText("Status: Running ●")
            self._status_label.setStyleSheet("color: #26a69a; font-size: 14px;")
        else:
            self._status_label.setText("Status: Stopped")
            self._status_label.setStyleSheet("color: #ef5350; font-size: 14px;")

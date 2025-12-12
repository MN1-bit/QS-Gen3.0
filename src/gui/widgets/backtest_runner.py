"""
Backtest Runner Widget.

Interface for running backtests and viewing results.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QComboBox, QPushButton, QDateEdit,
    QProgressBar, QFormLayout, QSpinBox
)
from PySide6.QtCore import Qt, Signal, Slot, QDate
from datetime import datetime, timedelta


class BacktestRunner(QWidget):
    """
    Widget for configuring and running backtests.
    """
    
    # Signals
    backtest_started = Signal(dict)   # Backtest config
    backtest_finished = Signal(dict)  # Backtest results
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("backtestRunner")
        self._is_running = False
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Backtest Runner")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ddd;")
        layout.addWidget(title)
        
        # Configuration group
        config_group = QGroupBox("Configuration")
        config_group.setStyleSheet("""
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
        
        config_layout = QFormLayout(config_group)
        config_layout.setSpacing(10)
        
        # Strategy selector
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
            }
        """)
        config_layout.addRow("Strategy:", self._strategy_combo)
        
        # Symbol
        self._symbol_combo = QComboBox()
        self._symbol_combo.addItems(["SPY", "QQQ", "AAPL", "MSFT", "NVDA"])
        self._symbol_combo.setStyleSheet(self._strategy_combo.styleSheet())
        config_layout.addRow("Symbol:", self._symbol_combo)
        
        # Date range
        date_style = """
            QDateEdit {
                background: rgba(255, 255, 255, 10);
                color: white;
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 4px;
                padding: 8px 15px;
            }
        """
        
        self._start_date = QDateEdit()
        self._start_date.setDate(QDate.currentDate().addMonths(-6))
        self._start_date.setCalendarPopup(True)
        self._start_date.setStyleSheet(date_style)
        config_layout.addRow("Start Date:", self._start_date)
        
        self._end_date = QDateEdit()
        self._end_date.setDate(QDate.currentDate())
        self._end_date.setCalendarPopup(True)
        self._end_date.setStyleSheet(date_style)
        config_layout.addRow("End Date:", self._end_date)
        
        # Initial capital
        self._capital_spin = QSpinBox()
        self._capital_spin.setRange(1000, 10000000)
        self._capital_spin.setValue(100000)
        self._capital_spin.setSingleStep(10000)
        self._capital_spin.setPrefix("$")
        self._capital_spin.setStyleSheet("""
            QSpinBox {
                background: rgba(255, 255, 255, 10);
                color: white;
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 4px;
                padding: 8px 15px;
            }
        """)
        config_layout.addRow("Initial Capital:", self._capital_spin)
        
        layout.addWidget(config_group)
        
        # Progress
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setStyleSheet("""
            QProgressBar {
                background: rgba(255, 255, 255, 10);
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 4px;
                height: 20px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background: #26a69a;
                border-radius: 3px;
            }
        """)
        self._progress_bar.setVisible(False)
        layout.addWidget(self._progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self._run_btn = QPushButton("▶ Run Backtest")
        self._run_btn.setStyleSheet("""
            QPushButton {
                background: rgba(38, 166, 154, 100);
                color: #26a69a;
                border: 1px solid #26a69a;
                border-radius: 6px;
                padding: 12px 30px;
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
        self._run_btn.clicked.connect(self._run_backtest)
        button_layout.addWidget(self._run_btn)
        
        self._stop_btn = QPushButton("■ Stop")
        self._stop_btn.setEnabled(False)
        self._stop_btn.setStyleSheet("""
            QPushButton {
                background: rgba(239, 83, 80, 100);
                color: #ef5350;
                border: 1px solid #ef5350;
                border-radius: 6px;
                padding: 12px 30px;
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
        self._stop_btn.clicked.connect(self._stop_backtest)
        button_layout.addWidget(self._stop_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        layout.addStretch()
        
    def _run_backtest(self):
        """Start the backtest."""
        config = {
            "strategy": self._strategy_combo.currentText(),
            "symbol": self._symbol_combo.currentText(),
            "start_date": self._start_date.date().toPython(),
            "end_date": self._end_date.date().toPython(),
            "initial_capital": self._capital_spin.value(),
        }
        
        print(f"[Backtest] Starting: {config}")
        
        self._is_running = True
        self._run_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
        self._progress_bar.setVisible(True)
        self._progress_bar.setValue(50)  # Demo progress
        
        self.backtest_started.emit(config)
        
    def _stop_backtest(self):
        """Stop the backtest."""
        print("[Backtest] Stopped by user")
        
        self._is_running = False
        self._run_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        self._progress_bar.setVisible(False)

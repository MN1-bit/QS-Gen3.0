"""
Order Entry Dialog.

Dialog for placing new orders to IBKR.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QDoubleSpinBox,
    QSpinBox, QGroupBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor


class OrderEntryDialog(QDialog):
    """
    Dialog for entering new orders.
    
    Supports Market, Limit, and Stop orders.
    """
    
    # Signals
    order_submitted = Signal(dict)  # Order details
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Order")
        self.setModal(True)
        self.setMinimumWidth(400)
        self._setup_ui()
        self._apply_style()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Symbol section
        symbol_group = QGroupBox("Symbol")
        symbol_layout = QFormLayout(symbol_group)
        
        self._symbol_edit = QLineEdit()
        self._symbol_edit.setPlaceholderText("e.g., SPY, QQQ, AAPL")
        symbol_layout.addRow("Symbol:", self._symbol_edit)
        
        self._exchange_combo = QComboBox()
        self._exchange_combo.addItems(["SMART", "NYSE", "NASDAQ", "ARCA"])
        symbol_layout.addRow("Exchange:", self._exchange_combo)
        
        layout.addWidget(symbol_group)
        
        # Order details section
        order_group = QGroupBox("Order Details")
        order_layout = QFormLayout(order_group)
        
        self._side_combo = QComboBox()
        self._side_combo.addItems(["BUY", "SELL"])
        order_layout.addRow("Side:", self._side_combo)
        
        self._type_combo = QComboBox()
        self._type_combo.addItems(["MKT", "LMT", "STP", "STP LMT"])
        self._type_combo.currentTextChanged.connect(self._on_order_type_changed)
        order_layout.addRow("Type:", self._type_combo)
        
        self._qty_spin = QSpinBox()
        self._qty_spin.setRange(1, 100000)
        self._qty_spin.setValue(100)
        order_layout.addRow("Quantity:", self._qty_spin)
        
        self._limit_price = QDoubleSpinBox()
        self._limit_price.setRange(0.01, 99999.99)
        self._limit_price.setDecimals(2)
        self._limit_price.setSingleStep(0.01)
        order_layout.addRow("Limit Price:", self._limit_price)
        
        self._stop_price = QDoubleSpinBox()
        self._stop_price.setRange(0.01, 99999.99)
        self._stop_price.setDecimals(2)
        self._stop_price.setSingleStep(0.01)
        order_layout.addRow("Stop Price:", self._stop_price)
        
        layout.addWidget(order_group)
        
        # Time in force
        tif_group = QGroupBox("Time in Force")
        tif_layout = QFormLayout(tif_group)
        
        self._tif_combo = QComboBox()
        self._tif_combo.addItems(["DAY", "GTC", "IOC", "FOK"])
        tif_layout.addRow("TIF:", self._tif_combo)
        
        layout.addWidget(tif_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self._cancel_btn)
        
        button_layout.addStretch()
        
        self._submit_btn = QPushButton("Submit Order")
        self._submit_btn.setDefault(True)
        self._submit_btn.clicked.connect(self._submit_order)
        button_layout.addWidget(self._submit_btn)
        
        layout.addLayout(button_layout)
        
        # Initial state
        self._on_order_type_changed("MKT")
        
    def _apply_style(self):
        self.setStyleSheet("""
            QDialog {
                background: #1e1e2e;
            }
            QGroupBox {
                color: #ddd;
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                color: #aaa;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                background: rgba(255, 255, 255, 10);
                color: white;
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 4px;
                padding: 6px 10px;
                min-width: 150px;
            }
            QPushButton {
                background: rgba(255, 255, 255, 10);
                color: white;
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 4px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 20);
            }
            QPushButton#submitBtn {
                background: rgba(38, 166, 154, 100);
                border-color: #26a69a;
                color: #26a69a;
            }
            QPushButton#submitBtn:hover {
                background: rgba(38, 166, 154, 150);
            }
        """)
        self._submit_btn.setObjectName("submitBtn")
        
    def _on_order_type_changed(self, order_type: str):
        """Enable/disable price fields based on order type."""
        self._limit_price.setEnabled(order_type in ["LMT", "STP LMT"])
        self._stop_price.setEnabled(order_type in ["STP", "STP LMT"])
        
    def _submit_order(self):
        """Submit the order."""
        order = {
            "symbol": self._symbol_edit.text().upper(),
            "exchange": self._exchange_combo.currentText(),
            "side": self._side_combo.currentText(),
            "type": self._type_combo.currentText(),
            "quantity": self._qty_spin.value(),
            "limit_price": self._limit_price.value() if self._limit_price.isEnabled() else None,
            "stop_price": self._stop_price.value() if self._stop_price.isEnabled() else None,
            "tif": self._tif_combo.currentText(),
        }
        
        if not order["symbol"]:
            return
            
        print(f"[Order] Submitting: {order}")
        self.order_submitted.emit(order)
        self.accept()
        
    def set_symbol(self, symbol: str):
        """Pre-fill the symbol field."""
        self._symbol_edit.setText(symbol)

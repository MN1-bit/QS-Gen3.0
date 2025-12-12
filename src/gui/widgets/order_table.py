"""
Order Table Widget.

Displays order history and active orders.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QHBoxLayout, QPushButton
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QColor
from typing import List, Dict
from datetime import datetime


class OrderTable(QWidget):
    """
    Table showing orders with status.
    
    Displays order ID, symbol, side, quantity, price, status, and time.
    """
    
    # Signals
    cancel_requested = Signal(str)  # Order ID
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("orderTable")
        self._setup_ui()
        self._setup_demo_data()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("Orders")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ddd;")
        header.addWidget(title)
        header.addStretch()
        
        self._cancel_all_btn = QPushButton("Cancel All")
        self._cancel_all_btn.setStyleSheet("""
            QPushButton {
                background: rgba(239, 83, 80, 100);
                color: #ef5350;
                border: 1px solid #ef5350;
                border-radius: 4px;
                padding: 5px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(239, 83, 80, 150);
            }
        """)
        header.addWidget(self._cancel_all_btn)
        layout.addLayout(header)
        
        # Table
        self._table = QTableWidget()
        self._table.setColumnCount(7)
        self._table.setHorizontalHeaderLabels([
            "Order ID", "Symbol", "Side", "Qty", "Price", "Status", "Time"
        ])
        
        # Style
        self._table.setStyleSheet("""
            QTableWidget {
                background: rgba(30, 30, 46, 200);
                color: #ddd;
                border: 1px solid rgba(255, 255, 255, 20);
                border-radius: 4px;
                gridline-color: rgba(255, 255, 255, 30);
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background: rgba(255, 255, 255, 10);
                color: #aaa;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.verticalHeader().setVisible(False)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self._table)
        
    def _setup_demo_data(self):
        """Add demo order data."""
        orders = [
            {"id": "1001", "symbol": "SPY", "side": "BUY", "qty": 10, 
             "price": 450.00, "status": "FILLED", "time": "09:35:22"},
            {"id": "1002", "symbol": "QQQ", "side": "SELL", "qty": 5,
             "price": 380.50, "status": "PENDING", "time": "10:15:45"},
            {"id": "1003", "symbol": "AAPL", "side": "BUY", "qty": 25,
             "price": 175.00, "status": "CANCELLED", "time": "11:22:10"},
        ]
        self.update_orders(orders)
        
    @Slot(list)
    def update_orders(self, orders: List[Dict]):
        """
        Update order table.
        
        Args:
            orders: List of order dicts
        """
        self._table.setRowCount(len(orders))
        
        for row, order in enumerate(orders):
            self._table.setItem(row, 0, QTableWidgetItem(order["id"]))
            self._table.setItem(row, 1, QTableWidgetItem(order["symbol"]))
            
            # Side with color
            side_item = QTableWidgetItem(order["side"])
            if order["side"] == "BUY":
                side_item.setForeground(QColor("#26a69a"))
            else:
                side_item.setForeground(QColor("#ef5350"))
            self._table.setItem(row, 2, side_item)
            
            self._table.setItem(row, 3, QTableWidgetItem(str(order["qty"])))
            self._table.setItem(row, 4, QTableWidgetItem(f"${order['price']:.2f}"))
            
            # Status with color
            status_item = QTableWidgetItem(order["status"])
            if order["status"] == "FILLED":
                status_item.setForeground(QColor("#26a69a"))
            elif order["status"] == "PENDING":
                status_item.setForeground(QColor("#ffb74d"))
            else:
                status_item.setForeground(QColor("#888"))
            self._table.setItem(row, 5, status_item)
            
            self._table.setItem(row, 6, QTableWidgetItem(order["time"]))

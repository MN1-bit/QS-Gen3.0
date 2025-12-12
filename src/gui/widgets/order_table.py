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
    
    Displays order ID, symbol, side, quantity, type, status.
    """
    
    # Signals
    cancel_requested = Signal(str)  # Order ID
    cancel_all_requested = Signal()  # Cancel all orders
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("orderTable")
        self._orders = {}  # orderId -> order data
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header = QHBoxLayout()
        self._title = QLabel("Orders (0)")
        self._title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ddd;")
        header.addWidget(self._title)
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
        self._cancel_all_btn.clicked.connect(self.cancel_all_requested.emit)
        header.addWidget(self._cancel_all_btn)
        layout.addLayout(header)
        
        # Table
        self._table = QTableWidget()
        self._table.setColumnCount(6)
        self._table.setHorizontalHeaderLabels([
            "Order ID", "Symbol", "Side", "Qty", "Type", "Status"
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
        
    @Slot(dict)
    def add_order(self, order: Dict):
        """
        Add or update an order.
        
        Args:
            order: Order dict with orderId, symbol, action, quantity, orderType, status
        """
        order_id = order["orderId"]
        self._orders[order_id] = order
        self._refresh_table()
        
    @Slot(dict)
    def update_order_status(self, status: Dict):
        """
        Update order status.
        
        Args:
            status: Status dict with orderId, status, filled, remaining
        """
        order_id = status["orderId"]
        if order_id in self._orders:
            self._orders[order_id]["status"] = status["status"]
            self._orders[order_id]["filled"] = status.get("filled", 0)
            self._refresh_table()
            
    @Slot()
    def clear_orders(self):
        """Clear all orders."""
        self._orders.clear()
        self._refresh_table()
        
    def _refresh_table(self):
        """Refresh the table from orders data."""
        orders = list(self._orders.values())
        
        self._title.setText(f"Orders ({len(orders)})")
        self._table.setRowCount(len(orders))
        
        for row, order in enumerate(orders):
            self._table.setItem(row, 0, QTableWidgetItem(str(order["orderId"])))
            self._table.setItem(row, 1, QTableWidgetItem(order["symbol"]))
            
            # Side with color
            side = order["action"]
            side_item = QTableWidgetItem(side)
            if side == "BUY":
                side_item.setForeground(QColor("#26a69a"))
            else:
                side_item.setForeground(QColor("#ef5350"))
            self._table.setItem(row, 2, side_item)
            
            self._table.setItem(row, 3, QTableWidgetItem(str(int(order["quantity"]))))
            self._table.setItem(row, 4, QTableWidgetItem(order["orderType"]))
            
            # Status with color
            status = order["status"]
            status_item = QTableWidgetItem(status)
            if status == "Filled":
                status_item.setForeground(QColor("#26a69a"))
            elif status == "Cancelled":
                status_item.setForeground(QColor("#ef5350"))
            elif status in ["Submitted", "PreSubmitted"]:
                status_item.setForeground(QColor("#ffb74d"))
            self._table.setItem(row, 5, status_item)

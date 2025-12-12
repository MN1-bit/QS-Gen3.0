"""
Position Panel Widget.

Displays current portfolio positions with P&L.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QColor
from typing import List, Dict


class PositionPanel(QWidget):
    """
    Panel showing current portfolio positions.
    
    Displays symbol, quantity, average price, current price, and P&L.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("positionPanel")
        self._setup_ui()
        self._setup_demo_data()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Positions")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ddd;")
        layout.addWidget(title)
        
        # Table
        self._table = QTableWidget()
        self._table.setColumnCount(6)
        self._table.setHorizontalHeaderLabels([
            "Symbol", "Qty", "Avg Price", "Current", "P&L", "P&L %"
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
        """Add demo position data."""
        positions = [
            {"symbol": "SPY", "qty": 100, "avg": 450.50, "current": 455.25},
            {"symbol": "QQQ", "qty": 50, "avg": 380.00, "current": 375.50},
            {"symbol": "AAPL", "qty": 25, "avg": 175.00, "current": 180.00},
        ]
        self.update_positions(positions)
        
    @Slot(list)
    def update_positions(self, positions: List[Dict]):
        """
        Update position table.
        
        Args:
            positions: List of position dicts with symbol, qty, avg, current
        """
        self._table.setRowCount(len(positions))
        
        for row, pos in enumerate(positions):
            symbol = pos["symbol"]
            qty = pos["qty"]
            avg = pos["avg"]
            current = pos["current"]
            pnl = (current - avg) * qty
            pnl_pct = ((current - avg) / avg) * 100
            
            self._table.setItem(row, 0, QTableWidgetItem(symbol))
            self._table.setItem(row, 1, QTableWidgetItem(str(qty)))
            self._table.setItem(row, 2, QTableWidgetItem(f"${avg:.2f}"))
            self._table.setItem(row, 3, QTableWidgetItem(f"${current:.2f}"))
            
            # P&L with color
            pnl_item = QTableWidgetItem(f"${pnl:+,.2f}")
            pnl_pct_item = QTableWidgetItem(f"{pnl_pct:+.2f}%")
            
            if pnl >= 0:
                pnl_item.setForeground(QColor("#26a69a"))
                pnl_pct_item.setForeground(QColor("#26a69a"))
            else:
                pnl_item.setForeground(QColor("#ef5350"))
                pnl_pct_item.setForeground(QColor("#ef5350"))
                
            self._table.setItem(row, 4, pnl_item)
            self._table.setItem(row, 5, pnl_pct_item)

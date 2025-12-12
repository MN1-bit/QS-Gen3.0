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
        self._positions = {}  # symbol -> position data
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title with count
        self._title = QLabel("Positions (0)")
        self._title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ddd;")
        layout.addWidget(self._title)
        
        # Table
        self._table = QTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels([
            "Symbol", "Qty", "Avg Cost", "Value"
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
    def add_position(self, position: Dict):
        """
        Add or update a position.
        
        Args:
            position: Position dict with symbol, position, avgCost
        """
        symbol = position["symbol"]
        self._positions[symbol] = position
        self._refresh_table()
        
    @Slot()
    def clear_positions(self):
        """Clear all positions."""
        self._positions.clear()
        self._refresh_table()
        
    def _refresh_table(self):
        """Refresh the table from positions data."""
        positions = [p for p in self._positions.values() if p["position"] != 0]
        
        self._title.setText(f"Positions ({len(positions)})")
        self._table.setRowCount(len(positions))
        
        for row, pos in enumerate(positions):
            symbol = pos["symbol"]
            qty = pos["position"]
            avg_cost = pos["avgCost"]
            value = abs(qty * avg_cost)
            
            self._table.setItem(row, 0, QTableWidgetItem(symbol))
            
            qty_item = QTableWidgetItem(str(int(qty)))
            if qty > 0:
                qty_item.setForeground(QColor("#26a69a"))
            else:
                qty_item.setForeground(QColor("#ef5350"))
            self._table.setItem(row, 1, qty_item)
            
            self._table.setItem(row, 2, QTableWidgetItem(f"${avg_cost:.2f}"))
            self._table.setItem(row, 3, QTableWidgetItem(f"${value:,.2f}"))

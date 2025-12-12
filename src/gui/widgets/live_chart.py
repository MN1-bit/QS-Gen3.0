"""
Live Chart Widget using PyQtGraph.

Real-time price chart with candlestick visualization.
"""
import pyqtgraph as pg
from pyqtgraph import DateAxisItem
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QColor
import numpy as np
from datetime import datetime
from typing import List, Optional


class CandlestickItem(pg.GraphicsObject):
    """Custom candlestick chart item for PyQtGraph."""
    
    def __init__(self, data=None):
        pg.GraphicsObject.__init__(self)
        self.data = data or []  # List of (time, open, high, low, close)
        self.generatePicture()
        
    def generatePicture(self):
        """Generate the candlestick picture."""
        self.picture = pg.QtGui.QPicture()
        p = pg.QtGui.QPainter(self.picture)
        
        if not self.data:
            p.end()
            return
            
        width = 0.35
        
        for candle in self.data:
            t, o, h, l, c = candle
            
            if c >= o:  # Bullish (green)
                p.setPen(pg.mkPen('#26a69a', width=1))
                p.setBrush(pg.mkBrush('#26a69a'))
            else:  # Bearish (red)
                p.setPen(pg.mkPen('#ef5350', width=1))
                p.setBrush(pg.mkBrush('#ef5350'))
            
            # Draw wick
            p.drawLine(pg.QtCore.QPointF(t, l), pg.QtCore.QPointF(t, h))
            
            # Draw body
            p.drawRect(pg.QtCore.QRectF(t - width, o, width * 2, c - o))
            
        p.end()
        
    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)
        
    def boundingRect(self):
        return pg.QtCore.QRectF(self.picture.boundingRect())
        
    def setData(self, data):
        """Update chart data."""
        self.data = data
        self.generatePicture()
        self.informViewBoundsChanged()


class LiveChartWidget(QWidget):
    """
    Live price chart widget with candlestick visualization.
    
    Displays real-time price data from IBKR.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("liveChartWidget")
        self._setup_ui()
        self._setup_demo_data()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header with symbol selector
        header = QHBoxLayout()
        
        symbol_label = QLabel("Symbol:")
        symbol_label.setStyleSheet("color: #aaa; font-size: 13px;")
        header.addWidget(symbol_label)
        
        self._symbol_combo = QComboBox()
        self._symbol_combo.addItems(["SPY", "QQQ", "AAPL", "MSFT", "NVDA"])
        self._symbol_combo.setStyleSheet("""
            QComboBox {
                background: rgba(255, 255, 255, 20);
                color: white;
                border: 1px solid rgba(255, 255, 255, 40);
                border-radius: 4px;
                padding: 5px 10px;
                min-width: 100px;
            }
        """)
        self._symbol_combo.currentTextChanged.connect(self._on_symbol_changed)
        header.addWidget(self._symbol_combo)
        
        self._price_label = QLabel("$0.00")
        self._price_label.setStyleSheet("color: #26a69a; font-size: 18px; font-weight: bold;")
        header.addWidget(self._price_label)
        
        header.addStretch()
        layout.addLayout(header)
        
        # Chart area
        pg.setConfigOptions(antialias=True)
        self._chart = pg.PlotWidget()
        self._chart.setBackground('#1e1e2e')
        self._chart.showGrid(x=True, y=True, alpha=0.3)
        self._chart.setLabel('left', 'Price', color='#888')
        self._chart.setLabel('bottom', 'Time', color='#888')
        
        # Add candlestick item
        self._candles = CandlestickItem()
        self._chart.addItem(self._candles)
        
        layout.addWidget(self._chart)
        
    def _setup_demo_data(self):
        """Generate demo candlestick data."""
        np.random.seed(42)
        n = 50
        data = []
        price = 450.0
        
        for i in range(n):
            o = price + np.random.uniform(-2, 2)
            c = o + np.random.uniform(-3, 3)
            h = max(o, c) + np.random.uniform(0, 2)
            l = min(o, c) - np.random.uniform(0, 2)
            price = c
            data.append((i, o, h, l, c))
            
        self._candles.setData(data)
        self._price_label.setText(f"${price:.2f}")
        
    @Slot(str)
    def _on_symbol_changed(self, symbol: str):
        """Handle symbol change."""
        # Regenerate demo data for new symbol
        self._setup_demo_data()
        
    @Slot(list)
    def update_data(self, candles: List[tuple]):
        """
        Update chart with new candle data.
        
        Args:
            candles: List of (time, open, high, low, close) tuples
        """
        self._candles.setData(candles)
        if candles:
            last_price = candles[-1][4]  # Close price
            self._price_label.setText(f"${last_price:.2f}")

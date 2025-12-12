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
    
    # Signals
    symbol_changed = Signal(str)  # Emitted when symbol changes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("liveChartWidget")
        self._current_symbol = "SPY"
        self._last_price = 0.0
        self._prices = []  # Store recent prices for line chart
        self._bars = []    # Store historical bars for candlestick
        self._setup_ui()
        
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
        
        self._price_label = QLabel("--")
        self._price_label.setStyleSheet("color: #888; font-size: 18px; font-weight: bold;")
        header.addWidget(self._price_label)
        
        # Live indicator
        self._live_indicator = QLabel("● LIVE")
        self._live_indicator.setStyleSheet("color: #26a69a; font-size: 11px;")
        self._live_indicator.setVisible(False)
        header.addWidget(self._live_indicator)
        
        # Status label
        self._status_label = QLabel("Waiting for connection...")
        self._status_label.setStyleSheet("color: #666; font-size: 11px;")
        header.addWidget(self._status_label)
        
        header.addStretch()
        layout.addLayout(header)
        
        # Chart area
        pg.setConfigOptions(antialias=True)
        self._chart = pg.PlotWidget()
        self._chart.setBackground('#1e1e2e')
        self._chart.showGrid(x=True, y=True, alpha=0.3)
        self._chart.setLabel('left', 'Price', color='#888')
        self._chart.setLabel('bottom', 'Time', color='#888')
        
        # Add candlestick item (for historical data)
        self._candles = CandlestickItem()
        self._chart.addItem(self._candles)
        
        # Add real-time price line
        self._price_line = self._chart.plot(
            pen=pg.mkPen('#26a69a', width=2),
            name='Price'
        )
        
        layout.addWidget(self._chart)
        
    @Slot(str)
    def _on_symbol_changed(self, symbol: str):
        """Handle symbol change."""
        self._current_symbol = symbol
        self._prices = []
        self._bars = []
        self._candles.setData([])
        self._price_line.setData([], [])
        self._live_indicator.setVisible(False)
        self._price_label.setText("--")
        self._status_label.setText("Loading...")
        self.symbol_changed.emit(symbol)
        
    @Slot(float)
    def update_price(self, price: float):
        """Update chart with new price."""
        self._last_price = price
        self._live_indicator.setVisible(True)
        self._status_label.setText("")
        
        # Update price label with color based on change
        if self._prices and price > self._prices[-1]:
            self._price_label.setStyleSheet("color: #26a69a; font-size: 18px; font-weight: bold;")
        elif self._prices and price < self._prices[-1]:
            self._price_label.setStyleSheet("color: #ef5350; font-size: 18px; font-weight: bold;")
            
        self._price_label.setText(f"${price:.2f}")
        self._prices.append(price)
        
        # Keep only last 100 prices
        if len(self._prices) > 100:
            self._prices = self._prices[-100:]
            
        # Update the price line chart
        if len(self._prices) > 1:
            x_data = list(range(len(self._prices)))
            self._price_line.setData(x_data, self._prices)
            
    @Slot(object)
    def add_bar(self, bar):
        """
        Add a historical bar to the chart.
        
        Args:
            bar: ibapi BarData object
        """
        # Convert bar to tuple format (index, open, high, low, close)
        bar_index = len(self._bars)
        self._bars.append((bar_index, bar.open, bar.high, bar.low, bar.close))
        
        # Update candlesticks
        self._candles.setData(self._bars)
        
        # Update price label if this is the latest bar
        if bar.close > 0:
            self._price_label.setText(f"${bar.close:.2f}")
            self._status_label.setText(f"{len(self._bars)} bars loaded")
        
    @Slot(list)
    def update_data(self, candles: List[tuple]):
        """Update chart with new candle data."""
        self._candles.setData(candles)
        if candles:
            last_price = candles[-1][4]  # Close price
            self._price_label.setText(f"${last_price:.2f}")
            
    @Slot()
    def clear_data(self):
        """Clear all chart data."""
        self._bars = []
        self._prices = []
        self._candles.setData([])
        self._price_line.setData([], [])
        self._price_label.setText("--")
        self._status_label.setText("Waiting for connection...")
            
    @property
    def current_symbol(self) -> str:
        """Get current symbol."""
        return self._current_symbol

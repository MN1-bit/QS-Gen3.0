"""
Tearsheet Viewer Widget.

Displays backtest performance metrics and statistics.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QGroupBox, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Slot
from typing import Dict, Any


class MetricCard(QFrame):
    """A card displaying a single metric."""
    
    def __init__(self, title: str, value: str, color: str = "#26a69a", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: rgba(255, 255, 255, 5);
                border: 1px solid rgba(255, 255, 255, 20);
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: bold;")
        layout.addWidget(value_label)
        
        self._value_label = value_label
        
    def set_value(self, value: str, color: str = None):
        """Update the value."""
        self._value_label.setText(value)
        if color:
            self._value_label.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: bold;")


class TearsheetViewer(QWidget):
    """
    Widget for viewing backtest performance tearsheet.
    
    Displays key metrics like returns, Sharpe ratio, drawdown, etc.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("tearsheetViewer")
        self._setup_ui()
        self._show_demo_data()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Performance Tearsheet")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ddd;")
        layout.addWidget(title)
        
        # Scroll area for metrics
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(15)
        
        # Returns section
        returns_group = QGroupBox("Returns")
        returns_group.setStyleSheet("""
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
        
        returns_layout = QGridLayout(returns_group)
        returns_layout.setSpacing(10)
        
        self._total_return = MetricCard("Total Return", "+45.2%", "#26a69a")
        returns_layout.addWidget(self._total_return, 0, 0)
        
        self._annual_return = MetricCard("Annual Return", "+22.6%", "#26a69a")
        returns_layout.addWidget(self._annual_return, 0, 1)
        
        self._daily_return = MetricCard("Avg Daily Return", "+0.09%", "#26a69a")
        returns_layout.addWidget(self._daily_return, 0, 2)
        
        content_layout.addWidget(returns_group)
        
        # Risk section
        risk_group = QGroupBox("Risk Metrics")
        risk_group.setStyleSheet(returns_group.styleSheet())
        
        risk_layout = QGridLayout(risk_group)
        risk_layout.setSpacing(10)
        
        self._sharpe = MetricCard("Sharpe Ratio", "1.85", "#26a69a")
        risk_layout.addWidget(self._sharpe, 0, 0)
        
        self._sortino = MetricCard("Sortino Ratio", "2.42", "#26a69a")
        risk_layout.addWidget(self._sortino, 0, 1)
        
        self._max_dd = MetricCard("Max Drawdown", "-12.3%", "#ef5350")
        risk_layout.addWidget(self._max_dd, 0, 2)
        
        self._volatility = MetricCard("Volatility", "18.5%", "#ffb74d")
        risk_layout.addWidget(self._volatility, 1, 0)
        
        self._calmar = MetricCard("Calmar Ratio", "1.84", "#26a69a")
        risk_layout.addWidget(self._calmar, 1, 1)
        
        self._var = MetricCard("VaR (95%)", "-2.1%", "#ffb74d")
        risk_layout.addWidget(self._var, 1, 2)
        
        content_layout.addWidget(risk_group)
        
        # Trade statistics
        trade_group = QGroupBox("Trade Statistics")
        trade_group.setStyleSheet(returns_group.styleSheet())
        
        trade_layout = QGridLayout(trade_group)
        trade_layout.setSpacing(10)
        
        self._total_trades = MetricCard("Total Trades", "142", "#ddd")
        trade_layout.addWidget(self._total_trades, 0, 0)
        
        self._win_rate = MetricCard("Win Rate", "58.4%", "#26a69a")
        trade_layout.addWidget(self._win_rate, 0, 1)
        
        self._profit_factor = MetricCard("Profit Factor", "1.72", "#26a69a")
        trade_layout.addWidget(self._profit_factor, 0, 2)
        
        self._avg_win = MetricCard("Avg Win", "+$425", "#26a69a")
        trade_layout.addWidget(self._avg_win, 1, 0)
        
        self._avg_loss = MetricCard("Avg Loss", "-$312", "#ef5350")
        trade_layout.addWidget(self._avg_loss, 1, 1)
        
        self._expectancy = MetricCard("Expectancy", "+$85", "#26a69a")
        trade_layout.addWidget(self._expectancy, 1, 2)
        
        content_layout.addWidget(trade_group)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
    def _show_demo_data(self):
        """Show demo performance data."""
        pass  # Demo data is already set in the cards
        
    @Slot(dict)
    def update_metrics(self, metrics: Dict[str, Any]):
        """
        Update all metrics from backtest results.
        
        Args:
            metrics: Dict with metric values
        """
        if "total_return" in metrics:
            val = metrics["total_return"]
            color = "#26a69a" if val >= 0 else "#ef5350"
            self._total_return.set_value(f"{val:+.1f}%", color)
            
        # Add more metric updates as needed

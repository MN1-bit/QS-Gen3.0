import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QColor
from qfluentwidgets import (
    FluentWindow, NavigationItemPosition, FluentIcon,
    SubtitleLabel, setFont, Theme, setTheme
)

from src.gui.widgets.connection_widget import ConnectionWidget
from src.gui.widgets.live_chart import LiveChartWidget
from src.gui.widgets.position_panel import PositionPanel
from src.gui.widgets.order_table import OrderTable
from src.gui.widgets.strategy_control import StrategyControl
from src.gui.widgets.log_viewer import LogViewer
from src.gui.widgets.backtest_runner import BacktestRunner
from src.gui.widgets.tearsheet_viewer import TearsheetViewer
from src.core.ibkr_bridge import IBKRBridge


class DashboardInterface(QWidget):
    """Dashboard page with connection status and overview."""
    
    def __init__(self, bridge: IBKRBridge, parent=None):
        super().__init__(parent)
        self.setObjectName("dashboardInterface")
        self._bridge = bridge
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        from PySide6.QtWidgets import QHBoxLayout, QPushButton, QSplitter, QFrame
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Header with connection and buttons
        header = QHBoxLayout()
        header.setSpacing(10)
        
        # Connection status widget
        self._connection_widget = ConnectionWidget()
        header.addWidget(self._connection_widget)
        
        header.addStretch()
        
        # New Order button
        self._new_order_btn = QPushButton("+ New Order")
        self._new_order_btn.setStyleSheet("""
            QPushButton {
                background: rgba(38, 166, 154, 100);
                color: #26a69a;
                border: 1px solid #26a69a;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(38, 166, 154, 150);
            }
        """)
        self._new_order_btn.clicked.connect(self._show_order_dialog)
        header.addWidget(self._new_order_btn)
        
        layout.addLayout(header)
        
        # Main content area with splitters
        # Layout:
        # ┌─────────────────────────────────────────┐
        # │              Live Chart                 │
        # ├─────────────┬─────────────┬─────────────┤
        # │  Positions  │   Orders    │  Strategy   │
        # └─────────────┴─────────────┴─────────────┘
        
        main_splitter = QSplitter(Qt.Vertical)
        main_splitter.setHandleWidth(3)
        main_splitter.setStyleSheet("""
            QSplitter::handle {
                background: rgba(255, 255, 255, 20);
            }
            QSplitter::handle:hover {
                background: rgba(255, 255, 255, 40);
            }
        """)
        
        # Top: Live Chart
        self._chart_widget = LiveChartWidget()
        main_splitter.addWidget(self._chart_widget)
        
        # Bottom: Horizontal splitter for Positions, Orders, and Strategy
        bottom_splitter = QSplitter(Qt.Horizontal)
        bottom_splitter.setHandleWidth(3)
        bottom_splitter.setStyleSheet("""
            QSplitter::handle {
                background: rgba(255, 255, 255, 20);
            }
            QSplitter::handle:hover {
                background: rgba(255, 255, 255, 40);
            }
        """)
        
        # Left: Positions
        self._position_panel = PositionPanel()
        bottom_splitter.addWidget(self._position_panel)
        
        # Center: Orders
        self._order_table = OrderTable()
        bottom_splitter.addWidget(self._order_table)
        
        # Right: Strategy Control
        self._strategy_control = StrategyControl()
        bottom_splitter.addWidget(self._strategy_control)
        
        # Set initial sizes for bottom splitter (33/33/33)
        bottom_splitter.setSizes([350, 350, 300])
        
        main_splitter.addWidget(bottom_splitter)
        
        # Set initial sizes for main splitter (55% chart, 45% bottom)
        main_splitter.setSizes([550, 450])
        
        layout.addWidget(main_splitter)
        
    def _show_order_dialog(self):
        """Show the order entry dialog."""
        from src.gui.dialogs.order_entry import OrderEntryDialog
        
        dialog = OrderEntryDialog(self)
        dialog.order_submitted.connect(self._bridge.place_order)
        dialog.exec()
        
    def _connect_signals(self):
        """Connect IBKRBridge signals to UI."""
        self._bridge.connection_status_changed.connect(
            self._connection_widget.set_status
        )
        self._bridge.connected.connect(
            self._connection_widget.set_connected
        )
        self._bridge.disconnected.connect(
            self._connection_widget.set_disconnected
        )
        # Connect reconnect button to bridge
        self._connection_widget.reconnect_requested.connect(
            self._bridge.reconnect
        )


class TradingMainWindow(FluentWindow):
    """
    Main trading window with Fluent Design.
    
    Note: Windows 11 Mica effect is disabled due to Windows 24H2 bug.
    See: docs/devlog/003-glassmorphism-research-results.md
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize IBKR Bridge
        self._bridge = IBKRBridge(self)
        
        self.initWindow()
        self.initNavigation()
        
    def initWindow(self):
        self.resize(1300, 800)
        self.setMinimumWidth(800)
        self.setWindowTitle("QS-Gen3.0 - Retail Quant System")
        
        # Center on screen
        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(int(w/2 - 1300/2), int(h/2 - 800/2))
        
    def initNavigation(self):
        # Dashboard (Home) - with real dashboard interface
        self.dashboardInterface = DashboardInterface(self._bridge, self)
        self.addSubInterface(
            self.dashboardInterface,
            FluentIcon.HOME,
            "Dashboard",
            NavigationItemPosition.TOP
        )
        
        # Live Chart
        self.chartInterface = LiveChartWidget(self)
        self.chartInterface.setObjectName("chartInterface")
        self.addSubInterface(
            self.chartInterface,
            FluentIcon.MARKET,
            "Live Chart",
            NavigationItemPosition.TOP
        )
        
        # Positions
        self.positionsInterface = PositionPanel(self)
        self.positionsInterface.setObjectName("positionsInterface")
        self.addSubInterface(
            self.positionsInterface,
            FluentIcon.BOOK_SHELF,
            "Positions",
            NavigationItemPosition.TOP
        )
        
        # Orders
        self.ordersInterface = OrderTable(self)
        self.ordersInterface.setObjectName("ordersInterface")
        self.addSubInterface(
            self.ordersInterface,
            FluentIcon.SEND,
            "Orders",
            NavigationItemPosition.TOP
        )
        
        # Strategy
        self.strategyInterface = StrategyControl(self)
        self.strategyInterface.setObjectName("strategyInterface")
        self.addSubInterface(
            self.strategyInterface,
            FluentIcon.PLAY,
            "Strategy",
            NavigationItemPosition.TOP
        )
        
        # Backtest
        self.backtestInterface = BacktestRunner(self)
        self.backtestInterface.setObjectName("backtestInterface")
        self.addSubInterface(
            self.backtestInterface,
            FluentIcon.HISTORY,
            "Backtest",
            NavigationItemPosition.TOP
        )
        
        # Tearsheet
        self.tearsheetInterface = TearsheetViewer(self)
        self.tearsheetInterface.setObjectName("tearsheetInterface")
        self.addSubInterface(
            self.tearsheetInterface,
            FluentIcon.DOCUMENT,
            "Tearsheet",
            NavigationItemPosition.TOP
        )
        
        # Logs
        self.logsInterface = LogViewer(self)
        self.logsInterface.setObjectName("logsInterface")
        self.addSubInterface(
            self.logsInterface,
            FluentIcon.COMMAND_PROMPT,
            "Logs",
            NavigationItemPosition.BOTTOM
        )
    
    @property
    def bridge(self) -> IBKRBridge:
        """Get the IBKR bridge instance."""
        return self._bridge

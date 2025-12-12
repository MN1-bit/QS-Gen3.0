import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, 
    QSystemTrayIcon, QMenu
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QColor, QAction
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
        
        # Connect price signal to chart
        self._bridge.price_received.connect(self._on_price_received)
        
        # Auto-subscribe to market data when connected
        self._bridge.connected.connect(self._subscribe_default_symbol)
        
        # Handle chart symbol change
        self._chart_widget.symbol_changed.connect(self._on_chart_symbol_changed)
        
        # Connect historical data signal
        self._bridge.historical_bar_received.connect(self._on_historical_bar)
        
        # Connect position signals
        self._bridge.position_received.connect(self._position_panel.add_position)
        self._bridge.positions_complete.connect(self._on_positions_complete)
        
        # Connect order signals
        self._bridge.order_received.connect(self._order_table.add_order)
        self._bridge.order_status_received.connect(self._order_table.update_order_status)
        
        # Auto-request positions and orders on connect
        self._bridge.connected.connect(self._request_tws_data)
        
        # Connect cancel all button
        self._order_table.cancel_all_requested.connect(self._bridge.cancel_all_orders)
        
    def _on_price_received(self, req_id: int, price: float):
        """Handle price update from bridge."""
        self._chart_widget.update_price(price)
        
    def _subscribe_default_symbol(self):
        """Subscribe to default symbol on connect."""
        symbol = self._chart_widget.current_symbol
        self._current_req_id = 1001
        self._bridge.subscribe_market_data(symbol, self._current_req_id)
        # Also request historical data
        self._request_chart_history(symbol)
        
    def _on_chart_symbol_changed(self, symbol: str):
        """Handle symbol change from chart."""
        if hasattr(self, '_current_req_id'):
            self._bridge.unsubscribe_market_data(self._current_req_id)
        self._current_req_id = 1001
        self._bridge.subscribe_market_data(symbol, self._current_req_id)
        # Also request historical data for new symbol
        self._request_chart_history(symbol)
        
    def _request_chart_history(self, symbol: str):
        """Request historical data for chart."""
        self._chart_widget.clear_data()
        self._bridge.request_historical_data(symbol, req_id=2001)
        
    def _on_historical_bar(self, req_id: int, bar):
        """Handle historical bar data."""
        if req_id == 2001:  # Chart history request
            self._chart_widget.add_bar(bar)
        
    def _request_tws_data(self):
        """Request positions and orders from TWS."""
        self._position_panel.clear_positions()
        self._order_table.clear_orders()
        self._bridge.request_positions()
        self._bridge.request_open_orders()
        
    def _on_positions_complete(self):
        """Called when all positions have been received."""
        print("[Dashboard] Positions sync complete")


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
        self.initSystemTray()
        
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
        
    def initSystemTray(self):
        """Initialize system tray icon and menu."""
        self._tray_icon = QSystemTrayIcon(self)
        # Use application style icon
        self._tray_icon.setIcon(FluentIcon.MARKET.icon())
        self._tray_icon.setToolTip("QS-Gen3.0 - Trading System")
        
        # Create tray menu
        tray_menu = QMenu()
        
        # Show action
        show_action = QAction("Show", self)
        show_action.triggered.connect(self._show_from_tray)
        tray_menu.addAction(show_action)
        
        # Connect action
        connect_action = QAction("Connect to TWS", self)
        connect_action.triggered.connect(self._bridge.connect_to_tws)
        tray_menu.addAction(connect_action)
        
        tray_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(exit_action)
        
        self._tray_icon.setContextMenu(tray_menu)
        self._tray_icon.activated.connect(self._on_tray_activated)
        self._tray_icon.show()
        
    def _show_from_tray(self):
        """Show window from tray."""
        self.showNormal()
        self.activateWindow()
        
    def _on_tray_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.DoubleClick:
            self._show_from_tray()
            
    def closeEvent(self, event):
        """Minimize to tray instead of closing."""
        if self._tray_icon.isVisible():
            self.hide()
            self._tray_icon.showMessage(
                "QS-Gen3.0",
                "Application minimized to tray. Double-click to restore.",
                QSystemTrayIcon.Information,
                2000
            )
            event.ignore()
        else:
            event.accept()

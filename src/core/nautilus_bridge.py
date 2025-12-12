"""
NautilusBridge: Nautilus Trader ↔ Qt Signal bridge.

This module converts Nautilus MessageBus events to Qt Signals
for GUI updates and manages the connection to IB Gateway.
"""
import asyncio
import threading
from typing import Optional, Any
from PySide6.QtCore import QObject, Signal, Slot, Qt


class NautilusBridge(QObject):
    """
    Bridge between Nautilus Trader events and Qt Signals.
    
    Manages connection to Dockerized IB Gateway and emits
    Qt Signals for GUI integration.
    """
    
    # Connection signals
    connected = Signal()
    disconnected = Signal()
    connection_status_changed = Signal(str)  # "connected", "disconnected", "connecting"
    
    # Data signals
    bar_received = Signal(object)  # Bar data
    quote_received = Signal(object)  # Quote data
    trade_received = Signal(object)  # Trade data
    price_received = Signal(str, float)  # symbol, price
    
    # Order signals
    order_submitted = Signal(object)  # OrderEvent
    order_filled = Signal(object)  # OrderFilled
    order_canceled = Signal(object)  # OrderCanceled
    order_rejected = Signal(object)  # OrderRejected
    order_received = Signal(dict)
    order_status_received = Signal(dict)
    
    # Position signals
    position_opened = Signal(object)  # Position
    position_changed = Signal(object)  # Position
    position_closed = Signal(object)  # Position
    position_received = Signal(dict)
    positions_complete = Signal()
    
    # Account signals
    account_updated = Signal(object)  # AccountState
    
    # Strategy signals
    strategy_started = Signal(str)  # strategy_id
    strategy_stopped = Signal(str)  # strategy_id
    
    # Error signal
    error_occurred = Signal(int, str)
    
    # Historical data signals
    historical_bar_received = Signal(int, object)
    
    # Internal signals for thread safety
    _internal_connected = Signal()
    _internal_disconnected = Signal()
    _internal_error = Signal(int, str)
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._trading_node = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._is_connected = False
        
        # Docker gateway settings
        self._gateway_host = "127.0.0.1"
        self._gateway_port = 4002
        
        # Connect internal signals for thread-safe emission
        self._internal_connected.connect(self._on_internal_connected, Qt.QueuedConnection)
        self._internal_disconnected.connect(self._on_internal_disconnected, Qt.QueuedConnection)
        self._internal_error.connect(self._on_internal_error, Qt.QueuedConnection)
        
    def _on_internal_connected(self):
        self._is_connected = True
        self.connected.emit()
        self.connection_status_changed.emit("connected")
        
    def _on_internal_disconnected(self):
        self._is_connected = False
        self.disconnected.emit()
        self.connection_status_changed.emit("disconnected")
        
    def _on_internal_error(self, code, msg):
        self.error_occurred.emit(code, msg)
        
    @property
    def is_connected(self) -> bool:
        return self._is_connected
        
    @Slot()
    def connect_to_tws(self):
        """Connect to the Dockerized IB Gateway via Nautilus."""
        if self._is_connected:
            print("[Nautilus] Already connected")
            return
            
        self.connection_status_changed.emit("connecting")
        print(f"[Nautilus] Connecting to IB Gateway at {self._gateway_host}:{self._gateway_port}...")
        
        # Start async event loop in background thread
        self._thread = threading.Thread(target=self._run_node, daemon=True)
        self._thread.start()
        
    def _run_node(self):
        """Run Nautilus TradingNode in background thread."""
        try:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._loop.run_until_complete(self._connect_async())
        except Exception as e:
            print(f"[Nautilus] Error: {e}")
            self._internal_error.emit(0, str(e))
            self._internal_disconnected.emit()
            
    async def _connect_async(self):
        """Async connection to Nautilus with IB adapter."""
        try:
            # Import Nautilus components
            from nautilus_trader.adapters.interactive_brokers.config import (
                InteractiveBrokersDataClientConfig,
                InteractiveBrokersExecClientConfig,
                InteractiveBrokersInstrumentProviderConfig,
            )
            from nautilus_trader.adapters.interactive_brokers.common import IB_VENUE
            from nautilus_trader.adapters.interactive_brokers.factories import (
                InteractiveBrokersLiveDataClientFactory,
                InteractiveBrokersLiveExecClientFactory,
            )
            from nautilus_trader.config import TradingNodeConfig, LoggingConfig
            from nautilus_trader.live.node import TradingNode
            
            # Instrument provider config
            provider_config = InteractiveBrokersInstrumentProviderConfig(
                load_ids=frozenset(["SPY.ARCA"]),
            )
            
            # Data client config
            data_config = InteractiveBrokersDataClientConfig(
                ibg_host=self._gateway_host,
                ibg_port=self._gateway_port,
                ibg_client_id=1,
                instrument_provider=provider_config,
            )
            
            # Execution client config
            exec_config = InteractiveBrokersExecClientConfig(
                ibg_host=self._gateway_host,
                ibg_port=self._gateway_port,
                ibg_client_id=2,
                instrument_provider=provider_config,
            )
            
            # Node config
            node_config = TradingNodeConfig(
                trader_id="QS-001",
                logging=LoggingConfig(log_level="INFO"),
                data_clients={IB_VENUE.value: data_config},
                exec_clients={IB_VENUE.value: exec_config},
            )
            
            # Build node
            self._trading_node = TradingNode(config=node_config)
            self._trading_node.add_data_client_factory(
                IB_VENUE, InteractiveBrokersLiveDataClientFactory
            )
            self._trading_node.add_exec_client_factory(
                IB_VENUE, InteractiveBrokersLiveExecClientFactory
            )
            self._trading_node.build()
            
            # Subscribe to events
            self._subscribe_to_events()
            
            print("[Nautilus] Node built successfully")
            self._internal_connected.emit()
            
            # Run the node
            await self._trading_node.run_async()
            
        except ImportError as e:
            print(f"[Nautilus] Import error: {e}")
            self._internal_error.emit(1, f"Import error: {e}")
            self._internal_disconnected.emit()
        except Exception as e:
            print(f"[Nautilus] Connection error: {e}")
            self._internal_error.emit(2, str(e))
            self._internal_disconnected.emit()
            
    def _subscribe_to_events(self):
        """Subscribe to Nautilus MessageBus events."""
        if not self._trading_node:
            return
            
        # Get the message bus
        msgbus = self._trading_node.trader.msgbus
        
        # Subscribe to various events
        # TODO: Add specific event subscriptions
        print("[Nautilus] Event subscriptions configured")
        
    @Slot()
    def disconnect_from_tws(self):
        """Disconnect from Nautilus/IB Gateway."""
        if self._trading_node:
            print("[Nautilus] Stopping node...")
            try:
                if self._loop and self._loop.is_running():
                    asyncio.run_coroutine_threadsafe(
                        self._trading_node.stop_async(), self._loop
                    )
            except Exception as e:
                print(f"[Nautilus] Stop error: {e}")
        
        self._is_connected = False
        self._internal_disconnected.emit()
        
    @Slot()
    def reconnect(self):
        """Reconnect to IB Gateway."""
        print("[Nautilus] Reconnecting...")
        self.disconnect_from_tws()
        self.connect_to_tws()
        
    # Compatibility methods with IBKRBridge interface
    def subscribe_market_data(self, symbol: str, req_id: int = 1001):
        """Subscribe to market data (compatibility)."""
        print(f"[Nautilus] Market data subscription for {symbol} - TODO")
        
    def unsubscribe_market_data(self, req_id: int):
        """Unsubscribe from market data (compatibility)."""
        print(f"[Nautilus] Unsubscribe reqId={req_id} - TODO")
        
    def request_historical_data(self, symbol: str, req_id: int = 2001):
        """Request historical data (compatibility)."""
        print(f"[Nautilus] Historical data for {symbol} - TODO")
        
    def request_positions(self):
        """Request positions (compatibility)."""
        print("[Nautilus] Requesting positions - TODO")
        
    def request_open_orders(self):
        """Request open orders (compatibility)."""
        print("[Nautilus] Requesting orders - TODO")
        
    def place_order(self, symbol, action, quantity, order_type, limit_price=None):
        """Place order (compatibility)."""
        print(f"[Nautilus] Place order {action} {quantity} {symbol} - TODO")
        
    def cancel_all_orders(self):
        """Cancel all orders (compatibility)."""
        print("[Nautilus] Cancel all orders - TODO")

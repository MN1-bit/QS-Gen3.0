"""
NautilusBridge: Nautilus Trader ↔ Qt Signal bridge.

This module converts Nautilus MessageBus events to Qt Signals
for GUI updates.
"""
from typing import Optional, Any
from PySide6.QtCore import QObject, Signal


class NautilusBridge(QObject):
    """Bridge between Nautilus Trader events and Qt Signals."""
    
    # Connection signals
    connected = Signal()
    disconnected = Signal()
    connection_status_changed = Signal(str)  # "connected", "disconnected", "reconnecting"
    
    # Data signals
    bar_received = Signal(object)  # Bar data
    quote_received = Signal(object)  # Quote data
    trade_received = Signal(object)  # Trade data
    
    # Order signals
    order_submitted = Signal(object)  # OrderEvent
    order_filled = Signal(object)  # OrderFilled
    order_canceled = Signal(object)  # OrderCanceled
    order_rejected = Signal(object)  # OrderRejected
    
    # Position signals
    position_opened = Signal(object)  # Position
    position_changed = Signal(object)  # Position
    position_closed = Signal(object)  # Position
    
    # Account signals
    account_updated = Signal(object)  # AccountState
    
    # Strategy signals
    strategy_started = Signal(str)  # strategy_id
    strategy_stopped = Signal(str)  # strategy_id
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._trading_node = None
        
    def set_trading_node(self, node):
        """Set the TradingNode instance to bridge."""
        self._trading_node = node
        self._subscribe_to_events()
        
    def _subscribe_to_events(self):
        """Subscribe to Nautilus MessageBus events."""
        if not self._trading_node:
            return
            
        # Get the message bus
        msgbus = self._trading_node.msgbus
        
        # Subscribe to various events
        # These handlers will emit Qt Signals
        pass  # TODO: Implement event subscriptions
        
    # Handler methods that emit signals
    def _on_connected(self):
        """Handle connection established."""
        self.connected.emit()
        self.connection_status_changed.emit("connected")
        
    def _on_disconnected(self):
        """Handle disconnection."""
        self.disconnected.emit()
        self.connection_status_changed.emit("disconnected")
        
    def _on_bar(self, bar):
        """Handle bar data received."""
        self.bar_received.emit(bar)
        
    def _on_order_event(self, event):
        """Handle order events."""
        from nautilus_trader.model.events import OrderFilled, OrderCanceled, OrderRejected
        
        if isinstance(event, OrderFilled):
            self.order_filled.emit(event)
        elif isinstance(event, OrderCanceled):
            self.order_canceled.emit(event)
        elif isinstance(event, OrderRejected):
            self.order_rejected.emit(event)
        else:
            self.order_submitted.emit(event)
            
    def _on_position_event(self, event):
        """Handle position events."""
        from nautilus_trader.model.events import PositionOpened, PositionChanged, PositionClosed
        
        if isinstance(event, PositionOpened):
            self.position_opened.emit(event.position)
        elif isinstance(event, PositionChanged):
            self.position_changed.emit(event.position)
        elif isinstance(event, PositionClosed):
            self.position_closed.emit(event.position)

"""
IBKR Connection Bridge using official ibapi.

Wraps the official IB API for Qt integration, providing signals for connection status.
Uses thread-safe signal emission via QueuedConnection.
"""
import threading
from typing import Optional, List
from PySide6.QtCore import QObject, Signal, Slot, Qt, QThread
from ibapi.client import EClient
from ibapi.wrapper import EWrapper


class IBKRClient(EWrapper, EClient):
    """
    IBKR API Client that bridges to Qt signals.
    """
    
    def __init__(self, bridge: 'IBKRBridge'):
        EWrapper.__init__(self)
        EClient.__init__(self, wrapper=self)
        self._bridge = bridge
        self.nextOrderId = None
        self.accounts: List[str] = []
        self._connected = False
        
    def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=""):
        """Handle errors from TWS."""
        print(f"[IBKR] Error {errorCode}: {errorString}")
        if errorCode in [2104, 2106, 2158]:
            # Info messages about data farm connections
            pass
        else:
            # Use thread-safe signal emission
            self._bridge._emit_error(errorCode, errorString)
            
    def connectAck(self):
        """Called when connection is acknowledged."""
        print("[IBKR] Connection acknowledged")
        
    def nextValidId(self, orderId):
        """Called when connection is complete."""
        print(f"[IBKR] Connected! Order ID: {orderId}")
        self.nextOrderId = orderId
        self._connected = True
        # Use thread-safe signal emission
        self._bridge._emit_connected()
        
    def managedAccounts(self, accountsList):
        """Called with list of managed accounts."""
        self.accounts = accountsList.split(',')
        print(f"[IBKR] Accounts: {self.accounts}")
        # Use thread-safe signal emission
        self._bridge._emit_accounts(self.accounts)
        
    def connectionClosed(self):
        """Called when connection is closed."""
        print("[IBKR] Connection closed")
        self._connected = False
        # Use thread-safe signal emission
        self._bridge._emit_disconnected()


class IBKRBridge(QObject):
    """
    Qt Bridge for IBKR connection.
    
    Provides signals for connection status and events.
    Uses thread-safe signal emission via internal signals with QueuedConnection.
    """
    
    # Signals (these are emitted from the main thread via _emit_* methods)
    connected = Signal()
    disconnected = Signal()
    connection_status_changed = Signal(str)  # "connected", "disconnected", "connecting"
    accounts_received = Signal(list)  # List of account IDs
    error_occurred = Signal(int, str)  # Error code, message
    
    # Internal thread-safe signals
    _internal_connected = Signal()
    _internal_disconnected = Signal()
    _internal_accounts = Signal(list)
    _internal_error = Signal(int, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._client: Optional[IBKRClient] = None
        self._thread: Optional[threading.Thread] = None
        self._host = "127.0.0.1"
        self._port = 7497
        self._client_id = 1
        
        # Connect internal signals with QueuedConnection for thread safety
        self._internal_connected.connect(self._on_internal_connected, Qt.QueuedConnection)
        self._internal_disconnected.connect(self._on_internal_disconnected, Qt.QueuedConnection)
        self._internal_accounts.connect(self._on_internal_accounts, Qt.QueuedConnection)
        self._internal_error.connect(self._on_internal_error, Qt.QueuedConnection)
        
        # Connect public signals for status updates
        self.connected.connect(self._on_connected)
        self.disconnected.connect(self._on_disconnected)
        
    # Internal signal handlers (called from main thread)
    def _on_internal_connected(self):
        self.connected.emit()
        
    def _on_internal_disconnected(self):
        self.disconnected.emit()
        
    def _on_internal_accounts(self, accounts):
        self.accounts_received.emit(accounts)
        
    def _on_internal_error(self, code, msg):
        self.error_occurred.emit(code, msg)
        
    # Thread-safe emit methods (called from background thread)
    def _emit_connected(self):
        self._internal_connected.emit()
        
    def _emit_disconnected(self):
        self._internal_disconnected.emit()
        
    def _emit_accounts(self, accounts):
        self._internal_accounts.emit(accounts)
        
    def _emit_error(self, code, msg):
        self._internal_error.emit(code, msg)
        
    def _on_connected(self):
        self.connection_status_changed.emit("connected")
        
    def _on_disconnected(self):
        self.connection_status_changed.emit("disconnected")
        
    @property
    def is_connected(self) -> bool:
        """Check if connected to TWS."""
        return self._client is not None and self._client._connected
        
    @property
    def accounts(self) -> List[str]:
        """Get list of accounts."""
        if self._client:
            return self._client.accounts
        return []
        
    @Slot()
    def connect_to_tws(self, host: str = "127.0.0.1", port: int = 7497, client_id: int = 1):
        """
        Connect to TWS.
        
        Args:
            host: TWS host
            port: TWS port (7497 for paper, 7496 for live)
            client_id: Unique client ID
        """
        print(f"[IBKR] Connecting to {host}:{port} (clientId={client_id})...")
        
        if self._client and self._client._connected:
            print("[IBKR] Already connected")
            return
            
        self._host = host
        self._port = port
        self._client_id = client_id
        
        self.connection_status_changed.emit("connecting")
        
        # Create client
        self._client = IBKRClient(self)
        
        def connect_and_run():
            """Connect and run message loop in background thread."""
            try:
                self._client.connect(host, port, client_id)
                print("[IBKR] Socket connected, starting message loop...")
                self._client.run()  # This blocks until disconnected
            except Exception as e:
                print(f"[IBKR] Connection error: {e}")
                self._emit_error(-1, str(e))
        
        # Start connection in background thread
        self._thread = threading.Thread(target=connect_and_run, daemon=True)
        self._thread.start()
        print("[IBKR] Connection thread started")
            
    @Slot()
    def disconnect_from_tws(self):
        """Disconnect from TWS."""
        print("[IBKR] Disconnecting...")
        if self._client:
            try:
                self._client.disconnect()
            except Exception as e:
                print(f"[IBKR] Disconnect error: {e}")
            self._client = None
            
    @Slot()
    def reconnect(self):
        """Reconnect to TWS."""
        print("[IBKR] Reconnecting...")
        self.disconnect_from_tws()
        self.connect_to_tws(self._host, self._port, self._client_id)
        
    @Slot(dict)
    def place_order(self, order: dict):
        """
        Place an order to TWS.
        
        Args:
            order: Order dict with symbol, side, type, quantity, etc.
        """
        if not self._client or not self._client._connected:
            print("[IBKR] Cannot place order - not connected")
            return
            
        from ibapi.contract import Contract
        from ibapi.order import Order
        
        # Create contract
        contract = Contract()
        contract.symbol = order["symbol"]
        contract.secType = "STK"
        contract.exchange = order.get("exchange", "SMART")
        contract.currency = "USD"
        
        # Create order
        ib_order = Order()
        ib_order.action = order["side"]
        ib_order.totalQuantity = order["quantity"]
        ib_order.orderType = order["type"]
        ib_order.tif = order.get("tif", "DAY")
        
        if order.get("limit_price"):
            ib_order.lmtPrice = order["limit_price"]
        if order.get("stop_price"):
            ib_order.auxPrice = order["stop_price"]
            
        # Get next order ID
        order_id = self._client.nextOrderId
        self._client.nextOrderId += 1
        
        print(f"[IBKR] Placing order {order_id}: {order['side']} {order['quantity']} {order['symbol']} @ {order['type']}")
        self._client.placeOrder(order_id, contract, ib_order)
        
    @Slot()
    def cancel_all_orders(self):
        """Cancel all open orders."""
        if not self._client or not self._client._connected:
            print("[IBKR] Cannot cancel orders - not connected")
            return
            
        print("[IBKR] Requesting global cancel...")
        self._client.reqGlobalCancel()



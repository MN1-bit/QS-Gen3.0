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
        
    def tickPrice(self, reqId, tickType, price, attrib):
        """Called when price tick is received."""
        # Real-time: 1=bid, 2=ask, 4=last
        # Delayed: 66=bid, 67=ask, 68=last
        if tickType in [4, 68]:  # Last price (real-time or delayed)
            print(f"[IBKR] Last Price {reqId}: ${price:.2f}")
            self._bridge._emit_price(reqId, price)
        elif tickType in [1, 66]:  # Bid
            self._bridge._emit_bid(reqId, price)
        elif tickType in [2, 67]:  # Ask
            self._bridge._emit_ask(reqId, price)
            
    def tickSize(self, reqId, tickType, size):
        """Called when size tick is received."""
        pass
        
    def tickGeneric(self, reqId, tickType, value):
        """Called for generic market data."""
        pass
        
    def historicalData(self, reqId, bar):
        """Called with historical bar data."""
        self._bridge._emit_historical_bar(reqId, bar)
        
    def historicalDataEnd(self, reqId, start, end):
        """Called when historical data is complete."""
        print(f"[IBKR] Historical data complete for reqId={reqId}")
        
    def position(self, account, contract, pos, avgCost):
        """Called with position data."""
        position_data = {
            "account": account,
            "symbol": contract.symbol,
            "secType": contract.secType,
            "position": pos,
            "avgCost": avgCost,
        }
        self._bridge._emit_position(position_data)
        
    def positionEnd(self):
        """Called when position data is complete."""
        print("[IBKR] Position data complete")
        self._bridge._emit_position_end()
        
    def openOrder(self, orderId, contract, order, orderState):
        """Called with open order data."""
        order_data = {
            "orderId": orderId,
            "symbol": contract.symbol,
            "secType": contract.secType,
            "action": order.action,
            "quantity": order.totalQuantity,
            "orderType": order.orderType,
            "status": orderState.status,
        }
        self._bridge._emit_order(order_data)
        
    def openOrderEnd(self):
        """Called when open order data is complete."""
        print("[IBKR] Open orders complete")
        
    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, 
                    permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
        """Called when order status changes."""
        status_data = {
            "orderId": orderId,
            "status": status,
            "filled": filled,
            "remaining": remaining,
            "avgFillPrice": avgFillPrice,
        }
        self._bridge._emit_order_status(status_data)


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
    
    # Market data signals
    price_received = Signal(int, float)  # reqId, last price
    bid_received = Signal(int, float)    # reqId, bid price
    ask_received = Signal(int, float)    # reqId, ask price
    
    # Historical data signals
    historical_bar_received = Signal(int, object)  # reqId, bar data
    
    # Position signals
    position_received = Signal(dict)  # Position data
    positions_complete = Signal()     # All positions received
    
    # Order signals
    order_received = Signal(dict)       # Order data
    order_status_received = Signal(dict)  # Order status update
    
    # Internal thread-safe signals
    _internal_connected = Signal()
    _internal_disconnected = Signal()
    _internal_accounts = Signal(list)
    _internal_error = Signal(int, str)
    _internal_price = Signal(int, float)
    _internal_bid = Signal(int, float)
    _internal_ask = Signal(int, float)
    _internal_historical_bar = Signal(int, object)
    _internal_position = Signal(dict)
    _internal_position_end = Signal()
    _internal_order = Signal(dict)
    _internal_order_status = Signal(dict)
    
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
        self._internal_price.connect(self._on_internal_price, Qt.QueuedConnection)
        self._internal_bid.connect(self._on_internal_bid, Qt.QueuedConnection)
        self._internal_ask.connect(self._on_internal_ask, Qt.QueuedConnection)
        self._internal_historical_bar.connect(self._on_internal_historical_bar, Qt.QueuedConnection)
        self._internal_position.connect(self._on_internal_position, Qt.QueuedConnection)
        self._internal_position_end.connect(self._on_internal_position_end, Qt.QueuedConnection)
        self._internal_order.connect(self._on_internal_order, Qt.QueuedConnection)
        self._internal_order_status.connect(self._on_internal_order_status, Qt.QueuedConnection)
        
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
        
    def _on_internal_price(self, req_id, price):
        print(f"[IBKR] Price {req_id}: ${price:.2f}")
        self.price_received.emit(req_id, price)
        
    def _on_internal_bid(self, req_id, price):
        self.bid_received.emit(req_id, price)
        
    def _on_internal_ask(self, req_id, price):
        self.ask_received.emit(req_id, price)
        
    def _on_internal_historical_bar(self, req_id, bar):
        self.historical_bar_received.emit(req_id, bar)
        
    def _on_internal_position(self, position):
        print(f"[IBKR] Position: {position['symbol']} {position['position']} @ ${position['avgCost']:.2f}")
        self.position_received.emit(position)
        
    def _on_internal_position_end(self):
        self.positions_complete.emit()
        
    def _on_internal_order(self, order):
        print(f"[IBKR] Order: {order['orderId']} {order['action']} {order['quantity']} {order['symbol']} - {order['status']}")
        self.order_received.emit(order)
        
    def _on_internal_order_status(self, status):
        print(f"[IBKR] Order Status: {status['orderId']} - {status['status']}")
        self.order_status_received.emit(status)
        
    # Thread-safe emit methods (called from background thread)
    def _emit_connected(self):
        self._internal_connected.emit()
        
    def _emit_disconnected(self):
        self._internal_disconnected.emit()
        
    def _emit_accounts(self, accounts):
        self._internal_accounts.emit(accounts)
        
    def _emit_error(self, code, msg):
        self._internal_error.emit(code, msg)
        
    def _emit_price(self, req_id, price):
        self._internal_price.emit(req_id, price)
        
    def _emit_bid(self, req_id, price):
        self._internal_bid.emit(req_id, price)
        
    def _emit_ask(self, req_id, price):
        self._internal_ask.emit(req_id, price)
        
    def _emit_historical_bar(self, req_id, bar):
        self._internal_historical_bar.emit(req_id, bar)
        
    def _emit_position(self, position):
        self._internal_position.emit(position)
        
    def _emit_position_end(self):
        self._internal_position_end.emit()
        
    def _emit_order(self, order):
        self._internal_order.emit(order)
        
    def _emit_order_status(self, status):
        self._internal_order_status.emit(status)
        
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
        
    @Slot(str)
    def subscribe_market_data(self, symbol: str, req_id: int = 1001) -> int:
        """
        Subscribe to market data for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., "SPY")
            req_id: Request ID for tracking
            
        Returns:
            Request ID
        """
        if not self._client or not self._client._connected:
            print("[IBKR] Cannot subscribe - not connected")
            return -1
            
        from ibapi.contract import Contract
        
        # Request delayed data (type 3) for paper trading without real-time subscription
        # 1 = Live, 2 = Frozen, 3 = Delayed, 4 = Delayed Frozen
        self._client.reqMarketDataType(3)
        
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        
        print(f"[IBKR] Subscribing to {symbol} (reqId={req_id}, delayed)")
        self._client.reqMktData(req_id, contract, "", False, False, [])
        return req_id
        
    @Slot(int)
    def unsubscribe_market_data(self, req_id: int):
        """
        Unsubscribe from market data.
        
        Args:
            req_id: Request ID from subscribe_market_data
        """
        if not self._client or not self._client._connected:
            return
            
        print(f"[IBKR] Unsubscribing reqId={req_id}")
        self._client.cancelMktData(req_id)
        
    @Slot(str, int)
    def request_historical_data(self, symbol: str, req_id: int = 2001):
        """
        Request historical bar data for a symbol.
        
        Args:
            symbol: Stock symbol
            req_id: Request ID for tracking
        """
        if not self._client or not self._client._connected:
            print("[IBKR] Cannot request historical data - not connected")
            return
            
        from ibapi.contract import Contract
        from datetime import datetime
        
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        
        # Request last 1 day of 5-minute bars
        end_time = datetime.now().strftime("%Y%m%d %H:%M:%S")
        
        print(f"[IBKR] Requesting historical data for {symbol}")
        self._client.reqHistoricalData(
            req_id, contract, end_time, "1 D", "5 mins", "TRADES", 1, 1, False, []
        )
        
    @Slot()
    def request_positions(self):
        """Request all positions from TWS."""
        if not self._client or not self._client._connected:
            print("[IBKR] Cannot request positions - not connected")
            return
            
        print("[IBKR] Requesting positions...")
        self._client.reqPositions()
        
    @Slot()
    def request_open_orders(self):
        """Request all open orders from TWS."""
        if not self._client or not self._client._connected:
            print("[IBKR] Cannot request orders - not connected")
            return
            
        print("[IBKR] Requesting open orders...")
        self._client.reqOpenOrders()


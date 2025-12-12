"""
Test TWS connection using official IB API (ibapi).
Bypasses ib_async/ib_insync to test direct connectivity.
"""
import time
import threading
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract


class TestApp(EWrapper, EClient):
    """Test application for TWS connection."""
    
    def __init__(self):
        EClient.__init__(self, self)
        self.connected = False
        self.accounts = []
        
    def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=""):
        """Handle errors from TWS."""
        print(f"Error {errorCode}: {errorString}")
        if errorCode == 502:
            print("  → TWS is not connected to server")
        elif errorCode == 504:
            print("  → Not connected to TWS")
        elif errorCode == 2104:
            print("  → Market data farm connection OK")
        elif errorCode == 2106:
            print("  → HMDS data farm connection OK")
        elif errorCode == 2158:
            print("  → Sec-def data farm connection OK")
            
    def connectAck(self):
        """Called when connection is acknowledged."""
        print("✅ Connection acknowledged!")
        self.connected = True
        
    def connectionClosed(self):
        """Called when connection is closed."""
        print("Connection closed")
        self.connected = False
        
    def nextValidId(self, orderId):
        """Called when connected - first callback after connection."""
        print(f"✅ Connected! Next valid order ID: {orderId}")
        self.connected = True
        
    def managedAccounts(self, accountsList):
        """Called with list of managed accounts."""
        self.accounts = accountsList.split(',')
        print(f"✅ Accounts: {self.accounts}")


def run_test():
    """Run TWS connection test."""
    print("=" * 50)
    print("TWS Direct Connection Test (ibapi)")
    print("=" * 50)
    
    app = TestApp()
    
    print("\nConnecting to TWS at 127.0.0.1:7497...")
    print("Client ID: 99")
    
    # Connect
    app.connect("127.0.0.1", 7497, clientId=99)
    
    # Start message processing in a thread
    api_thread = threading.Thread(target=app.run, daemon=True)
    api_thread.start()
    
    # Wait for connection
    timeout = 15
    start_time = time.time()
    
    while not app.connected and (time.time() - start_time) < timeout:
        time.sleep(0.5)
        print(".", end="", flush=True)
    
    print()
    
    if app.connected:
        print("\n" + "=" * 50)
        print("✅ SUCCESS - Connected to TWS!")
        print(f"   Accounts: {app.accounts}")
        print("=" * 50)
        
        # Wait a bit more for account info
        time.sleep(2)
        
        # Disconnect
        app.disconnect()
        return True
    else:
        print("\n" + "=" * 50)
        print("❌ FAILED - Connection timeout")
        print("=" * 50)
        app.disconnect()
        return False


if __name__ == "__main__":
    run_test()

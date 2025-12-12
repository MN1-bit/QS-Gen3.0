"""
Official IB API Sample - Based on Interactive Brokers TestApp pattern.
Reference: https://interactivebrokers.github.io/tws-api/
"""
import sys
import time
import threading
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract


class TestApp(EWrapper, EClient):
    """
    Official IB API sample application combining EWrapper and EClient.
    Based on the official TWS API documentation pattern.
    """
    
    def __init__(self):
        EWrapper.__init__(self)
        EClient.__init__(self, wrapper=self)
        self.nextOrderId = None
        self.connected_event = threading.Event()
        
    # EWrapper overrides
    def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=""):
        """Error handling callback."""
        if errorCode == 502:
            print(f"[ERROR 502] Couldn't connect to TWS. Confirm that the application is running.")
        elif errorCode == 504:
            print(f"[ERROR 504] Not connected - need to call connect first.")
        elif errorCode == 2104:
            print(f"[INFO] Market data farm connection is OK")
        elif errorCode == 2106:
            print(f"[INFO] HMDS data farm connection is OK")
        elif errorCode == 2158:
            print(f"[INFO] Sec-def data farm connection is OK")
        else:
            print(f"[ERROR {errorCode}] {errorString}")
            
    def connectAck(self):
        """Called when connection is acknowledged by TWS."""
        print("✅ Connection acknowledged by TWS")
        
    def nextValidId(self, orderId):
        """
        Callback when connection is complete - this is the first callback after connection.
        Provides the next valid order ID.
        """
        self.nextOrderId = orderId
        print(f"✅ Connected! Next valid order ID: {orderId}")
        self.connected_event.set()
        
    def managedAccounts(self, accountsList):
        """Callback with list of managed accounts."""
        accounts = accountsList.split(',')
        print(f"✅ Managed accounts: {accounts}")
        
    def connectionClosed(self):
        """Called when connection is closed."""
        print("⚠️ Connection closed")


def main():
    """Main entry point."""
    print("=" * 60)
    print("Interactive Brokers TWS API - Official Sample Test")
    print("=" * 60)
    
    # Create app instance
    app = TestApp()
    
    # Connection parameters
    host = "127.0.0.1"
    port = 7497  # Paper trading
    clientId = 1
    
    print(f"\nConnecting to TWS at {host}:{port} (clientId={clientId})...")
    print("Make sure TWS is running and API is enabled.")
    print()
    
    # Connect
    try:
        app.connect(host, port, clientId)
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Start the message processing thread
    # This is REQUIRED for callbacks to be processed
    api_thread = threading.Thread(target=app.run, daemon=True)
    api_thread.start()
    
    print("Waiting for connection confirmation...")
    
    # Wait for nextValidId callback (indicates connection complete)
    connected = app.connected_event.wait(timeout=30)
    
    if connected:
        print("\n" + "=" * 60)
        print("🎉 SUCCESS! Connected to TWS API")
        print(f"   Next Order ID: {app.nextOrderId}")
        print("=" * 60)
        
        # Wait a bit more to receive additional callbacks
        time.sleep(3)
        
        # Disconnect
        print("\nDisconnecting...")
        app.disconnect()
    else:
        print("\n" + "=" * 60)
        print("❌ FAILED - Connection timeout (30 seconds)")
        print("   No response received from TWS")
        print("=" * 60)
        app.disconnect()


if __name__ == "__main__":
    main()

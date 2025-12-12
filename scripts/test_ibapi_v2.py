"""
Test TWS connection using official IB API (ibapi) v2.
Improved thread synchronization.
"""
import time
import threading
import socket
from ibapi.client import EClient
from ibapi.wrapper import EWrapper


class TestApp(EWrapper, EClient):
    def __init__(self):
        EWrapper.__init__(self)
        EClient.__init__(self, wrapper=self)
        self.connected = False
        self.accounts = []
        self.connection_ack = threading.Event()
        
    def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=""):
        print(f"[ERROR] {errorCode}: {errorString}")
        # Connection errors
        if errorCode in [502, 504, 10061]:
            self.connection_ack.set()  # Unblock wait
            
    def connectAck(self):
        print("✅ [connectAck] Connection acknowledged!")
        self.connected = True
        self.connection_ack.set()
        
    def nextValidId(self, orderId):
        print(f"✅ [nextValidId] Connected! Order ID: {orderId}")
        self.connected = True
        self.connection_ack.set()
        
    def managedAccounts(self, accountsList):
        self.accounts = accountsList.split(',')
        print(f"✅ [managedAccounts] {self.accounts}")


def run_test():
    print("=" * 50)
    print("TWS Direct Connection Test v2 (ibapi)")
    print("=" * 50)
    
    # First, test raw socket
    print("\n[1] Testing raw socket connection...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 7497))
        if result == 0:
            print("    ✅ Socket connected!")
            # Try to receive some data
            sock.settimeout(3)
            try:
                data = sock.recv(1024)
                print(f"    Data received: {len(data)} bytes")
                print(f"    First 50 bytes: {data[:50]}")
            except socket.timeout:
                print("    ⚠️ Socket connected but no data received (timeout)")
            except Exception as e:
                print(f"    ⚠️ Receive error: {e}")
        else:
            print(f"    ❌ Socket connection failed: error {result}")
        sock.close()
    except Exception as e:
        print(f"    ❌ Socket error: {e}")
    
    # Now test ibapi
    print("\n[2] Testing ibapi connection...")
    app = TestApp()
    
    print(f"    Connecting to 127.0.0.1:7497 (clientId=10)...")
    
    try:
        app.connect("127.0.0.1", 7497, clientId=10)
    except Exception as e:
        print(f"    ❌ Connect failed: {e}")
        return False
    
    # Start message loop in thread
    api_thread = threading.Thread(target=app.run)
    api_thread.start()
    
    # Wait for connection ack with timeout
    print("    Waiting for connection acknowledgement...")
    ack = app.connection_ack.wait(timeout=15)
    
    if app.connected:
        print("\n" + "=" * 50)
        print("✅ SUCCESS!")
        print(f"   Accounts: {app.accounts}")
        print("=" * 50)
        time.sleep(2)
        app.disconnect()
        api_thread.join(timeout=2)
        return True
    else:
        print("\n" + "=" * 50)
        print("❌ FAILED - No connection acknowledgement")
        print("=" * 50)
        app.disconnect()
        api_thread.join(timeout=2)
        return False


if __name__ == "__main__":
    run_test()

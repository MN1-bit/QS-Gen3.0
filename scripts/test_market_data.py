"""
Test market data subscription.

Tests the IBKRBridge market data functionality.
"""
import sys
sys.path.insert(0, "d:/Codes/QS-Gen3.0")

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from src.core.ibkr_bridge import IBKRBridge


def main():
    app = QApplication(sys.argv)
    
    bridge = IBKRBridge()
    
    # Connect to signals
    def on_connected():
        print("\n=== Connected! Subscribing to SPY ===\n")
        bridge.subscribe_market_data("SPY", req_id=1001)
        
    def on_price(req_id, price):
        print(f"[TEST] Got price: reqId={req_id}, price=${price:.2f}")
        
    bridge.connected.connect(on_connected)
    bridge.price_received.connect(on_price)
    
    # Connect to TWS
    print("Connecting to TWS...")
    bridge.connect_to_tws()
    
    # Run for 15 seconds then quit
    QTimer.singleShot(15000, app.quit)
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

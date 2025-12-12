"""
Test IBKR Connection with Nautilus Trader.

Run this script while TWS/Gateway is running to test the connection.
"""
import asyncio
from src.core.trading_node import get_default_paper_config, create_live_trading_node


async def test_connection():
    """Test IBKR connection."""
    print("=" * 50)
    print("QS-Gen3.0 IBKR Connection Test")
    print("=" * 50)
    
    # Get paper trading config
    config = get_default_paper_config()
    print(f"\nConfig: {config}")
    
    # Create trading node
    print("\nCreating TradingNode...")
    try:
        node = create_live_trading_node(config)
        print("TradingNode created successfully!")
        
        # Start the node
        print("\nStarting node (connecting to TWS)...")
        print("This may take a few seconds...")
        
        # Run for 10 seconds to test connection
        await node.start_async()
        print("\n✅ Connected to IBKR!")
        
        # Wait a bit to let the connection stabilize
        await asyncio.sleep(5)
        
        # Print some info
        print("\nConnection info:")
        print(f"  Accounts: {node.trader.accounts()}")
        
        # Stop the node
        print("\nStopping node...")
        await node.stop_async()
        print("Node stopped.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_connection())
    print("\n" + "=" * 50)
    print(f"Test result: {'SUCCESS' if success else 'FAILED'}")
    print("=" * 50)

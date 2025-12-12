"""
TradingNode Configuration and Management for IBKR.

This module sets up the Nautilus TradingNode with IBKR connection.
Uses InteractiveBrokers adapter (TWS or IB Gateway).
"""
from typing import Optional
from pathlib import Path
import os


def create_ibkr_node_config(
    host: str = "127.0.0.1",
    port: int = 7497,  # 7497=TWS Paper, 7496=TWS Live, 4001=Gateway Paper, 4002=Gateway Live
    client_id: int = 1,
    account_id: str = "",  # Leave empty for auto-detection
) -> dict:
    """
    Create configuration for IBKR TradingNode.
    
    Args:
        host: TWS/Gateway host (usually localhost)
        port: TWS/Gateway port
            - 7497: TWS Paper Trading
            - 7496: TWS Live Trading  
            - 4001: IB Gateway Paper
            - 4002: IB Gateway Live
        client_id: Unique client ID (1-32)
        account_id: IBKR account ID (auto-detected if empty)
        
    Returns:
        Configuration dictionary
    """
    return {
        "host": host,
        "port": port,
        "client_id": client_id,
        "account_id": account_id,
    }


def create_live_trading_node(config: dict):
    """
    Create a live TradingNode for IBKR connection.
    
    Args:
        config: Configuration from create_ibkr_node_config()
        
    Returns:
        Configured TradingNode instance
    """
    from nautilus_trader.live.node import TradingNode
    from nautilus_trader.config import TradingNodeConfig, LoggingConfig
    from nautilus_trader.adapters.interactive_brokers.config import (
        InteractiveBrokersDataClientConfig,
        InteractiveBrokersExecClientConfig,
        InteractiveBrokersInstrumentProviderConfig,
        IBMarketDataTypeEnum,
    )
    from nautilus_trader.adapters.interactive_brokers.factories import (
        InteractiveBrokersLiveDataClientFactory,
        InteractiveBrokersLiveExecClientFactory,
    )
    
    # Instrument provider config (minimal)
    instrument_provider_config = InteractiveBrokersInstrumentProviderConfig()
    
    # Data client config
    data_client_config = InteractiveBrokersDataClientConfig(
        ibg_host=config["host"],
        ibg_port=config["port"],
        ibg_client_id=config["client_id"],
        use_regular_trading_hours=True,
        market_data_type=IBMarketDataTypeEnum.DELAYED_FROZEN,  # Use delayed data to avoid subscription issues
        instrument_provider=instrument_provider_config,
    )
    
    # Execution client config
    exec_client_config = InteractiveBrokersExecClientConfig(
        ibg_host=config["host"],
        ibg_port=config["port"],
        ibg_client_id=config["client_id"] + 1,  # Different client ID for exec
        account_id=config["account_id"] if config["account_id"] else None,
        instrument_provider=instrument_provider_config,
    )
    
    # Trading node config (simplified)
    node_config = TradingNodeConfig(
        trader_id="QS-Gen3",
        logging=LoggingConfig(log_level="INFO"),
        data_clients={"IBKR": data_client_config},
        exec_clients={"IBKR": exec_client_config},
    )
    
    # Create node
    node = TradingNode(config=node_config)
    
    # Build and add client factories
    node.add_data_client_factory("IBKR", InteractiveBrokersLiveDataClientFactory)
    node.add_exec_client_factory("IBKR", InteractiveBrokersLiveExecClientFactory)
    node.build()
    
    return node


async def connect_ibkr_async(node) -> bool:
    """
    Connect to IBKR asynchronously.
    
    Args:
        node: TradingNode instance
        
    Returns:
        True if connected successfully
    """
    try:
        await node.start_async()
        return True
    except Exception as e:
        print(f"Failed to connect to IBKR: {e}")
        return False


def get_default_paper_config() -> dict:
    """Get default config for TWS Paper Trading."""
    return create_ibkr_node_config(
        host="127.0.0.1",
        port=7497,  # TWS Paper Trading port
        client_id=1,
    )


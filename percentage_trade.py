#!/usr/bin/env python3
"""
AURACLE Percentage-Based Trading Module
======================================

Extends AURACLE to use percentage-based trade sizing.
Each trade will use a configured percentage of the wallet balance.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional, Union
import requests

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import config after setting path
import config

# Add percentage-based trading configuration to config
config.USE_PERCENTAGE_OF_BALANCE = os.getenv("USE_PERCENTAGE_OF_BALANCE", "false").lower() == "true"
config.MAX_BUY_PERCENTAGE = float(os.getenv("MAX_BUY_PERCENTAGE", "10"))

def get_wallet_balance(wallet_address: str) -> float:
    """
    Get the current SOL balance of the wallet.
    
    Args:
        wallet_address: The Solana wallet address to check
        
    Returns:
        The balance in SOL
    """
    try:
        rpc_url = config.SOLANA_RPC_ENDPOINT
        
        # Prepare RPC request to get balance
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [wallet_address]
        }
        
        # Send request to Solana RPC
        response = requests.post(rpc_url, json=payload)
        data = response.json()
        
        if "result" in data and "value" in data["result"]:
            # Convert lamports to SOL (1 SOL = 10^9 lamports)
            balance_sol = data["result"]["value"] / 1_000_000_000
            logger.info(f"Wallet balance: {balance_sol:.4f} SOL")
            return balance_sol
        else:
            logger.error(f"Failed to get wallet balance: {data}")
            return 0.0
    except Exception as e:
        logger.error(f"Error getting wallet balance: {e}")
        return 0.0

def calculate_trade_amount() -> float:
    """
    Calculate the trade amount based on percentage of wallet balance.
    
    Returns:
        The amount in SOL to use for the trade
    """
    if config.USE_PERCENTAGE_OF_BALANCE:
        # Get current wallet balance
        balance = get_wallet_balance(config.WALLET_ADDRESS)
        
        # Calculate trade amount as percentage of balance
        trade_amount = balance * (config.MAX_BUY_PERCENTAGE / 100.0)
        
        # Apply minimum and maximum limits for safety
        min_amount = 0.01  # Minimum 0.01 SOL
        max_amount = balance * 0.5  # Never use more than 50% of balance as safety measure
        
        trade_amount = max(min_amount, min(trade_amount, max_amount))
        
        logger.info(f"Using {config.MAX_BUY_PERCENTAGE}% of wallet balance: {trade_amount:.4f} SOL")
        return trade_amount
    else:
        # Fall back to fixed amount from config
        return config.MAX_BUY_AMOUNT_SOL

# Monkey patch the original config to use our dynamic trade amount
original_max_buy_amount = config.MAX_BUY_AMOUNT_SOL

def get_dynamic_trade_amount():
    """Dynamic trade amount getter that uses percentage when enabled."""
    if config.USE_PERCENTAGE_OF_BALANCE:
        return calculate_trade_amount()
    return original_max_buy_amount

# Replace the static MAX_BUY_AMOUNT_SOL with our dynamic property
config.__dict__['MAX_BUY_AMOUNT_SOL'] = property(get_dynamic_trade_amount)

# Print confirmation
print(f"✅ Percentage-based trading initialized - Using {config.MAX_BUY_PERCENTAGE}% of balance per trade")

# When imported directly, this will patch the config
if __name__ == "__main__":
    print("⚠️ This module is meant to be imported, not run directly")
    print("Run auracle.py instead after adding 'import percentage_trade' at the top")

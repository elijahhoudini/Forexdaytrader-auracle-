#!/usr/bin/env python3
"""
AURACLE with Percentage-Based Trading
===================================

This is a modified version of auracle.py that implements percentage-based trading.
"""

import sys
import os
import logging
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_wallet_balance(wallet_address):
    """Get the current SOL balance of the wallet."""
    try:
        rpc_url = os.getenv("SOLANA_RPC_ENDPOINT", "https://api.mainnet-beta.solana.com")
        
        # Prepare RPC request
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [wallet_address]
        }
        
        # Send request
        response = requests.post(rpc_url, json=payload)
        data = response.json()
        
        if "result" in data and "value" in data["result"]:
            # Convert lamports to SOL
            balance_sol = data["result"]["value"] / 1_000_000_000
            logger.info(f"Wallet balance: {balance_sol:.4f} SOL")
            return balance_sol
        else:
            logger.error(f"Failed to get wallet balance: {data}")
            return 0.0
    except Exception as e:
        logger.error(f"Error getting wallet balance: {e}")
        return 0.0

def calculate_trade_amount():
    """Calculate the trade amount based on percentage of wallet balance."""
    wallet_address = os.getenv("WALLET_ADDRESS")
    max_buy_percentage = float(os.getenv("MAX_BUY_PERCENTAGE", "10"))
    
    # Get current wallet balance
    balance = get_wallet_balance(wallet_address)
    
    # Calculate trade amount as percentage of balance
    trade_amount = balance * (max_buy_percentage / 100.0)
    
    # Apply minimum and maximum limits for safety
    min_amount = 0.01  # Minimum 0.01 SOL
    max_amount = balance * 0.5  # Never use more than 50% of balance as safety measure
    
    trade_amount = max(min_amount, min(trade_amount, max_amount))
    
    logger.info(f"Using {max_buy_percentage}% of wallet balance: {trade_amount:.4f} SOL")
    
    # Update the environment variable to be used by the original AURACLE
    os.environ["MAX_BUY_AMOUNT_SOL"] = str(trade_amount)
    
    return trade_amount

def main():
    """Main function that applies percentage-based trading and then runs the original AURACLE."""
    print("\n" + "=" * 60)
    print("🚀 AURACLE - Percentage-Based Trading")
    print("=" * 60)
    
    # Check wallet configuration
    wallet_address = os.getenv("WALLET_ADDRESS")
    if not wallet_address:
        print("❌ No wallet address found in .env")
        return
        
    masked_address = wallet_address[:8] + "..." + wallet_address[-8:] if len(wallet_address) > 16 else wallet_address
    print(f"✅ Using wallet: {masked_address}")
    
    # Check if percentage-based trading is enabled
    use_percentage = os.getenv("USE_PERCENTAGE_OF_BALANCE", "false").lower() == "true"
    max_buy_percentage = float(os.getenv("MAX_BUY_PERCENTAGE", "10"))
    
    if use_percentage:
        print(f"✅ Using percentage-based trading: {max_buy_percentage}% of wallet balance per trade")
        
        # Calculate and set trade amount
        trade_amount = calculate_trade_amount()
        print(f"✅ Calculated trade amount: {trade_amount:.4f} SOL")
    else:
        print("⚠️ Percentage-based trading not enabled. Using fixed amount.")
    
    # Confirm live trading
    demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"
    if not demo_mode:
        print("🔥 LIVE TRADING ENABLED - REAL MONEY WILL BE USED")
    else:
        print("🔷 Demo mode enabled - No real money will be used")
    
    # Now import and run the original AURACLE
    try:
        print("\n🚀 Starting AURACLE trading system...")
        
        # Import original auracle module
        import auracle
        
        # Run the main function from the original auracle
        auracle.main()
        
    except ImportError as e:
        print(f"❌ Failed to import auracle module: {e}")
        print("Try running the original auracle.py directly.")
    except Exception as e:
        print(f"❌ Error starting AURACLE: {e}")

if __name__ == "__main__":
    main()

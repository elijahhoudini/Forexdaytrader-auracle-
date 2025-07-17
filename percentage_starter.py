#!/usr/bin/env python3
"""
AURACLE Percentage Trading Starter
================================

Simple script to run AURACLE with percentage-based trading.
"""

import os
import sys
import asyncio
import logging
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_wallet_balance():
    """Get the current SOL balance of the wallet."""
    try:
        wallet_address = os.getenv("WALLET_ADDRESS")
        if not wallet_address:
            logger.error("No wallet address found in .env")
            return 0.0
            
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
    try:
        # Check if percentage-based trading is enabled
        use_percentage = os.getenv("USE_PERCENTAGE_OF_BALANCE", "false").lower() == "true"
        if not use_percentage:
            # Use fixed amount
            amount = float(os.getenv("MAX_BUY_AMOUNT_SOL", "0.05"))
            return amount
            
        # Get percentage setting
        percentage = float(os.getenv("MAX_BUY_PERCENTAGE", "10"))
        
        # Get wallet balance
        balance = get_wallet_balance()
        if balance <= 0:
            logger.warning("Zero or negative balance - using minimum amount")
            return 0.01  # Minimum amount
        
        # Calculate trade amount
        trade_amount = balance * (percentage / 100.0)
        
        # Apply safety limits
        min_amount = 0.01  # Minimum 0.01 SOL
        max_amount = balance * 0.5  # Never use more than 50% as safety measure
        
        trade_amount = max(min_amount, min(trade_amount, max_amount))
        
        # Set the trade amount in environment for AURACLE to use
        os.environ["MAX_BUY_AMOUNT_SOL"] = str(trade_amount)
        
        print(f"💰 Using {percentage}% of wallet balance: {trade_amount:.4f} SOL")
        return trade_amount
        
    except Exception as e:
        logger.error(f"Error calculating trade amount: {e}")
        return float(os.getenv("MAX_BUY_AMOUNT_SOL", "0.05"))  # Fall back to default

def main():
    """Run AURACLE with percentage-based trading."""
    print("\n" + "=" * 60)
    print("🚀 AURACLE - Percentage Trading")
    print("=" * 60)
    
    # Show wallet and trading details
    wallet_address = os.getenv("WALLET_ADDRESS", "")
    if wallet_address:
        masked_address = wallet_address[:8] + "..." + wallet_address[-8:] if len(wallet_address) > 16 else wallet_address
        print(f"✅ Using wallet: {masked_address}")
    else:
        print("❌ No wallet address found in .env")
        return
        
    # Show trading mode
    demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"
    if demo_mode:
        print("🔷 DEMO MODE: No real money will be used")
    else:
        print("🔥 LIVE TRADING: Real money will be used")
        
    # Calculate and set trade amount based on percentage
    trade_amount = calculate_trade_amount()
    
    # Run the original AURACLE
    try:
        print("\n🚀 Starting AURACLE with percentage-based trading...")
        
        # Try different methods to start AURACLE
        if os.path.exists("auracle.py"):
            print("✅ Running auracle.py...")
            os.system(f"python3 auracle.py")
        elif os.path.exists("start.py"):
            print("✅ Running start.py...")
            os.system(f"python3 start.py")
        elif os.path.exists("start_auracle.py"):
            print("✅ Running start_auracle.py...")
            os.system(f"python3 start_auracle.py")
        else:
            print("❌ No AURACLE startup script found")
            
    except Exception as e:
        print(f"❌ Error starting AURACLE: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Program stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        
    print("\n✅ Trading session complete")

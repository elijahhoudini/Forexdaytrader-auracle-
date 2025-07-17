#!/usr/bin/env python3
"""
AURACLE Fixed Trading Starter
===========================

This script applies fixes for transaction signing issues,
configures percentage-based trading, and starts AURACLE.
"""

import os
import sys
import time
import logging
import importlib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_banner():
    """Print the AURACLE startup banner."""
    print("\n" + "=" * 60)
    print("🚀 AURACLE - Fixed Trading System")
    print("=" * 60)

def check_wallet_config():
    """Check wallet configuration and print details."""
    wallet_address = os.getenv("WALLET_ADDRESS", "")
    if wallet_address:
        masked_address = wallet_address[:8] + "..." + wallet_address[-8:] if len(wallet_address) > 16 else wallet_address
        print(f"✅ Using wallet: {masked_address}")
        return True
    else:
        print("❌ No wallet address found in .env")
        return False

def check_trading_mode():
    """Check and print trading mode details."""
    demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"
    if demo_mode:
        print("🔷 DEMO MODE: No real money will be used")
    else:
        print("🔥 LIVE TRADING: Real money will be used")
        print("⚠️ Warning: Real funds will be at risk!")
        
def setup_percentage_based_trading():
    """Setup percentage-based trading configuration."""
    use_percentage = os.getenv("USE_PERCENTAGE_OF_BALANCE", "false").lower() == "true"
    if use_percentage:
        percentage = float(os.getenv("MAX_BUY_PERCENTAGE", "10"))
        print(f"✅ Percentage-based trading: {percentage}% of wallet balance per trade")
        
        # Make sure we have the required modules
        try:
            import requests
            print("✅ Required modules available")
        except ImportError:
            print("⚠️ Missing requests module - installing...")
            os.system("pip install requests")
    else:
        print("📊 Using fixed amount per trade")

def apply_jupiter_fix():
    """Apply the Jupiter transaction signing fix."""
    try:
        # Import our fixed Jupiter API module
        import jupiter_api_fix
        print("✅ Applied Jupiter transaction signing fix")
        return True
    except Exception as e:
        print(f"❌ Failed to apply Jupiter fix: {e}")
        return False

def run_auracle():
    """Run the AURACLE trading system."""
    print("\n🚀 Starting AURACLE with fixes...")
    
    # Find and run the appropriate AURACLE script
    if os.path.exists("auracle.py"):
        print("✅ Running auracle.py...")
        os.system("python3 auracle.py")
    elif os.path.exists("start.py"):
        print("✅ Running start.py...")
        os.system("python3 start.py")
    elif os.path.exists("start_auracle.py"):
        print("✅ Running start_auracle.py...")
        os.system("python3 start_auracle.py")
    else:
        print("❌ No suitable AURACLE script found")
        return False
        
    return True

def main():
    """Main function to start AURACLE with fixes."""
    print_banner()
    
    # Check wallet configuration
    if not check_wallet_config():
        print("❌ Invalid wallet configuration. Please check your .env file.")
        return
        
    # Check trading mode
    check_trading_mode()
    
    # Setup percentage-based trading
    setup_percentage_based_trading()
    
    # Apply Jupiter transaction signing fix
    if not apply_jupiter_fix():
        print("⚠️ Jupiter fix not applied - transactions may fail")
    
    # Run AURACLE
    if not run_auracle():
        print("❌ Failed to start AURACLE")
        return
        
    print("\n✅ AURACLE startup complete with transaction signing fixes")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Program stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        
    print("\n⏹️ AURACLE session ended")

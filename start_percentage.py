#!/usr/bin/env python3
"""
AURACLE with Percentage-Based Trading Starter
===========================================

Starts AURACLE with percentage-based trading enabled.
Each trade will use the configured percentage of wallet balance.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main function to start AURACLE with percentage-based trading."""
    # Display banner
    print("\n" + "=" * 60)
    print("🚀 AURACLE - Percentage-Based Trading")
    print("=" * 60)
    
    # Print wallet info
    wallet_address = os.getenv("WALLET_ADDRESS", "")
    if wallet_address:
        masked_address = wallet_address[:8] + "..." + wallet_address[-8:]
        print(f"✅ Using wallet: {masked_address}")
    else:
        print("❌ No wallet address found in .env")
        return
        
    # Print trading configuration
    print("✅ Using percentage-based trading")
    percentage = os.getenv("MAX_BUY_PERCENTAGE", "10")
    print(f"✅ Each trade will use {percentage}% of wallet balance")
    
    # Live trading confirmation
    demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"
    if not demo_mode:
        print("🔥 LIVE TRADING ENABLED - REAL MONEY WILL BE USED")
        # Ask for confirmation if running in interactive mode
        if sys.stdin.isatty():
            confirmation = input("Press ENTER to confirm or CTRL+C to cancel: ")
    else:
        print("🔷 Demo mode enabled - No real money will be used")
    
    # Import our percentage trading module to patch the config
    try:
        import percentage_trade
        print("✅ Percentage-based trading module loaded")
    except ImportError as e:
        print(f"❌ Failed to load percentage trading module: {e}")
        return
    
    # Import the main auracle module
    try:
        print("🔄 Starting AURACLE...")
        from auracle import main as auracle_main
        auracle_main()
    except ImportError:
        print("❌ Failed to import auracle module")
        print("Trying alternative methods...")
        
        # Try various starting scripts
        scripts = ["auracle.py", "start.py", "start_auracle.py", "main.py"]
        for script in scripts:
            if os.path.exists(script):
                print(f"✅ Found {script} - Executing...")
                os.system(f"python3 {script}")
                return
                
        print("❌ No suitable script found")

if __name__ == "__main__":
    main()

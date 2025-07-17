#!/usr/bin/env python3
"""
AURACLE with Enhanced Trading
===========================

This script runs AURACLE with enhanced trading features including
percentage-based trading that uses a set percentage of your wallet balance.
"""

import os
import sys
import time
import asyncio
import logging
from dotenv import load_dotenv
from typing import Optional, Dict, Any

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedTrader:
    """Enhanced trader with percentage-based trading."""
    
    def __init__(self):
        """Initialize the enhanced trader."""
        self.wallet_address = os.getenv("WALLET_ADDRESS", "")
        self.wallet_private_key = os.getenv("WALLET_PRIVATE_KEY", "")
        self.percentage = float(os.getenv("MAX_BUY_PERCENTAGE", "10"))
        self.demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"
        self.trade_handler = None
        self.enhanced_handler = None
        
    async def initialize(self):
        """Initialize the enhanced trader with all required components."""
        print("\n" + "=" * 60)
        print("🚀 AURACLE - Enhanced Trading System")
        print("=" * 60)
        
        # Show wallet and trading details
        if self.wallet_address:
            masked_address = self.wallet_address[:8] + "..." + self.wallet_address[-8:]
            print(f"✅ Using wallet: {masked_address}")
        else:
            print("❌ No wallet address found")
            return False
            
        # Show trading mode
        if self.demo_mode:
            print("🔷 DEMO MODE: No real money will be used")
        else:
            print("🔥 LIVE TRADING: Real money will be used")
            
        # Show percentage-based trading info
        print(f"✅ Percentage-based trading: {self.percentage}% of balance per trade")
        
        # Import enhanced trading module
        try:
            from enhanced_trading import EnhancedTradeHandler
            print("✅ Enhanced trading module loaded")
            
            # We'll initialize the trade handler later once we have access to the wallet
        except ImportError as e:
            print(f"❌ Failed to load enhanced trading module: {e}")
            return False
            
        return True
        
    async def patch_auracle(self):
        """Patch the AURACLE system with enhanced trading functionality."""
        try:
            # Import original modules
            import auracle
            import trade
            
            # Store original buy/sell functions to restore if needed
            trade_handler = getattr(auracle.auracle_instance, 'trade_handler', None)
            if not trade_handler:
                print("⚠️ No trade handler found in AURACLE instance")
                return False
                
            # Store original methods
            self.original_buy = trade_handler.buy_token
            self.original_sell = trade_handler.sell_token
            
            # Import enhanced trading
            from enhanced_trading import EnhancedTradeHandler
            
            # Create enhanced handler with reference to original wallet
            self.enhanced_handler = EnhancedTradeHandler(trade_handler.wallet, auracle.auracle_instance)
            
            # Replace methods in the original trade handler
            trade_handler.buy_token = self.enhanced_handler.buy_token
            trade_handler.sell_token = self.enhanced_handler.sell_token
            
            print("✅ AURACLE successfully patched with enhanced trading")
            return True
        except Exception as e:
            print(f"❌ Failed to patch AURACLE: {e}")
            return False
            
    async def restore_auracle(self):
        """Restore original AURACLE functionality."""
        try:
            # Import original modules
            import auracle
            
            # Restore original methods
            trade_handler = getattr(auracle.auracle_instance, 'trade_handler', None)
            if trade_handler and hasattr(self, 'original_buy') and hasattr(self, 'original_sell'):
                trade_handler.buy_token = self.original_buy
                trade_handler.sell_token = self.original_sell
                print("✅ Original AURACLE functionality restored")
            return True
        except Exception as e:
            print(f"❌ Failed to restore AURACLE: {e}")
            return False
            
    async def run_auracle(self):
        """Run the AURACLE system with enhanced trading."""
        try:
            # Import auracle module
            import auracle
            
            # Run the main auracle function
            print("\n🚀 Starting AURACLE with enhanced trading...")
            auracle.main()
            
            return True
        except Exception as e:
            print(f"❌ Failed to run AURACLE: {e}")
            return False

async def main():
    """Main entry point for enhanced AURACLE trading."""
    trader = EnhancedTrader()
    
    # Initialize the enhanced trader
    if not await trader.initialize():
        print("❌ Failed to initialize enhanced trader")
        return
        
    try:
        # Run AURACLE with enhanced trading
        await trader.run_auracle()
    except KeyboardInterrupt:
        print("\n👋 Enhanced trading stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Clean up
        try:
            await trader.restore_auracle()
        except:
            pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Program stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        
    # Print final message
    print("\n✅ Enhanced trading session complete")
    print("To restart with normal AURACLE, use: python3 auracle.py")
    print("To restart with enhanced trading, use: python3 enhanced_auracle.py")

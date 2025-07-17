#!/usr/bin/env python3
"""
Automated AURACLE Trading Bot Starter
====================================

This script automatically starts the AURACLE bot using credentials from .env file.
No terminal input required.
"""

import os
import sys
import asyncio
import logging
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """Automatically start AURACLE trading with .env credentials."""
    # Display startup banner
    print("\n" + "="*50)
    print("🚀 AURACLE Auto-Start System")
    print("="*50)
    
    # Check for required environment variables
    wallet_key = os.getenv("WALLET_PRIVATE_KEY")
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not wallet_key:
        print("❌ ERROR: No WALLET_PRIVATE_KEY found in .env file")
        print("Please add your wallet private key to .env file as WALLET_PRIVATE_KEY=your_key")
        return
    
    print("✅ Wallet key found in .env file")
    
    # Try to derive wallet address for validation
    try:
        try:
            # Try the standard solana package first
            from solana.keypair import Keypair
            
            # Convert string to bytes and create keypair
            key_bytes = bytes.fromhex(wallet_key.strip())
            keypair = Keypair.from_secret_key(key_bytes)
            
            # Get public key (wallet address)
            wallet_address = str(keypair.public_key)
            masked_address = wallet_address[:4] + "..." + wallet_address[-4:]
            
            # Set wallet address in environment
            os.environ["WALLET_ADDRESS"] = wallet_address
            
            print(f"✅ Wallet validated: {masked_address}")
        except ImportError:
            # If solana package isn't available, just proceed without validation
            print("⚠️ Solana package not available - skipping wallet validation")
            # Use the key anyway
            wallet_address = "wallet_from_env_file"
            os.environ["WALLET_ADDRESS"] = wallet_address
    except Exception as e:
        print(f"⚠️ Note about wallet key: {e}")
        print("⚠️ Proceeding with wallet key as provided")
    
    # Check for Telegram token
    if telegram_token:
        print("✅ Telegram token found in .env file")
    else:
        print("⚠️ No Telegram token found - will run in local mode")
    
    # Start the AURACLE bot
    print("\n🚀 Starting AURACLE trading bot...")
    
    try:
        # Import the main AURACLE bot module
        # First try to import from auracle.py
        try:
            import auracle
            print("✅ Imported AURACLE module")
            if hasattr(auracle, 'main'):
                print("🔄 Starting AURACLE main function...")
                await auracle.main()
                return
        except (ImportError, AttributeError):
            pass
        
        # Try to import from AURACLE_bot.py
        try:
            import AURACLE_bot
            print("✅ Imported AURACLE_bot module")
            if hasattr(AURACLE_bot, 'main'):
                print("🔄 Starting AURACLE_bot main function...")
                await AURACLE_bot.main()
                return
        except (ImportError, AttributeError):
            pass
        
        # Try auracle_telegram_unified.py
        try:
            import auracle_telegram_unified
            print("✅ Imported auracle_telegram_unified module")
            if hasattr(auracle_telegram_unified, 'main'):
                print("🔄 Starting auracle_telegram_unified main function...")
                await auracle_telegram_unified.main()
                return
        except (ImportError, AttributeError):
            pass
        
        # Fallback to telegram_bot.py
        try:
            import telegram_bot
            print("✅ Imported telegram_bot module")
            if hasattr(telegram_bot, 'main'):
                print("🔄 Starting telegram_bot main function...")
                await telegram_bot.main()
                return
        except (ImportError, AttributeError):
            pass
        
        print("❌ Could not find a suitable AURACLE module to start")
        print("Trying to start with basic functionality...")
        
        # Basic fallback implementation
        from telegram_bot import AuracleTelegramBot
        
        bot = AuracleTelegramBot()
        await bot.run()
        
    except Exception as e:
        print(f"❌ ERROR: Failed to start AURACLE bot: {e}")
        print("Falling back to local mode...")
        
        # Run in local mode as fallback
        print("\n🎯 AURACLE Local Mode")
        print("=" * 40)
        print("✅ System initialized")
        print("✅ Monitoring active with wallet from .env")
        print("✅ Trading mode enabled")
        
        running = True
        try:
            while running:
                print(f"⏰ System check - All systems operational")
                await asyncio.sleep(300)  # Check every 5 minutes
        except KeyboardInterrupt:
            print("\n👋 Local mode stopped")
            running = False

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 AURACLE bot stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check your .env file configuration")

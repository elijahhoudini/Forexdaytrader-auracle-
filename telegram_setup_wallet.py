#!/bin/bash
# telegram_setup_wallet.py - Set up wallet key via Telegram
# Created: July 17, 2025

import os
import sys
import logging
import asyncio
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """Start the wallet setup via Telegram bot."""
    print("==================================")
    print("🔐 AURACLE Telegram Wallet Setup 🔐")
    print("==================================")
    print("This script starts the Telegram bot with wallet key setup enabled.")
    print("Follow these steps:")
    print("1. Open Telegram and message your bot")
    print("2. Send /set_wallet_key command")
    print("3. Follow the prompts to securely set your wallet key")
    print("==================================")
    
    # Load environment variables
    load_dotenv()
    
    # Check if Telegram token is set
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ Error: No Telegram bot token found.")
        print("Please set TELEGRAM_BOT_TOKEN in your .env file.")
        return
    
    try:
        # Import the telegram bot
        from telegram_bot import AuracleTelegramBot
        
        # Create and start the bot
        bot = AuracleTelegramBot(token=token)
        print("✅ Starting Telegram bot...")
        print("Send /set_wallet_key command to your bot in Telegram.")
        print("Press Ctrl+C to exit when done.")
        
        await bot.run()
    except ImportError:
        print("❌ Error: Telegram bot library not available.")
        print("Please install required packages with:")
        print("pip install -r requirements.txt")
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped.")

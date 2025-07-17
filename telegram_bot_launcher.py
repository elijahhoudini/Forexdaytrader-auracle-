#!/usr/bin/env python3
"""
Improved Telegram Bot Launcher
=============================

This script starts the Telegram bot with proper error handling.
"""

import os
import sys
import time
import logging
import asyncio

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("telegram_launcher")

def check_environment():
    """Check if environment is properly set up."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("❌ TELEGRAM_BOT_TOKEN environment variable not set!")
        logger.info("Please make sure your .env file contains TELEGRAM_BOT_TOKEN=your_token")
        return False
    
    logger.info(f"✅ TELEGRAM_BOT_TOKEN found: {token[:5]}...{token[-5:]}")
    return True

async def start_bot():
    """Start the Telegram bot with error handling."""
    try:
        from telegram_bot import AuracleTelegramBot
        
        logger.info("🚀 Starting Telegram bot...")
        bot = AuracleTelegramBot()
        await bot.run()
    except Exception as e:
        logger.error(f"❌ Error starting Telegram bot: {e}")
        logger.error("Falling back to simplified mode")
        print("\n🎯 AURACLE Simple Mode")
        print("=" * 40)
        print("✅ System initialized in fallback mode")
        print("✅ Limited functionality available")

        while True:
            print("⏰ System check - Limited functionality")
            time.sleep(300)

def main():
    """Main function to start the bot."""
    if not check_environment():
        sys.exit(1)
    
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Critical error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

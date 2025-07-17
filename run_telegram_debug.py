#!/usr/bin/env python3
"""
Debug launcher for Telegram bot
"""
import os
import logging
import asyncio
from telegram_bot import AuracleTelegramBot

# Setup verbose logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

async def main():
    """Run the bot with debug logging"""
    print(f"Starting bot with token: {os.getenv('TELEGRAM_BOT_TOKEN')[:5]}...{os.getenv('TELEGRAM_BOT_TOKEN')[-5:]}")
    bot = AuracleTelegramBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())

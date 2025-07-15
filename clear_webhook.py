#!/usr/bin/env python3
"""
Clear Telegram Webhook
======================

Clears any existing webhook to prevent conflicts.
"""

import asyncio
import sys
import os
from telegram import Bot

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def clear_webhook():
    """Clear telegram webhook"""
    try:
        import config
        
        token = config.TELEGRAM_BOT_TOKEN
        if not token:
            print("❌ Error: TELEGRAM_BOT_TOKEN not found!")
            return False
        
        bot = Bot(token=token)
        
        print("🔄 Clearing telegram webhook...")
        await bot.delete_webhook()
        print("✅ Webhook cleared successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error clearing webhook: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(clear_webhook())

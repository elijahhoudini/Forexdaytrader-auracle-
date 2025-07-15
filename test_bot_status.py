#!/usr/bin/env python3
"""
Test AURACLE Telegram Bot Status
===============================

Quick test to verify bot is working properly.
"""

import asyncio
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_bot_status():
    """Test if bot is responding"""
    try:
        import config
        from telegram import Bot
        
        token = config.TELEGRAM_BOT_TOKEN
        if not token:
            print("❌ Error: TELEGRAM_BOT_TOKEN not found!")
            return False
        
        bot = Bot(token=token)
        
        print("🔄 Testing bot connection...")
        
        # Test basic bot info
        bot_info = await bot.get_me()
        print(f"✅ Bot connected: @{bot_info.username}")
        print(f"📱 Bot name: {bot_info.first_name}")
        
        # Test getting updates (should be empty if bot is polling)
        updates = await bot.get_updates(limit=1)
        print(f"📨 Recent updates: {len(updates)} (polling mode)")
        
        return True
        
    except Exception as e:
        print(f"❌ Bot test error: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 AURACLE Bot Status Test")
    print("=" * 30)
    
    success = await test_bot_status()
    
    if success:
        print("\n✅ Bot is working properly!")
        print("💬 Go to Telegram and send /start to your bot")
    else:
        print("\n❌ Bot has issues!")

if __name__ == "__main__":
    asyncio.run(main())

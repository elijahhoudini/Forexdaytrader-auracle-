#!/usr/bin/env python3
"""
AURACLE Unified Start Script
===========================

Simple script to start AURACLE with unified Telegram control.
"""

import asyncio
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Start AURACLE with unified Telegram control"""
    print("🚀 AURACLE - Unified Telegram Control")
    print("=" * 50)
    
    # Import after path setup
    try:
        from auracle_telegram_unified import AuracleUnifiedBot
        import config
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed.")
        return
    
    # Get token
    token = getattr(config, 'TELEGRAM_BOT_TOKEN', None) or os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found!")
        print("Please set it in config.py or environment variables.")
        return
    
    print(f"✅ Bot token configured")
    print(f"📱 Starting unified Telegram bot...")
    
    # Create and run bot
    bot = AuracleUnifiedBot(token)
    
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

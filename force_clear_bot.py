#!/usr/bin/env python3
"""
Force Clear Telegram Bot State
==============================

Aggressively clears bot state and ensures clean startup.
"""

import asyncio
import sys
import os
import time
import signal
import subprocess

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def force_clear_bot_state():
    """Force clear all bot state"""
    try:
        import config
        from telegram import Bot
        
        token = config.TELEGRAM_BOT_TOKEN
        if not token:
            print("❌ Error: TELEGRAM_BOT_TOKEN not found!")
            return False
        
        bot = Bot(token=token)
        
        print("🔄 Clearing telegram webhook...")
        await bot.delete_webhook()
        
        print("🔄 Clearing pending updates...")
        await bot.get_updates(offset=-1)
        
        print("⏳ Waiting for state to clear...")
        await asyncio.sleep(5)
        
        print("✅ Bot state cleared successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error clearing bot state: {e}")
        return False

def kill_all_processes():
    """Kill all related processes"""
    print("🔄 Killing all related processes...")
    
    # Kill all python processes
    try:
        subprocess.run(['pkill', '-9', '-f', 'python'], check=False)
        print("✅ Python processes killed")
    except Exception as e:
        print(f"⚠️ Error killing python processes: {e}")
    
    # Kill specific bot processes
    try:
        subprocess.run(['pkill', '-9', '-f', 'auracle'], check=False)
        print("✅ AURACLE processes killed")
    except Exception as e:
        print(f"⚠️ Error killing AURACLE processes: {e}")
    
    time.sleep(3)

async def main():
    """Main function"""
    print("🚀 Force Bot State Clear")
    print("=" * 30)
    
    # Kill all processes first
    kill_all_processes()
    
    # Clear bot state
    await force_clear_bot_state()
    
    print("✅ Bot state cleared - ready for clean startup")

if __name__ == "__main__":
    asyncio.run(main())

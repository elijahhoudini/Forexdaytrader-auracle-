#!/usr/bin/env python3
"""
Single Instance AURACLE Startup Script
=====================================

Ensures only one instance of AURACLE Telegram bot is running.
Kills any existing instances before starting a new one.
"""

import os
import sys
import time
import signal
import psutil
import asyncio
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def kill_existing_instances():
    """Kill any existing AURACLE bot instances"""
    current_pid = os.getpid()
    killed_count = 0
    
    print("🔍 Checking for existing AURACLE instances...")
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['pid'] == current_pid:
                continue
                
            cmdline = proc.info['cmdline']
            if cmdline and any('auracle' in arg.lower() for arg in cmdline):
                print(f"🛑 Killing existing AURACLE process: PID {proc.info['pid']}")
                proc.terminate()
                killed_count += 1
                
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if killed_count > 0:
        print(f"✅ Killed {killed_count} existing instances")
        print("⏳ Waiting for processes to terminate...")
        time.sleep(3)
    else:
        print("✅ No existing instances found")

def validate_configuration():
    """Validate that all required configuration is present"""
    print("🔍 Validating AURACLE configuration...")
    
    try:
        import config
        
        # Check required settings
        required_settings = [
            'TELEGRAM_BOT_TOKEN',
            'WALLET_PRIVATE_KEY',
            'WALLET_ADDRESS'
        ]
        
        missing = []
        for setting in required_settings:
            if not hasattr(config, setting) or not getattr(config, setting):
                missing.append(setting)
        
        if missing:
            print(f"❌ Missing required configuration: {', '.join(missing)}")
            return False
        
        # Check trading mode
        trading_mode = "🔥 LIVE TRADING" if not config.DEMO_MODE else "🧪 DEMO MODE"
        print(f"📊 Trading mode: {trading_mode}")
        
        if not config.DEMO_MODE:
            print("⚠️  🔥 LIVE TRADING ENABLED - Real money at risk!")
            print("⚠️  Ensure you have tested thoroughly in demo mode")
            print("⚠️  Start with small amounts and monitor closely")
        
        print("✅ Configuration validation passed")
        return True
        
    except ImportError as e:
        print(f"❌ Configuration error: {e}")
        return False
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False

async def start_bot():
    """Start the AURACLE bot"""
    print("📱 Starting unified Telegram bot...")
    
    try:
        from auracle_telegram_unified import AuracleUnifiedBot
        import config
        
        # Get token
        token = config.TELEGRAM_BOT_TOKEN
        if not token:
            print("❌ Error: TELEGRAM_BOT_TOKEN not found!")
            return False
        
        # Create and run bot
        bot = AuracleUnifiedBot(token)
        await bot.run()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested by user")
        return True
    except Exception as e:
        print(f"❌ Bot error: {e}")
        return False

def main():
    """Main entry point"""
    print("🚀 AURACLE - Single Instance Startup")
    print("=" * 50)
    
    # Kill existing instances
    kill_existing_instances()
    
    # Validate configuration
    if not validate_configuration():
        print("❌ Configuration validation failed!")
        sys.exit(1)
    
    # Start bot
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        print("\n✅ AURACLE stopped by user")
    except Exception as e:
        print(f"❌ Startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

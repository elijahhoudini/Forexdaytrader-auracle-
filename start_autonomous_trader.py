#!/usr/bin/env python3
"""
AURACLE Autonomous AI Trading Bot - Simple Launcher
=================================================

Easy launcher script for the autonomous trading bot.
"""

import os
import sys
import asyncio
from pathlib import Path

def print_banner():
    """Print startup banner."""
    print("=" * 60)
    print("🚀 AURACLE AUTONOMOUS AI TRADING BOT")
    print("Enhanced Production-Ready System")
    print("=" * 60)

def check_environment():
    """Check if environment is properly configured."""
    print("🔍 Checking environment configuration...")
    
    required_vars = ['WALLET_PRIVATE_KEY', 'TELEGRAM_BOT_TOKEN']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("\n📋 Setup Instructions:")
        print("1. Copy .env.example to .env")
        print("2. Fill in your wallet private key and Telegram bot token")
        print("3. Run this script again")
        return False
    
    # Check if .env file exists
    if not Path('.env').exists() and not all(os.getenv(var) for var in required_vars):
        print("⚠️ No .env file found. Please create one based on .env.example")
        return False
    
    print("✅ Environment configuration looks good")
    return True

def get_trading_mode():
    """Get trading mode from user or environment."""
    live_mode = os.getenv('LIVE_MODE', '').lower() == 'true'
    
    if live_mode:
        print("🔴 LIVE TRADING MODE DETECTED")
        print("⚠️ This will trade with REAL money!")
        
        confirm = input("\nAre you sure you want to continue? (yes/no): ").lower()
        if confirm != 'yes':
            print("👋 Trading cancelled for safety")
            return None
    else:
        print("🟡 DEMO MODE - Safe for testing")
    
    return live_mode

async def main():
    """Main launcher function."""
    print_banner()
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Get trading mode
    live_mode = get_trading_mode()
    if live_mode is None:
        sys.exit(0)
    
    print("\n🚀 Starting AURACLE Autonomous AI Trading Bot...")
    print("Press Ctrl+C to stop safely\n")
    
    try:
        # Import and start the autonomous trader
        from autonomous_ai_trader import AutonomousAITrader
        
        trader = AutonomousAITrader(live_mode=live_mode)
        await trader.start()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n🔧 Possible fixes:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Install additional packages: pip install websockets aiofiles base58")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your .env file configuration")
        print("2. Verify your wallet has sufficient balance")
        print("3. Test with demo mode first")
        print("4. Check the logs/ directory for detailed error information")
        sys.exit(1)

if __name__ == "__main__":
    # Load environment from .env file if it exists
    try:
        from dotenv import load_dotenv
        if Path('.env').exists():
            load_dotenv()
            print("📄 Loaded configuration from .env file")
    except ImportError:
        pass
    
    # Run the main launcher
    asyncio.run(main())
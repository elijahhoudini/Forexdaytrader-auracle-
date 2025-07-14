#!/usr/bin/env python3
"""
AURACLE Bot - One-Click Deployment Script
========================================

This script provides a one-click deployment for the AURACLE bot.
It handles configuration, validation, and startup automatically.
"""

import os
import sys
import time
import signal
import subprocess
from typing import Dict, Any


def print_banner():
    """Print startup banner."""
    print("=" * 60)
    print("🚀 AURACLE Bot - One-Click Deployment")
    print("=" * 60)
    print("🤖 Autonomous AI-Powered Solana Trading Bot")
    print("👤 Built for Traveler 5798")
    print("🔗 https://github.com/elijahhoudini/Final-")
    print("=" * 60)


def check_dependencies():
    """Check if all required dependencies are installed."""
    print("📦 Checking dependencies...")
    
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8+ required")
            return False
        
        # Check required packages
        required_packages = [
            'requests', 'pandas', 'numpy', 'solana', 'solders',
            'python-telegram-bot', 'web3', 'cryptography', 'aiohttp',
            'httpx', 'python-dotenv', 'base58'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print("❌ Missing packages:", ', '.join(missing_packages))
            print("💡 Run: pip install -r requirements.txt")
            return False
        
        print("✅ All dependencies are installed")
        return True
        
    except Exception as e:
        print(f"❌ Dependency check failed: {e}")
        return False


def create_env_file():
    """Create .env file if it doesn't exist."""
    env_file = ".env"
    
    if os.path.exists(env_file):
        print("✅ .env file already exists")
        return True
    
    print("📝 Creating .env file...")
    
    env_content = """# AURACLE Bot Configuration
# =========================

# Trading Configuration
DEMO_MODE=true
MAX_BUY_AMOUNT_SOL=0.01
SCAN_INTERVAL_SECONDS=45
PROFIT_TARGET_PERCENTAGE=0.15
STOP_LOSS_PERCENTAGE=-0.08
MAX_DAILY_TRADES=50
MAX_OPEN_POSITIONS=10

# Solana Network
SOLANA_RPC_ENDPOINT=https://api.mainnet-beta.solana.com

# Wallet Configuration (for live trading)
# WALLET_ADDRESS=your_wallet_address_here
# WALLET_PRIVATE_KEY=your_private_key_here

# Telegram Bot (optional)
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=7661187219:AAHuqb1IB9QtYxHeDbTbnkobwK1rFtyvqvk
TELEGRAM_CHAT_ID=7661187219

# Jupiter Configuration
JUPITER_SLIPPAGE_BPS=50
JUPITER_PRIORITY_FEE=1000

# Safety Settings
MIN_LIQUIDITY_THRESHOLD=15000
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ .env file created with default configuration")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False


def validate_configuration():
    """Validate bot configuration."""
    print("🔍 Validating configuration...")
    
    try:
        import config
        if config.validate_config():
            print("✅ Configuration is valid")
            return True
        else:
            print("❌ Configuration validation failed")
            return False
    except Exception as e:
        print(f"❌ Configuration validation error: {e}")
        return False


def run_safety_checks():
    """Run safety checks before deployment."""
    print("🛡️  Running safety checks...")
    
    try:
        # Import and check demo mode
        import config
        
        if not config.get_demo_mode():
            print("⚠️  WARNING: Demo mode is disabled!")
            print("🔥 This will execute real trades with real money!")
            response = input("Are you sure you want to proceed? (type 'YES' to continue): ")
            if response != 'YES':
                print("❌ Deployment cancelled for safety")
                return False
            print("🔥 Live trading mode confirmed")
        else:
            print("✅ Demo mode is enabled - safe for testing")
        
        # Check wallet configuration for live mode
        if not config.get_demo_mode():
            if not config.WALLET_ADDRESS or not config.WALLET_PRIVATE_KEY:
                print("❌ Live trading requires WALLET_ADDRESS and WALLET_PRIVATE_KEY")
                print("💡 Please configure these in your .env file")
                return False
        
        print("✅ Safety checks passed")
        return True
        
    except Exception as e:
        print(f"❌ Safety check failed: {e}")
        return False


def start_bot():
    """Start the AURACLE bot."""
    print("🚀 Starting AURACLE bot...")
    
    try:
        # Import and run auracle
        from auracle import main
        main()
        
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot startup failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Try fallback
        try:
            print("⚠️ Trying fallback startup method...")
            exec(open("main.py").read())
        except Exception as fallback_error:
            print(f"❌ Fallback startup also failed: {fallback_error}")
            return False
    
    return True


def main():
    """Main deployment function."""
    print_banner()
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install required packages.")
        sys.exit(1)
    
    # Step 2: Create .env file
    if not create_env_file():
        print("\n❌ Failed to create configuration file.")
        sys.exit(1)
    
    # Step 3: Validate configuration
    if not validate_configuration():
        print("\n❌ Configuration validation failed.")
        sys.exit(1)
    
    # Step 4: Run safety checks
    if not run_safety_checks():
        print("\n❌ Safety checks failed.")
        sys.exit(1)
    
    # Step 5: Start bot
    print("\n🎯 All checks passed! Starting AURACLE...")
    print("=" * 60)
    
    start_bot()
    
    print("\n" + "=" * 60)
    print("🏁 AURACLE deployment completed")
    print("=" * 60)


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
AURACLE Bot - Unified Replit Entry Point
========================================

Simple one-click deployment for Replit:
1. Import repository
2. Click "Run" 
3. (Optional) Add secrets for live trading

Always starts in demo mode for safety unless live trading secrets are present.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

# Bot information
BOT_NAME = "AURACLE"
BOT_VERSION = "1.0.0"
TRAVELER_ID = "5798"

def print_header():
    """Print startup header."""
    print("=" * 60)
    print(f"🚀 {BOT_NAME} v{BOT_VERSION} - Unified Entry Point")
    print(f"👤 Traveler ID: {TRAVELER_ID}")
    print("=" * 60)

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Checking dependencies...")
    
    # Check for key dependencies
    required_packages = [
        'solana', 'requests', 'pandas', 'numpy', 'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️  Missing {len(missing_packages)} packages")
        print("💡 On Replit, dependencies auto-install on first run")
        print("📝 Locally, run: pip install -r requirements.txt")
        
        # Try to install if we're not on Replit
        if not os.getenv('REPLIT_ENVIRONMENT'):
            try:
                print("🔧 Attempting to install missing packages...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
                print("✅ Dependencies installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"⚠️  Could not auto-install: {e}")
    
    return True

def setup_environment():
    """Set up environment variables and defaults."""
    print("\n🔧 Setting up environment...")
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print(f"✅ Data directory: {data_dir.absolute()}")
    
    # Load environment variables from .env if it exists
    env_file = Path(".env")
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print("✅ Loaded .env file")
        except ImportError:
            print("⚠️  python-dotenv not available, using os.environ")
    
    # Set safe defaults
    os.environ.setdefault("DEMO_MODE", "true")
    os.environ.setdefault("TELEGRAM_ENABLED", "true")
    os.environ.setdefault("LOG_LEVEL", "INFO")
    os.environ.setdefault("MAX_BUY_AMOUNT_SOL", "0.01")
    os.environ.setdefault("PROFIT_TARGET_PERCENTAGE", "0.15")
    os.environ.setdefault("STOP_LOSS_PERCENTAGE", "-0.08")
    os.environ.setdefault("SCAN_INTERVAL_SECONDS", "45")
    os.environ.setdefault("MAX_DAILY_TRADES", "50")
    os.environ.setdefault("MAX_OPEN_POSITIONS", "10")
    
    return True

def check_secrets():
    """Check what secrets are available and determine mode."""
    print("\n🔍 Checking configuration...")
    
    # Check for live trading secrets
    wallet_private_key = os.getenv("WALLET_PRIVATE_KEY")
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    # Determine mode
    has_wallet = wallet_private_key and wallet_private_key.strip() and wallet_private_key != "your_solana_private_key_here"
    has_telegram = telegram_bot_token and telegram_bot_token.strip() and telegram_bot_token != "your_telegram_bot_token_here"
    
    # Force demo mode unless explicitly disabled and we have wallet
    demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"
    if not demo_mode and not has_wallet:
        print("⚠️  Live trading requested but no wallet private key found")
        print("🔒 Forcing demo mode for safety")
        demo_mode = True
        os.environ["DEMO_MODE"] = "true"
    
    # Display configuration status
    print(f"🔑 Wallet configured: {'✅' if has_wallet else '❌'}")
    print(f"📱 Telegram configured: {'✅' if has_telegram else '❌'}")
    print(f"📊 Trading mode: {'🔶 DEMO MODE (Safe)' if demo_mode else '🔥 LIVE TRADING'}")
    
    if not demo_mode:
        print("\n⚠️  🔥 LIVE TRADING ENABLED - Real money at risk!")
        print("⚠️  Make sure you have tested thoroughly in demo mode")
        print("⚠️  Start with small amounts and monitor closely")
    
    # Show what features are available
    print("\n🎯 Available features:")
    print("✅ AI token discovery and filtering")
    print("✅ Risk assessment and fraud detection")
    print("✅ Automated trading with stop-loss/take-profit")
    print("✅ Position management and monitoring")
    print("✅ Comprehensive logging and statistics")
    print(f"{'✅' if has_telegram else '❌'} Telegram notifications and control")
    print(f"{'✅' if not demo_mode else '❌'} Live trading (real money)")
    
    return {
        'demo_mode': demo_mode,
        'has_wallet': has_wallet,
        'has_telegram': has_telegram
    }

def show_missing_secrets_help():
    """Show help for users who want to enable live trading."""
    print("\n" + "=" * 60)
    print("🔧 TO ENABLE LIVE TRADING:")
    print("=" * 60)
    print("Add these secrets in Replit (Secrets tab):")
    print()
    print("Required for live trading:")
    print("  WALLET_PRIVATE_KEY=your_solana_private_key_here")
    print("  DEMO_MODE=false")
    print()
    print("Optional for enhanced features:")
    print("  TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here")
    print("  TELEGRAM_CHAT_ID=your_telegram_chat_id_here")
    print("  PURCHASED_RPC=your_premium_rpc_endpoint")
    print("  MORALIS_API_KEY=your_moralis_api_key")
    print()
    print("⚠️  WARNING: Only enable live trading after testing in demo mode!")
    print("=" * 60)

def run_auracle_bot():
    """Run the main AURACLE bot."""
    try:
        print("\n🚀 Starting AURACLE Bot...")
        
        # Add current directory to Python path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Import and run the bot
        from auracle import main as auracle_main
        auracle_main()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 This might be due to missing dependencies")
        
        # Try alternative import method
        try:
            print("🔄 Trying alternative import method...")
            from auracle import Auracle
            bot = Auracle()
            bot.run()
        except Exception as e2:
            print(f"❌ Alternative import failed: {e2}")
            
            # Try the backup bot
            try:
                print("🔄 Trying backup bot...")
                import AURACLE_bot
                print("✅ Backup bot started successfully")
            except Exception as e3:
                print(f"❌ All import methods failed: {e3}")
                raise

    except Exception as e:
        print(f"❌ Error running AURACLE: {e}")
        import traceback
        traceback.print_exc()
        raise

def main():
    """Main entry point for unified Replit deployment."""
    try:
        print_header()
        
        # Basic checks
        if not check_python_version():
            return 1
        
        if not install_dependencies():
            return 1
        
        if not setup_environment():
            return 1
        
        # Check configuration
        config = check_secrets()
        
        # Show help if in demo mode
        if config['demo_mode']:
            show_missing_secrets_help()
        
        # Run the bot
        run_auracle_bot()
        
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Startup error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
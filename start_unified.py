#!/usr/bin/env python3
"""
AURACLE + Solana Trading Bot - Unified Startup Script
====================================================

This script makes it easy to run both the AURACLE bot and the Solana Trading Bot on Replit.
Just copy the repository to Replit and click 'Run'.
"""

import os
import sys
import subprocess
import argparse

def install_dependencies():
    """Check if dependencies are available."""
    print("📦 Checking dependencies...")
    
    # Check if key dependencies are already installed
    try:
        import solana
        import requests
        import pandas
        print("✅ Key dependencies found")
        return True
    except ImportError as e:
        print(f"⚠️  Missing dependency: {e}")
        print("💡 On Replit, dependencies will be auto-installed")
        print("📝 Locally, run: pip install -r requirements.txt")
        return True  # Continue anyway on Replit
    
    # Check telegram dependency separately (optional)
    try:
        import telegram
        print("✅ Telegram library found - Full bot features available")
    except ImportError:
        print("⚠️  Telegram library not found - Bot will run without Telegram integration")
        print("📝 To enable Telegram: pip install python-telegram-bot>=20.0")

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    return True

def run_auracle():
    """Run the original AURACLE bot."""
    print("🤖 Starting AURACLE Bot...")
    try:
        # Import and run the bot
        print("🔍 Importing AURACLE modules...")
        import config
        print("✅ Configuration loaded")
        
        print("🚀 Starting AURACLE bot...")
        from auracle import main as auracle_main
        auracle_main()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 This might be due to missing dependencies.")
        print("📝 Please run: pip install -r requirements.txt")
        sys.exit(1)

def run_solbot():
    """Run the Solana Trading Bot (Telegram-based)."""
    print("📱 Starting Solana Trading Bot (Telegram)...")
    try:
        # Add src to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        # Import and run the bot
        print("🔍 Importing Solbot modules...")
        from solbot.main import main as solbot_main
        print("✅ Solbot modules loaded")
        
        print("🚀 Starting Solbot...")
        solbot_main()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you have configured the environment variables.")
        print("📝 Check .env.example for required configuration.")
        sys.exit(1)

def main():
    """Main startup function."""
    parser = argparse.ArgumentParser(description='Run AURACLE or Solana Trading Bot')
    parser.add_argument('--bot', choices=['auracle', 'solbot', 'both'], default='auracle',
                        help='Which bot to run (default: auracle)')
    
    args = parser.parse_args()
    
    print("🚀 Unified Solana Trading Bot Startup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create data directory
    os.makedirs("data", exist_ok=True)
    
    print(f"\n🤖 Starting bot mode: {args.bot}")
    print("=" * 50)
    
    try:
        if args.bot == 'auracle':
            run_auracle()
        elif args.bot == 'solbot':
            run_solbot()
        elif args.bot == 'both':
            # This would require threading or multiprocessing
            print("⚠️  Running both bots simultaneously is not yet implemented")
            print("💡 Please choose either 'auracle' or 'solbot'")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("📝 Check the logs for more details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
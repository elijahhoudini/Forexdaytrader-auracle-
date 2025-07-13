#!/usr/bin/env python3
"""
AURACLE Bot - Simple Startup Script for Replit
==============================================

This script makes it easy to run the AURACLE bot on Replit.
Just copy the repository to Replit and click 'Run'.
"""

import os
import sys
import subprocess

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
        print("📝 To enable Telegram: pip install python-telegram-bot==12.0.0")

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    return True

def main():
    """Main startup function."""
    print("🚀 AURACLE Bot Startup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create data directory
    os.makedirs("data", exist_ok=True)
    
    print("\n🤖 Starting AURACLE Bot...")
    print("=" * 40)
    
    # Import and run the bot
    try:
        # Try to import the bot module
        print("🔍 Importing bot modules...")
        import config
        print("✅ Configuration loaded")
        
        print("🚀 Starting bot...")
        from auracle import main as auracle_main
        auracle_main()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 This might be due to missing dependencies.")
        print("📝 Please run: pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("📝 Check the logs for more details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
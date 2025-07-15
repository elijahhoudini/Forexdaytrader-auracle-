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

from auracle_telegram_unified import AuracleUnifiedBot
import config

def main():
    """Start AURACLE with unified Telegram control"""
    print("� AURACLE - Unified Telegram Control")
    print("=" * 50)
    
    # Get token
    token = config.TELEGRAM_BOT_TOKEN or os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found!")
        print("Please set it in config.py or environment variables.")
        return
    
    print(f"✅ Bot token configured")
    print(f"� Starting unified Telegram bot...")
    
    # Create and run bot
    bot = AuracleUnifiedBot(token)
    
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("\n� Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
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
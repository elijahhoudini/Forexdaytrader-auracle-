#!/usr/bin/env python3
"""
AURACLE Production Bot - Main Entry Point
========================================

Production-ready AURACLE trading bot with full Telegram integration.
All required commands implemented and ready for continuous operation.
"""

import asyncio
import os
import sys
import signal
import logging
from typing import Optional

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our components
import config
from unified_telegram_bot import AuracleTelegramBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/auracle_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AuracleProductionBot:
    """Main production bot controller"""
    
    def __init__(self):
        self.telegram_bot: Optional[AuracleTelegramBot] = None
        self.running = False
        
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            self.running = False
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def start(self):
        """Start the production bot"""
        logger.info("🚀 Starting AURACLE Production Bot...")
        
        # Validate configuration
        if not config.validate_config():
            logger.error("❌ Configuration validation failed")
            return False
        
        # Check for required token
        token = config.TELEGRAM_BOT_TOKEN or os.getenv('TELEGRAM_BOT_TOKEN')
        if not token or token == "DEMO_TOKEN_NOT_SET":
            logger.warning("⚠️ TELEGRAM_BOT_TOKEN not configured - running in local mode")
            # Run in local mode instead of failing
            from telegram_bot import MinimalTelegramBot
            minimal_bot = MinimalTelegramBot()
            await minimal_bot.run_local_mode()
            return True
        
        # Initialize Telegram bot
        self.telegram_bot = AuracleTelegramBot(token)
        
        # Set up signal handlers
        self.setup_signal_handlers()
        
        # Start bot
        self.running = True
        logger.info("✅ AURACLE Production Bot started successfully")
        
        try:
            await self.telegram_bot.run()
        except Exception as e:
            logger.error(f"❌ Bot error: {e}")
            return False
        finally:
            await self.stop()
        
        return True
    
    async def stop(self):
        """Stop the production bot"""
        logger.info("🛑 Stopping AURACLE Production Bot...")
        
        if self.telegram_bot:
            await self.telegram_bot.stop()
        
        logger.info("✅ AURACLE Production Bot stopped")

def print_banner():
    """Print startup banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                     AURACLE TRADING BOT                     ║
    ║                    Production Version                        ║
    ╠══════════════════════════════════════════════════════════════╣
    ║ Features:                                                    ║
    ║ • Full Telegram integration with all commands               ║
    ║ • Jupiter API for real Solana trading                       ║
    ║ • Wallet generation and management                          ║
    ║ • Referral system with persistence                          ║
    ║ • Auto-sniper with honeypot protection                     ║
    ║ • Profit/loss tracking and reporting                       ║
    ║ • Continuous operation mode                                 ║
    ║                                                             ║
    ║ Commands: /start, /start_sniper, /stop_sniper, /snipe      ║
    ║          /generate_wallet, /connect_wallet, /referral      ║
    ║          /claim, /qr, /status, /help                       ║
    ║                                                             ║
    ║ Mode: {mode}                                    ║
    ║ Jupiter API: ✅ Integrated                                   ║
    ║ Honeypot Protection: ✅ Active                              ║
    ║ Referral System: ✅ Persistent                              ║
    ║ Wallet Storage: ✅ Secure                                   ║
    ╚══════════════════════════════════════════════════════════════╝
    """.format(mode=config.get_trading_mode_string())
    
    print(banner)

async def main():
    """Main entry point"""
    print_banner()
    
    # Create bot instance
    bot = AuracleProductionBot()
    
    # Start bot
    success = await bot.start()
    
    if not success:
        logger.error("❌ Failed to start bot")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
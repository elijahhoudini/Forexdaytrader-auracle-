#!/usr/bin/env python3
"""
AURACLE Main Entry Point
=======================

Start the AURACLE bot with proper error handling.
"""

import asyncio
import sys
import os
import traceback

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def main():
    """Main entry point for AURACLE bot."""
    try:
        print("🤖 Starting AURACLE Bot...")

        # Import config first to validate setup
        import config
        print(f"✅ Configuration loaded - {config.get_trading_mode_string()}")

        # Test wallet functionality
        from wallet import Wallet
        wallet = Wallet()
        print(f"✅ Wallet initialized: {wallet.address[:8] if wallet.address else 'Demo'}...")

        # Test Jupiter API
        from jupiter_api import JupiterAPI
        jupiter = JupiterAPI()
        print("✅ Jupiter API initialized")

        # Start Telegram bot if enabled
        if config.TELEGRAM_ENABLED:
            from unified_telegram_bot import AuracleTelegramBot
            bot = AuracleTelegramBot(config.TELEGRAM_BOT_TOKEN)
            print("✅ Telegram bot initialized")

            # Start the bot
            await bot.start()
            print("🚀 AURACLE Bot is running!")

            # Keep running
            try:
                await bot.idle()
            except KeyboardInterrupt:
                print("\n🛑 Shutting down AURACLE Bot...")
            finally:
                await bot.stop()
                await jupiter.close()
                await wallet.close()
        else:
            print("⚠️ Telegram not enabled - running in test mode")

            # Test basic functionality
            balance = await wallet.get_balance()
            print(f"💰 Wallet balance: {balance} SOL")

            # Test Jupiter quote
            quote = await jupiter.get_quote(
                jupiter.SOL_MINT,
                jupiter.USDC_MINT,
                1000000  # 0.001 SOL
            )

            if quote:
                print(f"📊 Jupiter quote test successful")
            else:
                print("❌ Jupiter quote test failed")

            await jupiter.close()
            await wallet.close()

    except Exception as e:
        print(f"❌ AURACLE Bot error: {e}")
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        if result:
            print("✅ AURACLE Bot completed successfully")
        else:
            print("❌ AURACLE Bot encountered errors")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 AURACLE Bot interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
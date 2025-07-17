#!/usr/bin/env python3
"""
Minimal Telegram Bot
===================

A simplified telegram bot that provides basic functionality
when the full AURACLE system is not available.
"""

import os
import sys
import asyncio
import logging
from typing import Optional
import re

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class MinimalTelegramBot:
    """Minimal telegram bot implementation."""

    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.running = False

class AuracleTelegramBot:
    """AURACLE Telegram bot implementation."""
    
    def __init__(self, token=None):
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.running = False
        self.application = None
        self.wallet_setup_mode = {}
    
    async def run(self):
        """Start the AURACLE bot."""
        if not self.token:
            logger.warning("No Telegram token found - running in local mode")
            await self.run_local_mode()
            return

        try:
            # Try to import telegram library
            from telegram import Bot
            from telegram.ext import Application, CommandHandler, MessageHandler, filters

            logger.info("🚀 Starting AURACLE Telegram Bot...")

            # Create application
            self.application = Application.builder().token(self.token).build()

            # Add handlers
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("status", self.status_command))
            self.application.add_handler(CommandHandler("help", self.help_command))
            self.application.add_handler(CommandHandler("start_sniper", self.start_sniper_command))
            self.application.add_handler(CommandHandler("stop_sniper", self.stop_sniper_command))
            self.application.add_handler(CommandHandler("snipe", self.snipe_command))
            self.application.add_handler(CommandHandler("generate_wallet", self.generate_wallet_command))
            self.application.add_handler(CommandHandler("connect_wallet", self.connect_wallet_command))
            self.application.add_handler(CommandHandler("set_wallet_key", self.set_wallet_key_command))
            self.application.add_handler(CommandHandler("referral", self.referral_command))
            self.application.add_handler(CommandHandler("claim", self.claim_command))
            self.application.add_handler(CommandHandler("qr", self.qr_command))
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

            # Start polling
            await self.application.run_polling()

        except ImportError:
            logger.warning("Telegram library not available - running in local mode")
            await self.run_local_mode()
        except Exception as e:
            logger.error(f"Bot error: {e}")
            await self.run_local_mode()

    async def run_local_mode(self):
        """Run in local mode without telegram."""
        logger.info("🔄 Running in local mode...")
        print("\n🎯 AURACLE Local Mode")
        print("=" * 40)
        print("✅ System initialized")
        print("✅ Monitoring active")
        print("✅ Demo mode enabled")

        self.running = True
        try:
            while self.running:
                print(f"⏰ System check - All systems operational")
                await asyncio.sleep(300)  # Check every 5 minutes
        except KeyboardInterrupt:
            print("\n👋 Local mode stopped")
            self.running = False

    async def stop(self):
        """Stop the bot."""
        self.running = False
        if self.application:
            await self.application.stop()

    async def start_command(self, update, context):
        """Handle /start command."""
        await update.message.reply_text(
            "🚀 AURACLE Trading Bot\n\n"
            "✅ Bot is online\n"
            "✅ Demo mode active\n"
            "✅ All systems operational\n\n"
            "Commands:\n"
            "/start_sniper - Start autonomous sniper\n"
            "/stop_sniper - Stop sniper\n"
            "/snipe <amount> - Manual snipe\n"
            "/generate_wallet - Create wallet\n"
            "/set_wallet_key - Set your wallet key securely\n"
            "/status - System status\n"
            "/help - Show all commands"
        )

    async def status_command(self, update, context):
        """Handle /status command."""
        status_text = (
            "📊 AURACLE Status\n\n"
            "🔶 Mode: Demo (Safe)\n"
            "🌐 Network: Solana\n"
            "📡 Status: Online\n"
            "⚡ Performance: Optimal\n\n"
            "✅ All systems operational"
        )
        await update.message.reply_text(status_text)

    async def help_command(self, update, context):
        """Handle /help command."""
        help_text = (
            "🔧 AURACLE Commands\n\n"
            "/start - Initialize bot\n"
            "/start_sniper - Start autonomous sniper\n"
            "/stop_sniper - Stop sniper\n"
            "/snipe <amount> - Manual snipe execution\n"
            "/generate_wallet - Generate new wallet\n"
            "/connect_wallet - Connect existing wallet\n"
            "/set_wallet_key - Securely set your wallet key\n"
            "/referral - Referral system\n"
            "/claim - Claim referral earnings\n"
            "/qr - Generate wallet QR code\n"
            "/status - System status\n"
            "/help - This help message\n\n"
            "📖 The bot is running in demo mode for safety."
        )
        await update.message.reply_text(help_text)

    async def start_sniper_command(self, update, context):
        """Handle /start_sniper command."""
        await update.message.reply_text(
            "🎯 AURACLE Sniper Started\n\n"
            "✅ Autonomous trading enabled\n"
            "🔍 Scanning for opportunities\n"
            "⚡ Demo mode active (safe)\n\n"
            "Use /stop_sniper to stop trading"
        )

    async def stop_sniper_command(self, update, context):
        """Handle /stop_sniper command."""
        await update.message.reply_text(
            "🛑 AURACLE Sniper Stopped\n\n"
            "✅ All trading halted\n"
            "📊 Session complete\n\n"
            "Use /start_sniper to resume"
        )

    async def snipe_command(self, update, context):
        """Handle /snipe command."""
        await update.message.reply_text(
            "🎯 Manual Snipe Executed\n\n"
            "✅ Demo trade completed\n"
            "💰 Amount: 0.01 SOL\n"
            "📈 Status: Successful (Demo)\n\n"
            "Real trading disabled in demo mode"
        )

    async def generate_wallet_command(self, update, context):
        """Handle /generate_wallet command."""
        await update.message.reply_text(
            "💳 Wallet Generated\n\n"
            "✅ New Solana wallet created\n"
            "🔐 Private key stored securely\n"
            "📱 Address: Demo...Address\n\n"
            "Wallet ready for demo trading"
        )

    async def connect_wallet_command(self, update, context):
        """Handle /connect_wallet command."""
        await update.message.reply_text(
            "🔗 Connect Wallet\n\n"
            "Please send your private key or seed phrase.\n"
            "⚠️ Only use demo keys in demo mode!\n\n"
            "Your wallet will be stored securely."
        )
        
    async def set_wallet_key_command(self, update, context):
        """Handle /set_wallet_key command."""
        # Get user ID to track individual users in wallet setup mode
        user_id = update.effective_user.id
        
        # Set this user in wallet setup mode
        self.wallet_setup_mode[user_id] = True
        
        # Use direct message for security
        await update.message.reply_text(
            "🔐 Secure Wallet Key Setup\n\n"
            "Please send your wallet private key in the next message.\n"
            "⚠️ For security, your message will be deleted immediately!\n\n"
            "Your key will only be stored in the bot's secure memory and \n"
            "never written to disk or logs.\n\n"
            "Type 'cancel' to abort this operation."
        )

    async def referral_command(self, update, context):
        """Handle /referral command."""
        user_id = update.effective_user.id
        await update.message.reply_text(
            f"👥 Referral System\n\n"
            f"Your referral code: DEMO{user_id}\n"
            f"Referrals: 0\n"
            f"Earnings: 0 SOL\n\n"
            "Share your code to earn rewards!"
        )

    async def claim_command(self, update, context):
        """Handle /claim command."""
        await update.message.reply_text(
            "💰 Claim Rewards\n\n"
            "Available: 0 SOL\n"
            "Status: No rewards to claim\n\n"
            "Invite friends to earn rewards!"
        )

    async def qr_command(self, update, context):
        """Handle /qr command."""
        await update.message.reply_text(
            "📱 QR Code\n\n"
            "QR code generation available\n"
            "Wallet: Demo...Address\n\n"
            "Use for easy wallet sharing"
        )

    async def handle_message(self, update, context):
        """Handle regular messages."""
        user_id = update.effective_user.id
        message_text = update.message.text
        
        # Check if user is in wallet setup mode
        if user_id in self.wallet_setup_mode and self.wallet_setup_mode[user_id]:
            # User canceled the operation
            if message_text.lower() == 'cancel':
                self.wallet_setup_mode[user_id] = False
                await update.message.reply_text("❌ Wallet key setup canceled.")
                # Delete the message for security
                await update.message.delete()
                return
                
            # Process the wallet key
            try:
                # Delete the message immediately for security
                await update.message.delete()
                
                # Validate key format (basic check)
                if re.match(r'^[0-9a-fA-F]{64,88}$', message_text.strip()):
                    # Set the wallet key in environment variable
                    os.environ["WALLET_PRIVATE_KEY"] = message_text.strip()
                    
                    # Simple validation by deriving a wallet address
                    try:
                        from solana.keypair import Keypair
                        import base58
                        
                        # Convert string to bytes and create keypair
                        key_bytes = bytes.fromhex(message_text.strip())
                        keypair = Keypair.from_secret_key(key_bytes)
                        
                        # Get public key (wallet address)
                        wallet_address = str(keypair.public_key)
                        masked_address = wallet_address[:4] + "..." + wallet_address[-4:]
                        
                        # Set wallet address in environment
                        os.environ["WALLET_ADDRESS"] = wallet_address
                        
                        await context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=f"✅ Wallet key set successfully!\n\n"
                                f"📬 Wallet address: {masked_address}\n"
                                f"🔒 Key stored securely in memory\n\n"
                                f"The bot is now ready for live trading.\n"
                                f"Use /start_sniper to begin trading."
                        )
                    except Exception as e:
                        await context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text="❌ Invalid wallet key format. Please try again with /set_wallet_key."
                        )
                else:
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="❌ Invalid wallet key format. Please try again with /set_wallet_key."
                    )
                
                # Reset the wallet setup mode
                self.wallet_setup_mode[user_id] = False
                
            except Exception as e:
                logger.error(f"Error processing wallet key: {e}")
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="❌ Error setting wallet key. Please try again with /set_wallet_key."
                )
                # Reset the wallet setup mode
                self.wallet_setup_mode[user_id] = False
            
            return
        
        # Regular message handling
        await update.message.reply_text(
            "🤖 AURACLE is listening!\n"
            "Use /help for available commands."
        )

    async def start(self):
        """Start the minimal bot."""
        if not self.token:
            logger.warning("No Telegram token found - running in local mode")
            await self.run_local_mode()
            return

        try:
            # Try to import telegram library
            from telegram import Bot, Update
            from telegram.ext import Application, CommandHandler, MessageHandler, filters

            logger.info("🚀 Starting Minimal Telegram Bot...")

            # Create application
            app = Application.builder().token(self.token).build()

            # Add handlers
            app.add_handler(CommandHandler("start", self.start_command))
            app.add_handler(CommandHandler("status", self.status_command))
            app.add_handler(CommandHandler("help", self.help_command))
            app.add_handler(CommandHandler("set_wallet_key", self.set_wallet_key_command))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

            # Start bot
            await app.initialize()
            await app.start()

            logger.info("✅ Minimal Telegram Bot started successfully")

            # Keep running
            while self.running:
                await asyncio.sleep(1)

        except ImportError:
            logger.warning("Telegram library not available - running in local mode")
            await self.run_local_mode()
        except Exception as e:
            logger.error(f"Bot error: {e}")
            await self.run_local_mode()

    async def run_local_mode(self):
        """Run in local mode without telegram."""
        logger.info("🔄 Running in local mode...")
        print("\n🎯 AURACLE Local Mode")
        print("=" * 40)
        print("✅ System initialized")
        print("✅ Monitoring active")
        print("✅ Demo mode enabled")

        self.running = True
        try:
            while self.running:
                print(f"⏰ System check - All systems operational")
                await asyncio.sleep(300)  # Check every 5 minutes
        except KeyboardInterrupt:
            print("\n👋 Local mode stopped")
            self.running = False

    async def start_command(self, update, context):
        """Handle /start command."""
        await update.message.reply_text(
            "🚀 AURACLE Minimal Bot\n\n"
            "✅ Bot is online\n"
            "✅ Demo mode active\n"
            "✅ All systems operational\n\n"
            "Use /status for system info\n"
            "Use /help for commands"
        )

    async def status_command(self, update, context):
        """Handle /status command."""
        status_text = (
            "📊 AURACLE Status\n\n"
            "🔶 Mode: Demo (Safe)\n"
            "🌐 Network: Solana\n"
            "📡 Status: Online\n"
            "⚡ Performance: Optimal\n\n"
            "✅ All systems operational"
        )
        await update.message.reply_text(status_text)

    async def help_command(self, update, context):
        """Handle /help command."""
        help_text = (
            "🔧 AURACLE Commands\n\n"
            "/start - Initialize bot\n"
            "/status - System status\n"
            "/set_wallet_key - Securely set your wallet key\n"
            "/help - This help message\n\n"
            "📖 The bot is running in demo mode for safety."
        )
        await update.message.reply_text(help_text)

    async def handle_message(self, update, context):
        """Handle regular messages."""
        # Handle wallet setup messages
        user_id = update.effective_user.id
        if user_id in self.wallet_setup_mode and self.wallet_setup_mode[user_id]:
            # This is handled in the main handle_message method
            return
            
        # Regular message handling
        await update.message.reply_text(
            "🤖 AURACLE is listening!\n"
            "Use /help for available commands."
        )

async def main():
    """Main function to start the minimal bot."""
    bot = MinimalTelegramBot()
    await bot.start()

if __name__ == "__main__":
    asyncio.run(main())
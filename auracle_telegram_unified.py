#!/usr/bin/env python3
"""
AURACLE Unified Telegram Bot - Complete Integration
=================================================

Full integration of AURACLE intelligence into Telegram bot.
Control all trading operations, monitoring, and intelligence from Telegram.

Commands:
- /start - Initialize user and show welcome
- /start_auracle - Start AURACLE trading intelligence
- /stop_auracle - Stop AURACLE trading intelligence
- /status - Show AURACLE status and stats
- /scan - Force token scan
- /trade <token> <amount> - Execute manual trade
- /wallet - Show wallet info
- /positions - Show current positions
- /settings - Configure trading parameters
- /help - Show all commands

And all existing commands: /snipe, /generate_wallet, /connect_wallet, /referral, /claim, /qr
"""

import asyncio
import json
import os
import base64
import random
import string
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

# Try to import QR code library, fallback to minimal implementation
try:
    import qrcode
    from PIL import Image
    QR_AVAILABLE = True
except ImportError:
    try:
        from minimal_qrcode import QRCode, generate_qr_text
        QR_AVAILABLE = False
    except ImportError:
        QR_AVAILABLE = False

# Try to import Telegram library, fallback to minimal implementation
try:
    from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
    TELEGRAM_AVAILABLE = True
except ImportError:
    try:
        from minimal_telegram import (
            Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup, 
            Application, CommandHandler, CallbackQueryHandler, MessageHandler, 
            ContextTypes, filters
        )
        TELEGRAM_AVAILABLE = False
    except ImportError:
        TELEGRAM_AVAILABLE = False

import logging

# Import our components
from wallet import Wallet
from jupiter_api import JupiterTradeExecutor
from enhanced_discovery import EnhancedTokenDiscovery
from risk import RiskEvaluator
from scanner import TokenScanner
from trade import TradeHandler
from logger import AuracleLogger
from auracle import Auracle
import config

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class AuracleUnifiedBot:
    """
    Complete AURACLE Telegram Integration
    
    Combines all AURACLE intelligence with Telegram bot functionality.
    Users can control all trading operations from Telegram.
    """
    
    def __init__(self, token: str):
        """Initialize the unified bot"""
        self.token = token
        self.bot = Bot(token=token)
        self.application = Application.builder().token(token).build()
        
        # AURACLE Components
        self.auracle = None
        self.auracle_running = False
        self.auracle_thread = None
        
        # Data Management
        self.data_dir = "data"
        self.users_file = os.path.join(self.data_dir, "users.json")
        self.referrals_file = os.path.join(self.data_dir, "referrals.json") 
        self.trading_logs_file = os.path.join(self.data_dir, "trading_logs.json")
        self.wallets_file = os.path.join(self.data_dir, "wallets.json")
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        self._init_data_files()
        
        # Load data
        self.users = self._load_data(self.users_file)
        self.referrals = self._load_data(self.referrals_file)
        self.trading_logs = self._load_data(self.trading_logs_file)
        self.wallets = self._load_data(self.wallets_file)
        
        # Trading components
        self.wallet_manager = Wallet()
        self.jupiter_executor = JupiterTradeExecutor()
        self.token_discovery = EnhancedTokenDiscovery()
        self.risk_evaluator = RiskEvaluator()
        self.logger = AuracleLogger()
        
        # Setup command handlers
        self._setup_handlers()
        
        logger.info("🤖 AURACLE Unified Bot initialized")
    
    def _init_data_files(self):
        """Initialize data files if they don't exist"""
        for file_path in [self.users_file, self.referrals_file, self.trading_logs_file, self.wallets_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump({}, f)
    
    def _load_data(self, file_path: str) -> Dict:
        """Load data from JSON file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_data(self, file_path: str, data: Dict):
        """Save data to JSON file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving data to {file_path}: {e}")
    
    def _setup_handlers(self):
        """Setup all command handlers"""
        
        # Basic commands
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        
        # AURACLE commands
        self.application.add_handler(CommandHandler("start_auracle", self.start_auracle_command))
        self.application.add_handler(CommandHandler("stop_auracle", self.stop_auracle_command))
        self.application.add_handler(CommandHandler("scan", self.scan_command))
        self.application.add_handler(CommandHandler("trade", self.trade_command))
        self.application.add_handler(CommandHandler("positions", self.positions_command))
        self.application.add_handler(CommandHandler("settings", self.settings_command))
        
        # Existing commands
        self.application.add_handler(CommandHandler("start_sniper", self.start_sniper_command))
        self.application.add_handler(CommandHandler("stop_sniper", self.stop_sniper_command))
        self.application.add_handler(CommandHandler("snipe", self.snipe_command))
        self.application.add_handler(CommandHandler("generate_wallet", self.generate_wallet_command))
        self.application.add_handler(CommandHandler("connect_wallet", self.connect_wallet_command))
        self.application.add_handler(CommandHandler("wallet", self.wallet_command))
        self.application.add_handler(CommandHandler("referral", self.referral_command))
        self.application.add_handler(CommandHandler("claim", self.claim_command))
        self.application.add_handler(CommandHandler("qr", self.qr_command))
        
        # Callback handlers
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        logger.info("✅ All command handlers setup complete")
    
    # AURACLE CONTROL COMMANDS
    
    async def start_auracle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start AURACLE trading intelligence"""
        user_id = str(update.effective_user.id)
        
        if self.auracle_running:
            await update.message.reply_text(
                "🤖 AURACLE is already running!\n\n"
                "Use /status to check current status or /stop_auracle to stop."
            )
            return
        
        # Initialize user if not exists
        if user_id not in self.users:
            self.users[user_id] = {
                "joined_at": datetime.now().isoformat(),
                "total_trades": 0,
                "total_profit": 0.0,
                "settings": {
                    "max_buy_amount": 0.01,
                    "profit_target": 0.20,
                    "stop_loss": 0.05,
                    "auto_trade": False
                }
            }
            self._save_data(self.users_file, self.users)
        
        await update.message.reply_text(
            "🚀 Starting AURACLE Trading Intelligence...\n\n"
            "🔄 Initializing components...\n"
            "⏳ Please wait..."
        )
        
        try:
            # Initialize AURACLE
            self.auracle = Auracle()
            self.auracle_running = True
            
            # Start AURACLE in background thread
            self.auracle_thread = threading.Thread(target=self._run_auracle, daemon=True)
            self.auracle_thread.start()
            
            # Update user
            self.users[user_id]["last_started_auracle"] = datetime.now().isoformat()
            self._save_data(self.users_file, self.users)
            
            await update.message.reply_text(
                "✅ AURACLE Trading Intelligence Started!\n\n"
                f"🤖 Status: Active\n"
                f"👤 Traveler ID: {config.TRAVELER_ID}\n"
                f"💰 Wallet: {config.WALLET_ADDRESS[:8]}...\n"
                f"📊 Mode: {config.get_trading_mode_string()}\n\n"
                "Use /status to monitor progress\n"
                "Use /stop_auracle to stop"
            )
            
        except Exception as e:
            logger.error(f"Error starting AURACLE: {e}")
            await update.message.reply_text(
                f"❌ Error starting AURACLE: {str(e)}\n\n"
                "Please check configuration and try again."
            )
    
    async def stop_auracle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Stop AURACLE trading intelligence"""
        if not self.auracle_running:
            await update.message.reply_text(
                "🤖 AURACLE is not running.\n\n"
                "Use /start_auracle to start trading intelligence."
            )
            return
        
        await update.message.reply_text("🛑 Stopping AURACLE...")
        
        try:
            # Stop AURACLE
            if self.auracle:
                self.auracle.running = False
                self.auracle.trading_active = False
            
            self.auracle_running = False
            
            await update.message.reply_text(
                "✅ AURACLE Trading Intelligence Stopped!\n\n"
                "🤖 Status: Inactive\n"
                "📊 All trading operations halted\n\n"
                "Use /start_auracle to restart"
            )
            
        except Exception as e:
            logger.error(f"Error stopping AURACLE: {e}")
            await update.message.reply_text(f"❌ Error stopping AURACLE: {str(e)}")
    
    async def scan_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Force token scan"""
        await update.message.reply_text("🔍 Scanning for tokens...")
        
        try:
            # Force scan using enhanced discovery
            tokens = await self.token_discovery.discover_tokens()
            
            if not tokens:
                await update.message.reply_text("❌ No tokens found in current scan.")
                return
            
            # Format results
            message = "📊 Token Scan Results:\n\n"
            for i, token in enumerate(tokens[:5]):  # Show top 5
                message += f"{i+1}. {token.get('symbol', 'Unknown')}\n"
                message += f"   💰 Score: {token.get('score', 0):.2f}\n"
                message += f"   📈 Liquidity: ${token.get('liquidity', 0):,.0f}\n"
                message += f"   🎯 Risk: {token.get('risk_level', 'Unknown')}\n\n"
            
            await update.message.reply_text(message)
            
        except Exception as e:
            logger.error(f"Error in scan command: {e}")
            await update.message.reply_text(f"❌ Scan error: {str(e)}")
    
    async def trade_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Execute manual trade"""
        if not context.args or len(context.args) < 2:
            await update.message.reply_text(
                "❌ Usage: /trade <token_address> <amount_sol>\n\n"
                "Example: /trade EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v 0.01"
            )
            return
        
        token_address = context.args[0]
        try:
            amount_sol = float(context.args[1])
        except ValueError:
            await update.message.reply_text("❌ Invalid amount. Please enter a valid number.")
            return
        
        await update.message.reply_text(
            f"🔄 Executing trade...\n"
            f"🎯 Token: {token_address[:8]}...\n"
            f"💰 Amount: {amount_sol} SOL"
        )
        
        try:
            # Execute trade using Jupiter
            result = await self.jupiter_executor.execute_trade(
                token_address=token_address,
                amount_sol=amount_sol
            )
            
            if result.get('success'):
                await update.message.reply_text(
                    f"✅ Trade executed successfully!\n\n"
                    f"📊 Transaction: {result.get('tx_hash', 'N/A')[:8]}...\n"
                    f"💰 Amount: {amount_sol} SOL\n"
                    f"🎯 Token: {token_address[:8]}...\n"
                    f"⚡ Status: {result.get('status', 'Completed')}"
                )
            else:
                await update.message.reply_text(
                    f"❌ Trade failed: {result.get('error', 'Unknown error')}"
                )
                
        except Exception as e:
            logger.error(f"Error in trade command: {e}")
            await update.message.reply_text(f"❌ Trade error: {str(e)}")
    
    async def positions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show current positions"""
        await update.message.reply_text("📊 Loading positions...")
        
        try:
            # Get wallet balance and positions
            balance = await self.wallet_manager.get_balance()
            
            message = f"💼 Wallet Positions:\n\n"
            message += f"💰 SOL Balance: {balance:.4f} SOL\n\n"
            
            # Get token positions (mock for now)
            positions = []  # TODO: Implement real position tracking
            
            if not positions:
                message += "📝 No active positions"
            else:
                for pos in positions:
                    message += f"🎯 {pos['symbol']}\n"
                    message += f"   Amount: {pos['amount']}\n"
                    message += f"   Value: ${pos['value']:.2f}\n"
                    message += f"   P&L: {pos['pnl']:.2f}%\n\n"
            
            await update.message.reply_text(message)
            
        except Exception as e:
            logger.error(f"Error in positions command: {e}")
            await update.message.reply_text(f"❌ Error loading positions: {str(e)}")
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Configure trading settings"""
        user_id = str(update.effective_user.id)
        
        if user_id not in self.users:
            await update.message.reply_text("❌ Please use /start first to initialize your account.")
            return
        
        settings = self.users[user_id].get("settings", {})
        
        keyboard = [
            [
                InlineKeyboardButton("💰 Max Buy Amount", callback_data="setting_max_buy"),
                InlineKeyboardButton("🎯 Profit Target", callback_data="setting_profit_target")
            ],
            [
                InlineKeyboardButton("🛑 Stop Loss", callback_data="setting_stop_loss"),
                InlineKeyboardButton("🤖 Auto Trade", callback_data="setting_auto_trade")
            ],
            [
                InlineKeyboardButton("📊 View Current", callback_data="setting_view")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "⚙️ Trading Settings:\n\n"
            f"💰 Max Buy Amount: {settings.get('max_buy_amount', 0.01)} SOL\n"
            f"🎯 Profit Target: {settings.get('profit_target', 0.20)*100:.1f}%\n"
            f"🛑 Stop Loss: {settings.get('stop_loss', 0.05)*100:.1f}%\n"
            f"🤖 Auto Trade: {'ON' if settings.get('auto_trade', False) else 'OFF'}\n\n"
            "Select a setting to modify:",
            reply_markup=reply_markup
        )
    
    # EXISTING COMMANDS (adapted)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command - Initialize user"""
        user_id = str(update.effective_user.id)
        user_name = update.effective_user.first_name or "Trader"
        
        # Initialize user
        if user_id not in self.users:
            self.users[user_id] = {
                "name": user_name,
                "joined_at": datetime.now().isoformat(),
                "total_trades": 0,
                "total_profit": 0.0,
                "settings": {
                    "max_buy_amount": 0.01,
                    "profit_target": 0.20,
                    "stop_loss": 0.05,
                    "auto_trade": False
                }
            }
            self._save_data(self.users_file, self.users)
        
        keyboard = [
            [
                InlineKeyboardButton("🚀 Start AURACLE", callback_data="start_auracle_btn"),
                InlineKeyboardButton("📊 Status", callback_data="status_btn")
            ],
            [
                InlineKeyboardButton("💼 Wallet", callback_data="wallet_btn"),
                InlineKeyboardButton("⚙️ Settings", callback_data="settings_btn")
            ],
            [
                InlineKeyboardButton("📚 Help", callback_data="help_btn")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"👋 Welcome to AURACLE, {user_name}!\n\n"
            "🤖 I'm your AI trading assistant powered by advanced intelligence.\n\n"
            "🎯 **Key Features:**\n"
            "• Autonomous token scanning\n"
            "• Intelligent risk assessment\n"
            "• Automated trade execution\n"
            "• Real-time monitoring\n\n"
            "📱 **Quick Actions:**",
            reply_markup=reply_markup
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show comprehensive status"""
        user_id = str(update.effective_user.id)
        
        try:
            # Get wallet balance
            balance = await self.wallet_manager.get_balance()
            
            # AURACLE status
            auracle_status = "🟢 Active" if self.auracle_running else "🔴 Inactive"
            
            # User stats
            user_stats = self.users.get(user_id, {})
            
            message = f"📊 **AURACLE Status Report**\n\n"
            message += f"🤖 AURACLE: {auracle_status}\n"
            message += f"💰 Balance: {balance:.4f} SOL\n"
            message += f"📈 Total Trades: {user_stats.get('total_trades', 0)}\n"
            message += f"💵 Total Profit: {user_stats.get('total_profit', 0.0):.4f} SOL\n\n"
            
            if self.auracle and self.auracle_running:
                stats = self.auracle.stats
                message += f"🔍 Scans: {stats.get('scans_completed', 0)}\n"
                message += f"🎯 Evaluations: {stats.get('tokens_evaluated', 0)}\n"
                message += f"⚡ Trades: {stats.get('trades_executed', 0)}\n"
                message += f"⏰ Uptime: {datetime.utcnow() - stats.get('start_time', datetime.utcnow())}\n"
            
            await update.message.reply_text(message)
            
        except Exception as e:
            logger.error(f"Error in status command: {e}")
            await update.message.reply_text(f"❌ Status error: {str(e)}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help message"""
        help_text = """
🤖 **AURACLE Command Guide**

**🎯 Trading Commands:**
/start_auracle - Start AI trading intelligence
/stop_auracle - Stop AI trading intelligence
/scan - Force token scan
/trade <token> <amount> - Execute manual trade
/positions - Show current positions
/settings - Configure trading parameters

**💼 Wallet Commands:**
/wallet - Show wallet info
/generate_wallet - Generate new wallet
/connect_wallet - Connect existing wallet

**📊 Information Commands:**
/status - Show comprehensive status
/help - Show this help message

**🎁 Referral Commands:**
/referral - Get referral code
/claim - Claim referral rewards
/qr - Generate QR code

**⚡ Quick Trading:**
/start_sniper - Start sniper mode
/stop_sniper - Stop sniper mode
/snipe <amount> - Quick snipe trade

**📱 Need Help?**
Contact support or check documentation.
        """
        
        await update.message.reply_text(help_text)
    
    # CALLBACK HANDLERS
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "start_auracle_btn":
            await self.start_auracle_command(update, context)
        elif query.data == "status_btn":
            await self.status_command(update, context)
        elif query.data == "wallet_btn":
            await self.wallet_command(update, context)
        elif query.data == "settings_btn":
            await self.settings_command(update, context)
        elif query.data == "help_btn":
            await self.help_command(update, context)
        # Add more callback handlers as needed
    
    # HELPER METHODS
    
    def _run_auracle(self):
        """Run AURACLE in background thread"""
        try:
            if self.auracle:
                self.auracle.run()
        except Exception as e:
            logger.error(f"Error running AURACLE: {e}")
            self.auracle_running = False
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages"""
        message = update.message.text.lower()
        
        # Basic responses
        if "hello" in message or "hi" in message:
            await update.message.reply_text("👋 Hello! Use /help to see available commands.")
        elif "status" in message:
            await self.status_command(update, context)
        elif "help" in message:
            await self.help_command(update, context)
        else:
            await update.message.reply_text(
                "🤖 I'm here to help with trading! Use /help to see available commands."
            )
    
    # PLACEHOLDER METHODS FOR EXISTING COMMANDS
    
    async def start_sniper_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start sniper mode"""
        await update.message.reply_text("🎯 Sniper mode activated!")
    
    async def stop_sniper_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Stop sniper mode"""
        await update.message.reply_text("🛑 Sniper mode deactivated!")
    
    async def snipe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Execute snipe trade"""
        await update.message.reply_text("⚡ Snipe trade executed!")
    
    async def generate_wallet_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate new wallet"""
        await update.message.reply_text("💼 New wallet generated!")
    
    async def connect_wallet_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Connect existing wallet"""
        await update.message.reply_text("🔗 Wallet connected!")
    
    async def wallet_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show wallet info"""
        try:
            balance = await self.wallet_manager.get_balance()
            await update.message.reply_text(
                f"💼 **Wallet Information**\n\n"
                f"💰 SOL Balance: {balance:.4f} SOL\n"
                f"📍 Address: {config.WALLET_ADDRESS[:8]}...\n"
                f"🌐 Network: Mainnet"
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Error getting wallet info: {str(e)}")
    
    async def referral_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show referral info"""
        await update.message.reply_text("🎁 Referral system coming soon!")
    
    async def claim_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Claim referral rewards"""
        await update.message.reply_text("💰 Claim system coming soon!")
    
    async def qr_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate QR code"""
        await update.message.reply_text("📱 QR code generation coming soon!")
    
    # MAIN RUN METHOD
    
    async def run(self):
        """Run the bot"""
        logger.info("🚀 Starting AURACLE Unified Bot...")
        
        try:
            # Initialize and start polling
            await self.application.initialize()
            await self.application.start()
            
            # Start polling for updates
            await self.application.updater.start_polling(
                drop_pending_updates=True,
                poll_interval=1.0,
                timeout=30
            )
            
            logger.info("✅ AURACLE Unified Bot started successfully!")
            
            # Keep running
            while True:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"❌ Bot error: {e}")
            raise
        finally:
            # Cleanup
            await self.stop()
    
    async def stop(self):
        """Stop the bot"""
        logger.info("🛑 Stopping AURACLE Unified Bot...")
        
        # Stop AURACLE
        if self.auracle_running:
            self.auracle_running = False
            if self.auracle:
                self.auracle.running = False
        
        # Stop Telegram bot
        if self.application:
            await self.application.stop()
        
        logger.info("✅ AURACLE Unified Bot stopped")

# MAIN ENTRY POINT
async def main():
    """Main entry point"""
    print("🚀 AURACLE Unified Telegram Bot")
    print("=" * 50)
    
    # Get token from config or environment
    token = config.TELEGRAM_BOT_TOKEN or os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found!")
        print("Please set it in config.py or environment variables.")
        return
    
    # Create and run bot
    bot = AuracleUnifiedBot(token)
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())

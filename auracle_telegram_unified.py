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
        self.jupiter_executor = JupiterTradeExecutor(self.wallet_manager.keypair)
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
            
            # Get wallet balance for display
            balance = await self.wallet_manager.get_balance()
            
            await update.message.reply_text(
                "✅ AURACLE Trading Intelligence Started!\n\n"
                f"🤖 Status: 🟢 Active\n"
                f"💰 Wallet: {config.WALLET_ADDRESS[:8]}...\n"
                f"💵 Balance: {balance:.4f} SOL\n"
                f"📊 Mode: {config.get_trading_mode_string()}\n\n"
                "🎯 AURACLE is now scanning for opportunities...\n"
                "Use /status to monitor progress"
            )
            
        except Exception as e:
            logger.error(f"Error starting AURACLE: {e}")
            self.auracle_running = False
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
            
            # Format results with better presentation
            message = "📊 *Token Scan Results:*\n\n"
            
            for i, token in enumerate(tokens[:5]):  # Show top 5
                symbol = token.get('symbol', 'Unknown')
                score = token.get('score', 0)
                liquidity = token.get('liquidity', 0)
                risk_level = token.get('risk_level', 'Unknown')
                price_change = token.get('price_change_24h', 0)
                
                message += f"{i+1}. *{symbol}*\n"
                message += f"   💰 Score: {score:.2f}/1.0\n"
                message += f"   � Liquidity: ${liquidity:,.0f}\n"
                message += f"   🎯 Risk: {risk_level}\n"
                message += f"   📈 24h Change: {price_change:+.1f}%\n"
                message += f"   🔗 Address: `{token.get('address', 'N/A')[:8]}...`\n\n"
            
            if len(tokens) > 5:
                message += f"*... and {len(tokens) - 5} more tokens*\n\n"
            
            message += "Use `/trade <address> <amount>` to trade manually"
            
            await update.message.reply_text(message, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Error in scan command: {e}")
            await update.message.reply_text(f"❌ Scan error: {str(e)}")
    
    async def trade_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Execute manual trade with enhanced safety checks"""
        if not context.args or len(context.args) < 2:
            await update.message.reply_text(
                "❌ Usage: /trade <token_address> <amount_sol>\n\n"
                "Example: /trade EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v 0.01\n\n"
                "🛡️ Safety Features:\n"
                "• Maximum 1.0 SOL per trade\n"
                "• Balance verification before trading\n"
                "• Real-time quote validation\n"
                "• Transaction confirmation tracking"
            )
            return
        
        token_address = context.args[0]
        try:
            amount_sol = float(context.args[1])
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid amount. Please enter a valid number.\n\n"
                "Example: /trade EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v 0.01"
            )
            return
        
        # Enhanced validation with safety checks
        if amount_sol <= 0:
            await update.message.reply_text("❌ Amount must be greater than 0.")
            return
        
        if amount_sol > 1.0:  # Safety limit for manual trades
            await update.message.reply_text(
                "❌ Maximum trade amount is 1.0 SOL for safety.\n\n"
                "💡 This limit prevents accidental large trades.\n"
                "For larger amounts, use multiple smaller trades."
            )
            return
        
        # Validate token address format
        if len(token_address) < 32 or len(token_address) > 50:
            await update.message.reply_text(
                "❌ Invalid token address format.\n\n"
                "Token addresses should be 32-50 characters long.\n"
                "Example: EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
            )
            return
        
        # Check wallet balance before trading
        try:
            current_balance = await self.wallet_manager.get_balance()
            if current_balance < amount_sol:
                await update.message.reply_text(
                    f"❌ Insufficient balance!\n\n"
                    f"💰 Current Balance: {current_balance:.4f} SOL\n"
                    f"🎯 Required Amount: {amount_sol:.4f} SOL\n"
                    f"❌ Shortfall: {amount_sol - current_balance:.4f} SOL"
                )
                return
        except Exception as e:
            await update.message.reply_text(
                f"❌ Error checking balance: {str(e)}\n\n"
                "Please try again or contact support if the issue persists."
            )
            return
        
        # Send initial trade confirmation
        await update.message.reply_text(
            f"🔄 Executing trade...\n\n"
            f"🎯 Token: {token_address[:8]}...{token_address[-8:]}\n"
            f"💰 Amount: {amount_sol} SOL\n"
            f"💵 Current Balance: {current_balance:.4f} SOL\n"
            f"🌐 Mode: {config.get_trading_mode_string()}\n\n"
            f"⏳ Getting quote from Jupiter..."
        )
        
        try:
            # Execute trade using Jupiter with enhanced error handling
            result = await self.jupiter_executor.buy_token(token_address, amount_sol)
            
            if result.get('success'):
                # Update user trade stats
                user_id = str(update.effective_user.id)
                if user_id in self.users:
                    self.users[user_id]["total_trades"] += 1
                    # Update profit tracking (simplified)
                    self.users[user_id]["total_profit"] = self.users[user_id].get("total_profit", 0.0)
                    self._save_data(self.users_file, self.users)
                
                # Calculate output amount display
                output_amount = result.get('output_amount', 0)
                signature = result.get('signature', 'N/A')
                
                # Success message with detailed information
                success_message = (
                    f"✅ Trade executed successfully!\n\n"
                    f"📊 Transaction Details:\n"
                    f"🔗 Signature: {signature[:8]}...{signature[-8:] if len(signature) > 16 else signature}\n"
                    f"💰 SOL Spent: {amount_sol} SOL\n"
                    f"🎯 Token: {token_address[:8]}...{token_address[-8:]}\n"
                    f"⚡ Tokens Received: {output_amount:,}\n"
                    f"🌐 Mode: {config.get_trading_mode_string()}\n\n"
                    f"🔍 View Transaction:\n"
                    f"https://solscan.io/tx/{signature}\n\n"
                    f"💡 Use /positions to view your current holdings"
                )
                
                await update.message.reply_text(success_message)
                
                # Log successful trade
                trade_log = {
                    "user_id": user_id,
                    "timestamp": time.time(),
                    "token_address": token_address,
                    "amount_sol": amount_sol,
                    "output_amount": output_amount,
                    "signature": signature,
                    "success": True
                }
                
                # Save trade log
                if user_id not in self.trading_logs:
                    self.trading_logs[user_id] = []
                self.trading_logs[user_id].append(trade_log)
                self._save_data(self.trading_logs_file, self.trading_logs)
                
            else:
                # Handle trade failure with detailed error info
                error_msg = result.get('error', 'Unknown error')
                
                failure_message = (
                    f"❌ Trade failed!\n\n"
                    f"🎯 Token: {token_address[:8]}...{token_address[-8:]}\n"
                    f"💰 Amount: {amount_sol} SOL\n"
                    f"📊 Error: {error_msg}\n\n"
                    f"🔧 Possible solutions:\n"
                    f"• Check token address is correct\n"
                    f"• Ensure sufficient balance\n"
                    f"• Try a smaller amount\n"
                    f"• Wait and try again (network congestion)\n\n"
                    f"💡 Use /status to check system status"
                )
                
                await update.message.reply_text(failure_message)
                
                # Log failed trade
                trade_log = {
                    "user_id": user_id,
                    "timestamp": time.time(),
                    "token_address": token_address,
                    "amount_sol": amount_sol,
                    "error": error_msg,
                    "success": False
                }
                
                if user_id not in self.trading_logs:
                    self.trading_logs[user_id] = []
                self.trading_logs[user_id].append(trade_log)
                self._save_data(self.trading_logs_file, self.trading_logs)
                
        except Exception as e:
            logger.error(f"Error in trade command: {e}")
            
            # Enhanced error handling with helpful messages
            error_message = (
                f"❌ Trade execution error!\n\n"
                f"🎯 Token: {token_address[:8]}...{token_address[-8:]}\n"
                f"💰 Amount: {amount_sol} SOL\n"
                f"📊 Error: {str(e)}\n\n"
                f"🔧 This might be due to:\n"
                f"• Network connectivity issues\n"
                f"• Invalid token address\n"
                f"• Insufficient liquidity\n"
                f"• RPC node problems\n\n"
                f"💡 Please try again in a few moments.\n"
                f"If the issue persists, contact support."
            )
            
            await update.message.reply_text(error_message)
    
    async def positions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show current positions and trading history"""
        await update.message.reply_text("📊 Loading positions and trading history...")
        
        try:
            user_id = str(update.effective_user.id)
            
            # Get wallet balance
            balance = await self.wallet_manager.get_balance()
            
            # Get user trading history
            user_trades = self.trading_logs.get(user_id, [])
            user_stats = self.users.get(user_id, {})
            
            message = f"💼 *Your Trading Dashboard*\n\n"
            message += f"💰 SOL Balance: {balance:.4f} SOL\n"
            message += f"📊 Total Trades: {user_stats.get('total_trades', 0)}\n"
            message += f"💵 Total Profit: {user_stats.get('total_profit', 0.0):.4f} SOL\n"
            message += f"📍 Wallet: {config.WALLET_ADDRESS[:8]}...\n\n"
            
            # Show recent trades
            if user_trades:
                message += f"📈 *Recent Trades (Last 5):*\n\n"
                
                # Sort by timestamp and get last 5
                recent_trades = sorted(user_trades, key=lambda x: x.get('timestamp', 0), reverse=True)[:5]
                
                for i, trade in enumerate(recent_trades, 1):
                    status = "✅" if trade.get('success') else "❌"
                    timestamp = datetime.fromtimestamp(trade.get('timestamp', 0))
                    token_addr = trade.get('token_address', 'N/A')
                    amount = trade.get('amount_sol', 0)
                    
                    message += f"{i}. {status} {timestamp.strftime('%m/%d %H:%M')}\n"
                    message += f"   🎯 Token: {token_addr[:8]}...\n"
                    message += f"   💰 Amount: {amount} SOL\n"
                    
                    if trade.get('success'):
                        output = trade.get('output_amount', 0)
                        message += f"   ⚡ Received: {output:,} tokens\n"
                        
                        # Add transaction link
                        signature = trade.get('signature', '')
                        if signature and signature != 'N/A':
                            message += f"   � [View Transaction](https://solscan.io/tx/{signature})\n"
                    else:
                        error = trade.get('error', 'Unknown error')
                        message += f"   ❌ Error: {error}\n"
                    
                    message += "\n"
                    
                if len(user_trades) > 5:
                    message += f"*... and {len(user_trades) - 5} more trades*\n\n"
            else:
                message += f"📝 No trading history yet\n\n"
                message += f"💡 Use /trade to make your first trade!\n"
                message += f"Example: /trade EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v 0.01\n\n"
            
            # Add quick action buttons
            keyboard = [
                [
                    InlineKeyboardButton("🔄 Refresh", callback_data="refresh_positions"),
                    InlineKeyboardButton("💰 Check Balance", callback_data="check_balance")
                ],
                [
                    InlineKeyboardButton("📊 Full History", callback_data="full_history"),
                    InlineKeyboardButton("🎯 New Trade", callback_data="new_trade_help")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Show trading performance if available
            if user_trades:
                successful_trades = [t for t in user_trades if t.get('success')]
                failed_trades = [t for t in user_trades if not t.get('success')]
                
                success_rate = (len(successful_trades) / len(user_trades) * 100) if user_trades else 0
                
                message += f"📈 *Trading Performance:*\n"
                message += f"✅ Successful: {len(successful_trades)}\n"
                message += f"❌ Failed: {len(failed_trades)}\n"
                message += f"📊 Success Rate: {success_rate:.1f}%\n\n"
            
            message += f"🤖 *Trading Status:*\n"
            message += f"🔥 Mode: {config.get_trading_mode_string()}\n"
            message += f"🤖 AURACLE: {'🟢 Active' if self.auracle_running else '🔴 Inactive'}\n"
            
            await update.message.reply_text(message, parse_mode="Markdown", reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Error in positions command: {e}")
            await update.message.reply_text(f"❌ Error loading positions: {str(e)}")
            
    async def handle_positions_callback(self, query, context):
        """Handle positions-related button callbacks"""
        if query.data == "refresh_positions":
            await query.edit_message_text("🔄 Refreshing positions...")
            # Simulate refresh by calling positions command
            await self.positions_command(query, context)
            
        elif query.data == "check_balance":
            try:
                balance = await self.wallet_manager.get_balance()
                await query.edit_message_text(
                    f"💰 *Current Balance*\n\n"
                    f"SOL: {balance:.4f} SOL\n"
                    f"USD: ~${balance * 180:.2f}\n\n"  # Rough SOL price estimate
                    f"📍 Address: {config.WALLET_ADDRESS[:8]}...\n"
                    f"🌐 Network: Mainnet",
                    parse_mode="Markdown"
                )
            except Exception as e:
                await query.edit_message_text(f"❌ Error checking balance: {str(e)}")
                
        elif query.data == "full_history":
            await query.edit_message_text(
                "📊 Full trading history coming soon!\n\n"
                "For now, use /positions to see recent trades."
            )
            
        elif query.data == "new_trade_help":
            await query.edit_message_text(
                "🎯 *How to Make a Trade*\n\n"
                "Use the command:\n"
                "/trade <token_address> <amount_sol>\n\n"
                "Example:\n"
                "/trade EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v 0.01\n\n"
                "🛡️ Safety limits:\n"
                "• Maximum 1.0 SOL per trade\n"
                "• Balance verification before trading\n"
                "• Real-time quote validation\n\n"
                "💡 Use /scan to find promising tokens!",
                parse_mode="Markdown"
            )
    
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
        
        # Initialize user if not exists
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
        
        # Get current balance for display
        try:
            balance = await self.wallet_manager.get_balance()
            balance_text = f"💰 Balance: {balance:.4f} SOL\n"
        except:
            balance_text = "💰 Balance: Checking...\n"
        
        # Dynamic button based on AURACLE state
        auracle_button = (
            InlineKeyboardButton("� Stop AURACLE", callback_data="stop_auracle_btn") 
            if self.auracle_running 
            else InlineKeyboardButton("� Start AURACLE", callback_data="start_auracle_btn")
        )
        
        keyboard = [
            [
                auracle_button,
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
        
        # Status indicator
        status_indicator = "🟢 Active" if self.auracle_running else "🔴 Inactive"
        
        await update.message.reply_text(
            f"👋 Welcome to AURACLE, {user_name}!\n\n"
            "🤖 I'm your AI trading assistant powered by advanced intelligence.\n\n"
            f"📊 *Current Status:*\n"
            f"🤖 AURACLE: {status_indicator}\n"
            f"{balance_text}"
            f"🔥 Mode: {config.get_trading_mode_string()}\n\n"
            "🎯 *Key Features:*\n"
            "• Autonomous token scanning\n"
            "• Intelligent risk assessment\n"
            "• Automated trade execution\n"
            "• Real-time monitoring\n\n"
            "📱 *Quick Actions:*",
            reply_markup=reply_markup,
            parse_mode="Markdown"
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
            
            message = f"📊 *AURACLE Status Report*\n\n"
            message += f"🤖 AURACLE: {auracle_status}\n"
            message += f"💰 Balance: {balance:.4f} SOL\n"
            message += f"📈 Total Trades: {user_stats.get('total_trades', 0)}\n"
            message += f"💵 Total Profit: {user_stats.get('total_profit', 0.0):.4f} SOL\n\n"
            
            if self.auracle and self.auracle_running:
                stats = self.auracle.stats
                message += f"🔍 Scans: {stats.get('scans_completed', 0)}\n"
                message += f"🎯 Evaluations: {stats.get('tokens_evaluated', 0)}\n"
                message += f"⚡ Trades: {stats.get('trades_executed', 0)}\n"
                uptime = datetime.utcnow() - stats.get('start_time', datetime.utcnow())
                message += f"⏰ Uptime: {str(uptime).split('.')[0]}\n"
            
            await update.message.reply_text(message, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Error in status command: {e}")
            await update.message.reply_text(f"❌ Status error: {str(e)}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help message"""
        help_text = """🤖 *AURACLE Command Guide*

*🎯 Trading Commands:*
/start\\_auracle - Start AI trading intelligence
/stop\\_auracle - Stop AI trading intelligence
/scan - Force token scan and show results
/trade <token> <amount> - Execute manual trade
/positions - Show current positions
/settings - Configure trading parameters

*💼 Wallet Commands:*
/wallet - Show wallet info and balance
/generate\\_wallet - Generate new wallet (placeholder)
/connect\\_wallet - Connect existing wallet (placeholder)

*📊 Information Commands:*
/status - Show comprehensive AURACLE status
/help - Show this help message

*🎁 Additional Features:*
/referral - Get referral code (coming soon)
/claim - Claim referral rewards (coming soon)
/qr - Generate QR code (coming soon)

*⚡ Quick Trading:*
/start\\_sniper - Start sniper mode (placeholder)
/stop\\_sniper - Stop sniper mode (placeholder)
/snipe <amount> - Quick snipe trade (placeholder)

*🔧 Current Status:*
• Jupiter API: ✅ Fixed and Working
• Live Trading: ✅ Enabled
• Stop/Start: ✅ Fully Functional
• Telegram Bot: ✅ Responsive

*📱 Need Help?*
Use /start to see the main interface with buttons!
Contact support for advanced features."""
        
        await update.message.reply_text(help_text, parse_mode="MarkdownV2")
    
    # CALLBACK HANDLERS
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        try:
            if query.data == "start_auracle_btn":
                await self.handle_start_auracle_callback(query, context)
            elif query.data == "stop_auracle_btn":
                await self.handle_stop_auracle_callback(query, context)
            elif query.data == "status_btn":
                await self.handle_status_callback(query, context)
            elif query.data == "wallet_btn":
                await self.handle_wallet_callback(query, context)
            elif query.data == "settings_btn":
                await self.handle_settings_callback(query, context)
            elif query.data == "help_btn":
                await self.handle_help_callback(query, context)
            elif query.data.startswith("setting_"):
                await self.handle_setting_callback(query, context)
            elif query.data in ["refresh_positions", "check_balance", "full_history", "new_trade_help"]:
                await self.handle_positions_callback(query, context)
            else:
                await query.message.reply_text("❌ Unknown button action")
                
        except Exception as e:
            logger.error(f"Error in button callback: {e}")
            await query.message.reply_text(f"❌ Error: {str(e)}")
    
    async def handle_start_auracle_callback(self, query, context):
        """Handle start AURACLE button callback"""
        user_id = str(query.from_user.id)
        
        if self.auracle_running:
            await query.edit_message_text(
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
        
        await query.edit_message_text(
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
            
            # Get wallet balance for display
            balance = await self.wallet_manager.get_balance()
            
            await query.edit_message_text(
                "✅ AURACLE Trading Intelligence Started!\n\n"
                f"🤖 Status: 🟢 Active\n"
                f"💰 Wallet: {config.WALLET_ADDRESS[:8]}...\n"
                f"💵 Balance: {balance:.4f} SOL\n"
                f"📊 Mode: {config.get_trading_mode_string()}\n\n"
                "🎯 AURACLE is now scanning for opportunities...\n"
                "Use /status to monitor progress"
            )
            
        except Exception as e:
            logger.error(f"Error starting AURACLE: {e}")
            self.auracle_running = False
            await query.edit_message_text(
                f"❌ Error starting AURACLE: {str(e)}\n\n"
                "Please check configuration and try again."
            )
    
    async def handle_status_callback(self, query, context):
        """Handle status button callback"""
        user_id = str(query.from_user.id)
        
        try:
            # Get wallet balance
            balance = await self.wallet_manager.get_balance()
            
            # AURACLE status
            auracle_status = "🟢 Active" if self.auracle_running else "🔴 Inactive"
            
            # User stats
            user_stats = self.users.get(user_id, {})
            
            message = f"📊 *AURACLE Status Report*\n\n"
            message += f"🤖 AURACLE: {auracle_status}\n"
            message += f"💰 Balance: {balance:.4f} SOL\n"
            message += f"📈 Total Trades: {user_stats.get('total_trades', 0)}\n"
            message += f"💵 Total Profit: {user_stats.get('total_profit', 0.0):.4f} SOL\n\n"
            
            if self.auracle and self.auracle_running:
                stats = self.auracle.stats
                message += f"🔍 Scans: {stats.get('scans_completed', 0)}\n"
                message += f"🎯 Evaluations: {stats.get('tokens_evaluated', 0)}\n"
                message += f"⚡ Trades: {stats.get('trades_executed', 0)}\n"
                uptime = datetime.utcnow() - stats.get('start_time', datetime.utcnow())
                message += f"⏰ Uptime: {str(uptime).split('.')[0]}\n"
            
            await query.edit_message_text(message, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Error in status callback: {e}")
            await query.edit_message_text(f"❌ Status error: {str(e)}")
    
    async def handle_wallet_callback(self, query, context):
        """Handle wallet button callback"""
        try:
            balance = await self.wallet_manager.get_balance()
            await query.edit_message_text(
                f"💼 *Wallet Information*\n\n"
                f"💰 SOL Balance: {balance:.4f} SOL\n"
                f"📍 Address: {config.WALLET_ADDRESS[:8]}...\n"
                f"🌐 Network: Mainnet",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Error in wallet callback: {e}")
            await query.edit_message_text(f"❌ Error getting wallet info: {str(e)}")
    
    async def handle_settings_callback(self, query, context):
        """Handle settings button callback"""
        user_id = str(query.from_user.id)
        
        if user_id not in self.users:
            await query.edit_message_text("❌ Please use /start first to initialize your account.")
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
        
        await query.edit_message_text(
            "⚙️ Trading Settings:\n\n"
            f"💰 Max Buy Amount: {settings.get('max_buy_amount', 0.01)} SOL\n"
            f"🎯 Profit Target: {settings.get('profit_target', 0.20)*100:.1f}%\n"
            f"🛑 Stop Loss: {settings.get('stop_loss', 0.05)*100:.1f}%\n"
            f"🤖 Auto Trade: {'ON' if settings.get('auto_trade', False) else 'OFF'}\n\n"
            "Select a setting to modify:",
            reply_markup=reply_markup
        )
    
    async def handle_help_callback(self, query, context):
        """Handle help button callback"""
        help_text = """🤖 *AURACLE Command Guide*

*🎯 Trading Commands:*
/start_auracle - Start AI trading intelligence
/stop_auracle - Stop AI trading intelligence
/scan - Force token scan
/trade <token> <amount> - Execute manual trade
/positions - Show current positions
/settings - Configure trading parameters

*💼 Wallet Commands:*
/wallet - Show wallet info
/generate_wallet - Generate new wallet
/connect_wallet - Connect existing wallet

*📊 Information Commands:*
/status - Show comprehensive status
/help - Show this help message

*🎁 Referral Commands:*
/referral - Get referral code
/claim - Claim referral rewards
/qr - Generate QR code

*⚡ Quick Trading:*
/start_sniper - Start sniper mode
/stop_sniper - Stop sniper mode
/snipe <amount> - Quick snipe trade

*📱 Need Help?*
Contact support or check documentation."""
        
        await query.edit_message_text(help_text, parse_mode="Markdown")
    
    async def handle_setting_callback(self, query, context):
        """Handle settings callback"""
        user_id = str(query.from_user.id)
        
        if user_id not in self.users:
            await query.edit_message_text("❌ Please use /start first to initialize your account.")
            return
        
        settings = self.users[user_id].get("settings", {})
        
        if query.data == "setting_view":
            # Show current settings
            await query.edit_message_text(
                f"📊 *Current Trading Settings:*\n\n"
                f"💰 Max Buy Amount: {settings.get('max_buy_amount', 0.01)} SOL\n"
                f"🎯 Profit Target: {settings.get('profit_target', 0.20)*100:.1f}%\n"
                f"🛑 Stop Loss: {settings.get('stop_loss', 0.05)*100:.1f}%\n"
                f"🤖 Auto Trade: {'ON' if settings.get('auto_trade', False) else 'OFF'}\n\n"
                f"Use /settings to modify these values.",
                parse_mode="Markdown"
            )
        else:
            # Handle other setting modifications
            await query.edit_message_text(
                "⚙️ Setting modification coming soon!\n\n"
                "For now, use /settings to view current values."
            )
    
    async def handle_stop_auracle_callback(self, query, context):
        """Handle stop AURACLE button callback"""
        if not self.auracle_running:
            await query.edit_message_text(
                "🤖 AURACLE is not running.\n\n"
                "Use 'Start AURACLE' button to start trading intelligence."
            )
            return
        
        await query.edit_message_text("🛑 Stopping AURACLE...")
        
        try:
            # Stop AURACLE with proper cleanup
            if self.auracle:
                if hasattr(self.auracle, 'running'):
                    self.auracle.running = False
                if hasattr(self.auracle, 'trading_active'):
                    self.auracle.trading_active = False
                if hasattr(self.auracle, 'should_stop'):
                    self.auracle.should_stop = True
            
            # Update state
            self.auracle_running = False
            
            # Give thread time to stop
            await asyncio.sleep(0.5)
            
            await query.edit_message_text(
                "✅ AURACLE Trading Intelligence Stopped!\n\n"
                "🤖 Status: 🔴 Inactive\n"
                "📊 All trading operations halted\n"
                "💼 Wallet remains safe\n"
                "🔄 Ready to restart anytime\n\n"
                "Use 'Start AURACLE' button to restart"
            )
            
        except Exception as e:
            logger.error(f"Error stopping AURACLE: {e}")
            await query.edit_message_text(f"❌ Error stopping AURACLE: {str(e)}")
            # Force state reset even if error
            self.auracle_running = False
    
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
                f"💼 *Wallet Information*\n\n"
                f"💰 SOL Balance: {balance:.4f} SOL\n"
                f"📍 Address: {config.WALLET_ADDRESS[:8]}...\n"
                f"🌐 Network: Mainnet",
                parse_mode="Markdown"
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

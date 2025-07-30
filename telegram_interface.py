#!/usr/bin/env python3
"""
AURACLE Telegram Interface - Enhanced Command System
==================================================

Advanced Telegram bot interface for live trading interventions,
status monitoring, and emergency controls.

Features:
- Live pause/resume commands
- Force-sell functionality
- Real-time status updates
- Error log streaming
- Performance monitoring
- Emergency stop controls
"""

import asyncio
import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import asdict

# Try to import telegram libraries
try:
    from telegram import Bot, Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False

import config


class TelegramInterface:
    """Enhanced Telegram interface for autonomous AI trader control."""
    
    def __init__(self, trader_instance):
        """Initialize Telegram interface with trader reference."""
        self.trader = trader_instance
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.admin_chat_id = os.getenv('TELEGRAM_ADMIN_CHAT_ID', self.chat_id)
        
        self.application = None
        self.bot = None
        self.running = False
        
        # Setup logging
        self.logger = logging.getLogger('TelegramInterface')
        
        # Command permissions
        self.authorized_users = set()
        admin_users = os.getenv('TELEGRAM_ADMIN_USERS', '').split(',')
        self.authorized_users.update(user.strip() for user in admin_users if user.strip())
        
        self.logger.info("📱 Telegram interface initialized")
    
    async def start(self):
        """Start the enhanced Telegram bot interface."""
        if not TELEGRAM_AVAILABLE:
            self.logger.warning("📱 Telegram library not available - interface disabled")
            return
        
        if not self.bot_token:
            self.logger.warning("📱 No Telegram bot token - interface disabled")
            return
        
        try:
            self.logger.info("🚀 Starting enhanced Telegram interface...")
            
            # Create application
            self.application = Application.builder().token(self.bot_token).build()
            self.bot = self.application.bot
            
            # Add command handlers
            self.setup_command_handlers()
            
            # Start the bot
            self.running = True
            await self.application.run_polling()
            
        except Exception as e:
            self.logger.error(f"❌ Telegram interface startup error: {e}")
    
    def setup_command_handlers(self):
        """Setup all Telegram command handlers."""
        # Basic commands
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        
        # Trading control commands
        self.application.add_handler(CommandHandler("pause", self.pause_command))
        self.application.add_handler(CommandHandler("resume", self.resume_command))
        self.application.add_handler(CommandHandler("stop", self.emergency_stop_command))
        self.application.add_handler(CommandHandler("force_sell", self.force_sell_command))
        
        # Information commands
        self.application.add_handler(CommandHandler("positions", self.positions_command))
        self.application.add_handler(CommandHandler("performance", self.performance_command))
        self.application.add_handler(CommandHandler("logs", self.logs_command))
        self.application.add_handler(CommandHandler("journal", self.journal_command))
        
        # Configuration commands
        self.application.add_handler(CommandHandler("blacklist", self.blacklist_command))
        self.application.add_handler(CommandHandler("settings", self.settings_command))
        
        # Authorization
        self.application.add_handler(CommandHandler("auth", self.auth_command))
        
        # Message handler for general updates
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        self.logger.info("✅ Telegram command handlers setup complete")
    
    def is_authorized(self, update: Update) -> bool:
        """Check if user is authorized to use bot commands."""
        user_id = str(update.effective_user.id)
        username = update.effective_user.username
        
        # Check if user is in authorized list
        if user_id in self.authorized_users or username in self.authorized_users:
            return True
        
        # For admin chat, allow all users
        if self.admin_chat_id and str(update.effective_chat.id) == self.admin_chat_id:
            return True
        
        return False
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        if not self.is_authorized(update):
            await update.message.reply_text("❌ Unauthorized access")
            return
        
        welcome_message = """
🚀 **AURACLE Autonomous AI Trading Bot**
Enhanced Telegram Control Interface

**Available Commands:**
🎮 `/pause` - Pause trading
🎮 `/resume` - Resume trading
🛑 `/stop` - Emergency stop
💰 `/force_sell <token>` - Force sell position

📊 `/status` - Current status
📈 `/positions` - Open positions
📊 `/performance` - Performance stats
📋 `/logs` - Recent error logs
📖 `/journal` - Trade journal

⚙️ `/settings` - Bot settings
🚫 `/blacklist` - Token blacklist
🔐 `/auth <password>` - Authorize access

Type `/help` for detailed command information.
"""
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        if not self.is_authorized(update):
            await update.message.reply_text("❌ Unauthorized access")
            return
        
        help_text = """
**🎮 Trading Controls:**
• `/pause` - Pause all trading activities
• `/resume` - Resume trading operations
• `/stop` - Emergency stop (cancels pending trades)
• `/force_sell <token_symbol>` - Force sell specific token

**📊 Information:**
• `/status` - Bot status and current activity
• `/positions` - List all open positions
• `/performance` - Performance metrics and stats
• `/logs [count]` - Show recent error logs (default: 10)
• `/journal [date]` - Show trade journal (YYYY-MM-DD)

**⚙️ Configuration:**
• `/settings` - Display current bot settings
• `/blacklist [add/remove] [token]` - Manage token blacklist
• `/auth <password>` - Authorize your account

**🚨 Emergency:**
• Emergency stop: Send "STOP" in all caps
• Force sell all: Send "SELL ALL" in all caps

All commands require authorization. Contact admin for access.
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        if not self.is_authorized(update):
            await update.message.reply_text("❌ Unauthorized access")
            return
        
        try:
            # Get current status from trader
            status_info = {
                'running': self.trader.running,
                'paused': self.trader.paused,
                'live_mode': self.trader.live_mode,
                'pending_trades': len(self.trader.pending_trades),
                'blacklisted_tokens': len(self.trader.blacklisted_tokens),
                'websocket_connected': self.trader.websocket_client is not None,
                'session_stats': self.trader.session_stats
            }
            
            # Get wallet balance
            wallet_balance = await self.trader.get_wallet_balance()
            
            status_text = f"""
**🤖 AURACLE Status Report**

**🔄 System Status:**
• Running: {'✅' if status_info['running'] else '❌'}
• Paused: {'⏸️' if status_info['paused'] else '▶️'}
• Mode: {'🔴 LIVE' if status_info['live_mode'] else '🟡 DEMO'}
• WebSocket: {'🟢 Connected' if status_info['websocket_connected'] else '🔴 Disconnected'}

**💰 Wallet:**
• Balance: {wallet_balance:.4f} SOL

**📊 Trading:**
• Pending Trades: {status_info['pending_trades']}
• Blacklisted Tokens: {status_info['blacklisted_tokens']}

**📈 Session Stats:**
• Total Trades: {status_info['session_stats']['trades_executed']}
• Successful: {status_info['session_stats']['successful_trades']}
• Failed: {status_info['session_stats']['failed_trades']}
• Avg Execution: {status_info['session_stats']['average_execution_time']:.0f}ms

*Last updated: {datetime.utcnow().strftime('%H:%M:%S UTC')}*
"""
            await update.message.reply_text(status_text, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error getting status: {e}")
    
    async def pause_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pause command."""
        if not self.is_authorized(update):
            await update.message.reply_text("❌ Unauthorized access")
            return
        
        try:
            self.trader.paused = True
            await update.message.reply_text("⏸️ Trading paused successfully")
            self.logger.info(f"📱 Trading paused by {update.effective_user.username}")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error pausing: {e}")
    
    async def resume_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /resume command."""
        if not self.is_authorized(update):
            await update.message.reply_text("❌ Unauthorized access")
            return
        
        try:
            self.trader.paused = False
            await update.message.reply_text("▶️ Trading resumed successfully")
            self.logger.info(f"📱 Trading resumed by {update.effective_user.username}")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error resuming: {e}")
    
    async def emergency_stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stop command."""
        if not self.is_authorized(update):
            await update.message.reply_text("❌ Unauthorized access")
            return
        
        try:
            await self.trader.emergency_stop()
            await update.message.reply_text("🛑 EMERGENCY STOP ACTIVATED")
            self.logger.warning(f"📱 Emergency stop triggered by {update.effective_user.username}")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error stopping: {e}")
    
    async def force_sell_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /force_sell command."""
        if not self.is_authorized(update):
            await update.message.reply_text("❌ Unauthorized access")
            return
        
        try:
            if not context.args:
                await update.message.reply_text("❌ Usage: /force_sell <token_symbol>")
                return
            
            token_symbol = context.args[0].upper()
            
            # Find token in open positions
            position_found = False
            for mint, position in self.trader.auracle.trade_handler.open_positions.items():
                if position.get('symbol', '').upper() == token_symbol:
                    position_found = True
                    
                    # Execute force sell
                    sell_data = {
                        'mint': mint,
                        'symbol': token_symbol,
                        'action': 'sell',
                        'token_amount': position.get('amount', 0),
                        'expected_price': 0.0
                    }
                    
                    metadata = await self.trader.execute_trade_with_redundancy(sell_data)
                    
                    if metadata.status != "failed":
                        await update.message.reply_text(f"✅ Force sell initiated for {token_symbol}")
                    else:
                        await update.message.reply_text(f"❌ Force sell failed: {metadata.error_message}")
                    
                    break
            
            if not position_found:
                await update.message.reply_text(f"❌ No open position found for {token_symbol}")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Error executing force sell: {e}")
    
    async def positions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /positions command."""
        if not self.is_authorized(update):
            await update.message.reply_text("❌ Unauthorized access")
            return
        
        try:
            positions = self.trader.auracle.trade_handler.open_positions
            
            if not positions:
                await update.message.reply_text("📊 No open positions")
                return
            
            positions_text = "**📊 Open Positions:**\n\n"
            
            for mint, position in positions.items():
                symbol = position.get('symbol', 'UNKNOWN')
                amount = position.get('amount', 0)
                entry_price = position.get('entry_price', 0)
                current_value = position.get('current_value', 0)
                pnl = position.get('pnl', 0)
                pnl_percent = position.get('pnl_percent', 0)
                
                positions_text += f"""
**{symbol}**
• Amount: {amount:,.0f} tokens
• Entry: ${entry_price:.6f}
• Value: ${current_value:.4f}
• P&L: {pnl:+.4f} SOL ({pnl_percent:+.1f}%)
• Mint: `{mint[:8]}...{mint[-8:]}`

"""
            
            await update.message.reply_text(positions_text, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error getting positions: {e}")
    
    async def performance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /performance command."""
        if not self.is_authorized(update):
            await update.message.reply_text("❌ Unauthorized access")
            return
        
        try:
            stats = self.trader.session_stats
            
            # Calculate additional metrics
            success_rate = 0
            if stats['trades_executed'] > 0:
                success_rate = (stats['successful_trades'] / stats['trades_executed']) * 100
            
            performance_text = f"""
**📈 Performance Report**

**📊 Session Statistics:**
• Total Trades: {stats['trades_executed']}
• Successful: {stats['successful_trades']}
• Failed: {stats['failed_trades']}
• Success Rate: {success_rate:.1f}%

**⚡ Execution Metrics:**
• Avg Execution Time: {stats['average_execution_time']:.0f}ms
• P&L: {stats['total_profit_loss']:+.4f} SOL

**🎯 Recent Performance:**
"""
            
            # Add recent trade performance
            if len(self.trader.trade_journal) > 0:
                recent_trades = self.trader.trade_journal[-5:]  # Last 5 trades
                
                for trade in recent_trades:
                    status_emoji = "✅" if trade.status == "confirmed" else "❌"
                    performance_text += f"• {status_emoji} {trade.token_symbol} {trade.action} - {trade.execution_delay_ms}ms\n"
            
            performance_text += f"\n*Updated: {datetime.utcnow().strftime('%H:%M:%S UTC')}*"
            
            await update.message.reply_text(performance_text, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error getting performance: {e}")
    
    async def logs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /logs command."""
        if not self.is_authorized(update):
            await update.message.reply_text("❌ Unauthorized access")
            return
        
        try:
            count = 10  # Default
            if context.args and context.args[0].isdigit():
                count = min(int(context.args[0]), 50)  # Max 50 lines
            
            # Read log file
            log_file = 'logs/autonomous_trader.log'
            if not os.path.exists(log_file):
                await update.message.reply_text("❌ No log file found")
                return
            
            with open(log_file, 'r') as f:
                lines = f.readlines()
            
            # Get recent lines
            recent_lines = lines[-count:] if lines else []
            
            if not recent_lines:
                await update.message.reply_text("📋 No recent logs")
                return
            
            logs_text = f"**📋 Recent Logs ({count} lines):**\n\n```\n"
            logs_text += ''.join(recent_lines)
            logs_text += "\n```"
            
            # Split if too long
            if len(logs_text) > 4000:
                logs_text = logs_text[:3900] + "\n... (truncated)\n```"
            
            await update.message.reply_text(logs_text, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error reading logs: {e}")
    
    async def journal_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /journal command."""
        if not self.is_authorized(update):
            await update.message.reply_text("❌ Unauthorized access")
            return
        
        try:
            # Get date parameter
            date_str = context.args[0] if context.args else datetime.utcnow().strftime('%Y%m%d')
            
            # Validate date format
            try:
                if len(date_str) == 8:  # YYYYMMDD
                    datetime.strptime(date_str, '%Y%m%d')
                elif len(date_str) == 10:  # YYYY-MM-DD
                    date_str = datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y%m%d')
                else:
                    raise ValueError("Invalid date format")
            except ValueError:
                await update.message.reply_text("❌ Invalid date format. Use YYYY-MM-DD or YYYYMMDD")
                return
            
            # Read journal file
            journal_file = f"logs/trade_log_{date_str}.json"
            if not os.path.exists(journal_file):
                await update.message.reply_text(f"❌ No journal found for {date_str}")
                return
            
            with open(journal_file, 'r') as f:
                journal_data = json.load(f)
            
            if not journal_data:
                await update.message.reply_text(f"📖 No trades on {date_str}")
                return
            
            # Format journal entries
            journal_text = f"**📖 Trade Journal - {date_str}**\n\n"
            
            for trade in journal_data[-10:]:  # Last 10 trades
                status_emoji = "✅" if trade['status'] == "confirmed" else "❌"
                timestamp = datetime.fromisoformat(trade['timestamp']).strftime('%H:%M:%S')
                
                journal_text += f"""
{status_emoji} **{trade['token_symbol']}** - {trade['action'].upper()}
• Time: {timestamp}
• Amount: {trade['amount_sol']:.4f} SOL
• Slippage: {trade['slippage_percent']:.2f}%
• Status: {trade['status']}
"""
                
                if trade.get('error_message'):
                    journal_text += f"• Error: {trade['error_message']}\n"
                
                journal_text += "\n"
            
            await update.message.reply_text(journal_text, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error reading journal: {e}")
    
    async def blacklist_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /blacklist command."""
        if not self.is_authorized(update):
            await update.message.reply_text("❌ Unauthorized access")
            return
        
        try:
            if not context.args:
                # Show current blacklist
                if not self.trader.blacklisted_tokens:
                    await update.message.reply_text("🚫 Blacklist is empty")
                    return
                
                blacklist_text = f"**🚫 Token Blacklist ({len(self.trader.blacklisted_tokens)} tokens):**\n\n"
                
                for i, token in enumerate(list(self.trader.blacklisted_tokens)[:20]):  # Show first 20
                    blacklist_text += f"• `{token[:8]}...{token[-8:]}`\n"
                
                if len(self.trader.blacklisted_tokens) > 20:
                    blacklist_text += f"\n... and {len(self.trader.blacklisted_tokens) - 20} more"
                
                await update.message.reply_text(blacklist_text, parse_mode='Markdown')
                return
            
            action = context.args[0].lower()
            
            if action == "add" and len(context.args) > 1:
                token = context.args[1]
                self.trader.blacklisted_tokens.add(token)
                await update.message.reply_text(f"✅ Added {token} to blacklist")
                
            elif action == "remove" and len(context.args) > 1:
                token = context.args[1]
                if token in self.trader.blacklisted_tokens:
                    self.trader.blacklisted_tokens.remove(token)
                    await update.message.reply_text(f"✅ Removed {token} from blacklist")
                else:
                    await update.message.reply_text(f"❌ {token} not in blacklist")
                    
            else:
                await update.message.reply_text("❌ Usage: /blacklist [add/remove] [token_mint]")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Error managing blacklist: {e}")
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /settings command."""
        if not self.is_authorized(update):
            await update.message.reply_text("❌ Unauthorized access")
            return
        
        try:
            settings_text = f"""
**⚙️ Bot Settings**

**🎯 Trading Configuration:**
• Live Mode: {'🔴 YES' if self.trader.live_mode else '🟡 NO'}
• Max Buy Amount: {config.MAX_BUY_AMOUNT_SOL} SOL
• Scan Interval: {config.SCAN_INTERVAL_SECONDS}s
• Max Daily Trades: {config.MAX_DAILY_TRADES}
• Max Open Positions: {config.MAX_OPEN_POSITIONS}

**🛡️ Risk Management:**
• Profit Target: {config.PROFIT_TARGET_PERCENTAGE * 100}%
• Stop Loss: {config.STOP_LOSS_PERCENTAGE * 100}%
• Min Liquidity: ${config.MIN_LIQUIDITY_USD:,.0f}

**🌐 Network:**
• RPC Endpoint: {config.SOLANA_RPC_ENDPOINT}
• WebSocket: {'✅' if self.trader.websocket_client else '❌'}

**📱 Telegram:**
• Bot Active: ✅
• Authorized Users: {len(self.authorized_users)}
"""
            
            await update.message.reply_text(settings_text, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error getting settings: {e}")
    
    async def auth_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /auth command."""
        if not context.args:
            await update.message.reply_text("❌ Usage: /auth <password>")
            return
        
        password = context.args[0]
        auth_password = os.getenv('TELEGRAM_AUTH_PASSWORD', 'auracle2024')
        
        if password == auth_password:
            user_id = str(update.effective_user.id)
            username = update.effective_user.username
            
            self.authorized_users.add(user_id)
            if username:
                self.authorized_users.add(username)
            
            await update.message.reply_text("✅ Authorization successful! You can now use all commands.")
            self.logger.info(f"📱 User authorized: {username} ({user_id})")
        else:
            await update.message.reply_text("❌ Invalid password")
            self.logger.warning(f"📱 Failed auth attempt from {update.effective_user.username}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle non-command messages."""
        if not self.is_authorized(update):
            return
        
        text = update.message.text.upper()
        
        # Emergency commands
        if text == "STOP":
            await self.emergency_stop_command(update, context)
        elif text == "SELL ALL":
            await self.force_sell_all_positions(update)
        elif text in ["STATUS", "STATS"]:
            await self.status_command(update, context)
    
    async def force_sell_all_positions(self, update: Update):
        """Force sell all open positions."""
        try:
            positions = self.trader.auracle.trade_handler.open_positions
            
            if not positions:
                await update.message.reply_text("📊 No positions to sell")
                return
            
            await update.message.reply_text(f"🔄 Force selling {len(positions)} positions...")
            
            for mint, position in positions.items():
                sell_data = {
                    'mint': mint,
                    'symbol': position.get('symbol', 'UNKNOWN'),
                    'action': 'sell',
                    'token_amount': position.get('amount', 0),
                    'expected_price': 0.0
                }
                
                metadata = await self.trader.execute_trade_with_redundancy(sell_data)
                
                status_emoji = "✅" if metadata.status != "failed" else "❌"
                await update.message.reply_text(f"{status_emoji} {position.get('symbol', 'UNKNOWN')}")
            
            await update.message.reply_text("✅ Force sell all completed")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error force selling: {e}")
    
    async def send_trade_update(self, metadata):
        """Send trade update notification to Telegram."""
        if not self.bot or not self.chat_id:
            return
        
        try:
            status_emoji = "✅" if metadata.status == "confirmed" else "❌" if metadata.status == "failed" else "⏳"
            
            trade_text = f"""
{status_emoji} **Trade Update**

**Token:** {metadata.token_symbol}
**Action:** {metadata.action.upper()}
**Amount:** {metadata.amount_sol:.4f} SOL
**Status:** {metadata.status.upper()}
**Execution Time:** {metadata.execution_delay_ms}ms
"""
            
            if metadata.error_message:
                trade_text += f"**Error:** {metadata.error_message}\n"
            
            if metadata.slippage_percent > 0:
                trade_text += f"**Slippage:** {metadata.slippage_percent:.2f}%\n"
            
            trade_text += f"\n*Time: {metadata.timestamp.strftime('%H:%M:%S UTC')}*"
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=trade_text,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error sending trade update: {e}")
    
    async def send_performance_update(self, stats: Dict[str, Any]):
        """Send performance update to Telegram."""
        if not self.bot or not self.chat_id:
            return
        
        try:
            success_rate = 0
            if stats['trades_executed'] > 0:
                success_rate = (stats['successful_trades'] / stats['trades_executed']) * 100
            
            perf_text = f"""
📊 **Performance Update**

**Session Stats:**
• Trades: {stats['trades_executed']} ({success_rate:.1f}% success)
• Avg Execution: {stats['average_execution_time']:.0f}ms
• P&L: {stats['total_profit_loss']:+.4f} SOL

*Auto-update every 10 trades*
"""
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=perf_text,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error sending performance update: {e}")
    
    async def send_emergency_notification(self):
        """Send emergency stop notification."""
        if not self.bot or not self.admin_chat_id:
            return
        
        try:
            emergency_text = """
🚨 **EMERGENCY STOP ACTIVATED**

The AURACLE trading bot has been stopped.
All pending trades have been cancelled.

Check logs for details.
"""
            
            await self.bot.send_message(
                chat_id=self.admin_chat_id,
                text=emergency_text,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error sending emergency notification: {e}")
    
    async def send_error_alert(self, error_message: str):
        """Send critical error alert to admin."""
        if not self.bot or not self.admin_chat_id:
            return
        
        try:
            alert_text = f"""
⚠️ **Critical Error Alert**

**Error:** {error_message}
**Time:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

Please check the bot status and logs.
"""
            
            await self.bot.send_message(
                chat_id=self.admin_chat_id,
                text=alert_text,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error sending error alert: {e}")
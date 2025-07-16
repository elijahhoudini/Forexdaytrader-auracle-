
# AI Trading Command Handlers
# Autonomous trading with AI intelligence

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class AITradingCommands:
    """AI Trading command handlers for the telegram bot"""
    
    def __init__(self, ai_trader, data_manager):
        self.ai_trader = ai_trader
        self.data_manager = data_manager
    
    async def start_ai_trading_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start_ai_trading command"""
        try:
            user_id = str(update.effective_user.id)
            
            # Check if already active
            if self.ai_trader.active:
                await update.message.reply_text(
                    "🤖 AI trading is already active!\n\nUse /stop_ai_trading to stop it first.",
                    parse_mode='Markdown'
                )
                return
            
            # Parse amount
            amount_sol = 0.01
            if context.args:
                try:
                    amount_sol = float(context.args[0])
                    if amount_sol <= 0 or amount_sol > 1.0:
                        amount_sol = 0.01
                except ValueError:
                    amount_sol = 0.01
            
            # Start AI trading
            result = await self.ai_trader.start_autonomous_trading(user_id, amount_sol)
            
            if result["success"]:
                message = f"🤖 **AI Autonomous Trading Started!**\n\n"
                message += f"💰 **Trading Amount:** {amount_sol} SOL per trade\n"
                message += f"🎯 **Profit Target:** {self.ai_trader.profit_threshold * 100:.1f}%\n"
                message += f"🛡️ **Stop Loss:** {self.ai_trader.stop_loss * 100:.1f}%\n"
                message += f"⏱️ **Analysis Interval:** {self.ai_trader.trading_interval} seconds\n\n"
                message += "**🧠 AI Features:**\n"
                message += "• 📊 Multi-factor token analysis\n"
                message += "• 💡 Smart entry/exit timing\n"
                message += "• 🔍 Real-time market monitoring\n"
                message += "• 📈 Profit optimization\n"
                message += "• ⚖️ Risk management\n\n"
                message += "Use /stop_ai_trading to stop anytime.\n"
                message += "Use /ai_status to check progress."
                
                keyboard = [
                    [InlineKeyboardButton("📊 Check Status", callback_data="ai_status")],
                    [InlineKeyboardButton("🛑 Stop Trading", callback_data="stop_ai_trading")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
            else:
                await update.message.reply_text(
                    f"❌ Failed to start AI trading: {result.get('error', 'Unknown error')}"
                )
                
        except Exception as e:
            logger.error(f"Start AI trading command error: {e}")
            await update.message.reply_text("❌ Error starting AI trading system")
    
    async def stop_ai_trading_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stop_ai_trading command"""
        try:
            result = await self.ai_trader.stop_autonomous_trading()
            
            if result["success"]:
                stats = self.ai_trader.get_stats()
                
                message = f"🤖 **AI Trading Stopped Successfully**\n\n"
                message += f"📊 **Final Session Statistics:**\n"
                message += f"• 🔄 Total Trades: {stats['trades_executed']}\n"
                message += f"• ✅ Successful: {stats['successful_trades']}\n"
                
                if stats['trades_executed'] > 0:
                    success_rate = (stats['successful_trades'] / stats['trades_executed']) * 100
                    message += f"• 📈 Success Rate: {success_rate:.1f}%\n"
                
                message += f"• 💰 Total Profit: {stats['total_profit']:+.4f} SOL\n"
                message += f"• 🔍 Tokens Analyzed: {stats['tokens_analyzed']}\n"
                message += f"• 📈 Final Positions: {stats['positions_held']}\n\n"
                
                if stats['total_profit'] > 0:
                    message += "🎉 **Profitable session!**"
                elif stats['total_profit'] < 0:
                    message += "📉 Session had losses - AI will learn for next time"
                else:
                    message += "⚖️ Break-even session"
                
                await update.message.reply_text(message, parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Failed to stop AI trading")
                
        except Exception as e:
            logger.error(f"Stop AI trading command error: {e}")
            await update.message.reply_text("❌ Error stopping AI trading system")
    
    async def ai_status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ai_status command"""
        try:
            stats = self.ai_trader.get_stats()
            positions = self.ai_trader.get_positions()
            
            # Status header
            if stats['active']:
                status_emoji = "🟢"
                status_text = "**Active & Trading**"
            else:
                status_emoji = "🔴"
                status_text = "**Inactive**"
            
            message = f"🤖 **AI Trading Dashboard**\n\n"
            message += f"{status_emoji} Status: {status_text}\n\n"
            
            # Performance metrics
            message += f"📊 **Performance Metrics:**\n"
            message += f"• 🔄 Trades Executed: {stats['trades_executed']}\n"
            
            if stats['trades_executed'] > 0:
                success_rate = (stats['successful_trades'] / stats['trades_executed']) * 100
                message += f"• ✅ Success Rate: {success_rate:.1f}%\n"
            else:
                message += f"• ✅ Success Rate: N/A\n"
            
            message += f"• 💰 Session P&L: {stats['total_profit']:+.4f} SOL\n"
            message += f"• 🔍 Tokens Analyzed: {stats['tokens_analyzed']}\n"
            message += f"• 📈 Active Positions: {stats['positions_held']}\n\n"
            
            # Active positions
            if positions:
                message += f"🏦 **Current Positions:**\n"
                for i, (pos_id, pos) in enumerate(list(positions.items())[:3]):
                    buy_time = pos['buy_time'][:10]  # Just date
                    message += f"• {pos['token_symbol']}: {pos['amount_sol']:.4f} SOL (bought {buy_time})\n"
                
                if len(positions) > 3:
                    message += f"• ... and {len(positions) - 3} more positions\n"
            else:
                message += f"🏦 **Current Positions:** None\n"
            
            # Add control buttons
            if stats['active']:
                keyboard = [
                    [InlineKeyboardButton("🔄 Refresh", callback_data="ai_status")],
                    [InlineKeyboardButton("🛑 Stop Trading", callback_data="stop_ai_trading")]
                ]
            else:
                keyboard = [
                    [InlineKeyboardButton("🚀 Start Trading", callback_data="start_ai_trading")],
                    [InlineKeyboardButton("📊 View Trades", callback_data="ai_trades")]
                ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"AI status command error: {e}")
            await update.message.reply_text("❌ Error getting AI trading status")
    
    async def ai_trades_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ai_trades command to show recent AI trades"""
        try:
            user_id = str(update.effective_user.id)
            trades = self.data_manager.get_user_trades(user_id)
            
            if not trades:
                await update.message.reply_text("🤖 No AI trades found yet")
                return
            
            # Filter for AI trades
            ai_trades = [trade for trade in trades if trade.get('action', '').startswith('ai_')]
            
            if not ai_trades:
                await update.message.reply_text("🤖 No AI trades found yet")
                return
            
            # Show recent trades
            recent_trades = ai_trades[-10:]  # Last 10 trades
            total_profit = 0
            
            message = f"🤖 **Recent AI Trades** (Last {len(recent_trades)})\n\n"
            
            for trade in recent_trades:
                action = trade.get('action', '')
                token = trade.get('token', 'Unknown')
                amount = trade.get('amount', 0)
                success = trade.get('success', False)
                timestamp = trade.get('timestamp', '')[:10]  # Just date
                
                # Calculate profit if available
                pnl = trade.get('pnl_sol', 0)
                if pnl != 0:
                    total_profit += pnl
                    pnl_str = f" ({pnl:+.4f} SOL)"
                else:
                    pnl_str = ""
                
                status = "✅" if success else "❌"
                action_type = "🟢 BUY" if "buy" in action else "🔴 SELL"
                
                message += f"{status} {action_type} {token} - {amount:.4f} SOL{pnl_str} ({timestamp})\n"
            
            if total_profit != 0:
                profit_emoji = "💰" if total_profit > 0 else "📉"
                message += f"\n{profit_emoji} **Total Session P&L:** {total_profit:+.4f} SOL"
            
            keyboard = [
                [InlineKeyboardButton("🔄 Refresh", callback_data="ai_trades")],
                [InlineKeyboardButton("📊 Dashboard", callback_data="ai_status")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"AI trades command error: {e}")
            await update.message.reply_text("❌ Error fetching AI trades")

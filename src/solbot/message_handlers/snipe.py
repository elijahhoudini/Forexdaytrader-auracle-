
# Contact Author for your project
# Contact Info
# https://t.me/idioRusty

import logging
from typing import Dict, Any
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class AITradingHandler:
    """Handler for AI trading message interactions"""
    
    def __init__(self, ai_trader):
        self.ai_trader = ai_trader
    
    async def handle_start_ai_trading(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Dict[str, Any]:
        """Handle start AI trading command"""
        try:
            user_id = str(update.effective_user.id)
            
            # Parse amount if provided
            amount_sol = 0.01  # default
            if context.args:
                try:
                    amount_sol = float(context.args[0])
                    if amount_sol <= 0 or amount_sol > 1.0:  # Limit to reasonable amounts
                        amount_sol = 0.01
                except ValueError:
                    amount_sol = 0.01
            
            result = await self.ai_trader.start_autonomous_trading(user_id, amount_sol)
            
            if result["success"]:
                message = f"🤖 **AI Autonomous Trading Started**\n\n"
                message += f"💰 Trading Amount: {amount_sol} SOL\n"
                message += f"🎯 Profit Target: {self.ai_trader.profit_threshold * 100}%\n"
                message += f"🛡️ Stop Loss: {self.ai_trader.stop_loss * 100}%\n"
                message += f"⏱️ Analysis Interval: {self.ai_trader.trading_interval}s\n\n"
                message += "The AI will autonomously:\n"
                message += "• 🔍 Analyze market opportunities\n"
                message += "• 📊 Score tokens using AI logic\n"
                message += "• 💰 Buy promising tokens\n"
                message += "• 📈 Monitor positions for profit\n"
                message += "• 🎯 Sell at optimal times\n\n"
                message += "Use /stop_ai_trading to stop anytime."
            else:
                message = f"❌ Failed to start AI trading: {result.get('error', 'Unknown error')}"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            return result
            
        except Exception as e:
            logger.error(f"Start AI trading error: {e}")
            await update.message.reply_text("❌ Error starting AI trading")
            return {"success": False, "error": str(e)}
    
    async def handle_stop_ai_trading(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Dict[str, Any]:
        """Handle stop AI trading command"""
        try:
            result = await self.ai_trader.stop_autonomous_trading()
            
            if result["success"]:
                stats = self.ai_trader.get_stats()
                message = f"🤖 **AI Trading Stopped**\n\n"
                message += f"📊 **Session Statistics:**\n"
                message += f"• 🔄 Trades Executed: {stats['trades_executed']}\n"
                message += f"• ✅ Successful Trades: {stats['successful_trades']}\n"
                message += f"• 💰 Total Profit: {stats['total_profit']:.4f} SOL\n"
                message += f"• 🔍 Tokens Analyzed: {stats['tokens_analyzed']}\n"
                message += f"• 📈 Active Positions: {stats['positions_held']}\n"
            else:
                message = "❌ Failed to stop AI trading"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            return result
            
        except Exception as e:
            logger.error(f"Stop AI trading error: {e}")
            await update.message.reply_text("❌ Error stopping AI trading")
            return {"success": False, "error": str(e)}
    
    async def handle_ai_trading_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle AI trading status command"""
        try:
            stats = self.ai_trader.get_stats()
            positions = self.ai_trader.get_positions()
            
            message = f"🤖 **AI Trading Status**\n\n"
            
            if stats['active']:
                message += "🟢 **Status:** Active\n\n"
            else:
                message += "🔴 **Status:** Inactive\n\n"
            
            message += f"📊 **Statistics:**\n"
            message += f"• 🔄 Trades: {stats['trades_executed']}\n"
            message += f"• ✅ Success Rate: {(stats['successful_trades']/max(stats['trades_executed'], 1)*100):.1f}%\n"
            message += f"• 💰 Profit: {stats['total_profit']:.4f} SOL\n"
            message += f"• 🔍 Analyzed: {stats['tokens_analyzed']} tokens\n"
            message += f"• 📈 Positions: {stats['positions_held']}\n\n"
            
            if positions:
                message += f"🏦 **Active Positions:**\n"
                for pos_id, pos in list(positions.items())[:5]:  # Show max 5
                    message += f"• {pos['token_symbol']}: {pos['amount_sol']:.4f} SOL\n"
                if len(positions) > 5:
                    message += f"• ... and {len(positions) - 5} more\n"
            else:
                message += "🏦 **Active Positions:** None\n"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"AI trading status error: {e}")
            await update.message.reply_text("❌ Error getting AI trading status")

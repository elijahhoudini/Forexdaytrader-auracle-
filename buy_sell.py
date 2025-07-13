"""
AURACLE Buy/Sell Interface
=========================

Buy/sell interface compatible with AURACLE bot system.
Provides telegram integration for manual trading controls.
"""

import logging
import math
import time
from typing import Dict, Any, Optional
from datetime import datetime
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode, Update
from telegram.ext import CallbackContext

# Import AURACLE modules
import config
from wallet import Wallet
from trade import TradeHandler

logger = logging.getLogger(__name__)

LAMPORTS_PER_SOL = 1000000000  # Solana lamports per SOL
BUY_SELL_TOKEN_ADDRESS = "buy_sell_token_address"

# State management for bot interactions
user_states = {}
user_logs = {}

class AuracleTrading:
    """AURACLE trading interface for manual buy/sell operations"""
    
    def __init__(self):
        self.wallet = Wallet()
        self.trade_handler = TradeHandler(self.wallet)
        
    def get_wallet_balance(self) -> float:
        """Get SOL balance from wallet"""
        return self.wallet.get_balance("SOL")
        
    def get_token_balance(self, wallet_address: str, token_address: str) -> tuple:
        """Get token balance for specific wallet and token"""
        # This is a simplified implementation
        # In real implementation, this would query the blockchain
        if config.get_demo_mode():
            return (10000, 10000)  # Demo balance
        else:
            return (0, 0)  # Real implementation needed
            
    def get_token_metadata(self, token_address: str) -> tuple:
        """Get token metadata (name, symbol, decimals, etc.)"""
        # This is a simplified implementation
        # In real implementation, this would query token metadata
        return ("Unknown", "TOKEN", "", "", "", 9)

# Initialize the trading interface
auracle_trading = AuracleTrading()

def buy_option(bot, chat_id, message_id, token_address):
    """Display buy options for a token"""
    logger.info(f'buy_option called for message_id {message_id}')
    try:
        keyboard = [
            [InlineKeyboardButton("0.1", callback_data=f"BUYX_{token_address}_0.1"), 
             InlineKeyboardButton("0.2", callback_data=f"BUYX_{token_address}_0.2"), 
             InlineKeyboardButton("0.3", callback_data=f"BUYX_{token_address}_0.3")],
            [InlineKeyboardButton("0.4", callback_data=f"BUYX_{token_address}_0.4"), 
             InlineKeyboardButton("0.5", callback_data=f"BUYX_{token_address}_0.5"), 
             InlineKeyboardButton("0.6", callback_data=f"BUYX_{token_address}_0.6")],
            [InlineKeyboardButton("0.7", callback_data=f"BUYX_{token_address}_0.7"), 
             InlineKeyboardButton("0.8", callback_data=f"BUYX_{token_address}_0.8"), 
             InlineKeyboardButton("0.9", callback_data=f"BUYX_{token_address}_0.9")],
            [InlineKeyboardButton("1", callback_data=f"BUYX_{token_address}_1"), 
             InlineKeyboardButton("1.25", callback_data=f"BUYX_{token_address}_1.25"), 
             InlineKeyboardButton("1.5", callback_data=f"BUYX_{token_address}_1.5")],
            [InlineKeyboardButton("1.75", callback_data=f"BUYX_{token_address}_1.75"), 
             InlineKeyboardButton("2", callback_data=f"BUYX_{token_address}_2"), 
             InlineKeyboardButton("3", callback_data=f"BUYX_{token_address}_3")],
            [InlineKeyboardButton("4", callback_data=f"BUYX_{token_address}_4"), 
             InlineKeyboardButton("5", callback_data=f"BUYX_{token_address}_5"), 
             InlineKeyboardButton("7.5", callback_data=f"BUYX_{token_address}_7.5")],
            [InlineKeyboardButton("10", callback_data=f"BUYX_{token_address}_10"), 
             InlineKeyboardButton("20", callback_data=f"BUYX_{token_address}_20"), 
             InlineKeyboardButton("X", callback_data=f"CUSTOM_BUY_AMOUNT_{token_address}")],
            [InlineKeyboardButton("RAPID FIRE BUY", callback_data=f"BATCHBUY_{token_address}"), 
             InlineKeyboardButton("CANCEL", callback_data=f"EXIT_FUN_{token_address}")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(
            chat_id=chat_id, 
            message_id=message_id, 
            text="<b>AURACLE BUY:</b> Enter the quantity of SOL that you would like to spend", 
            reply_markup=reply_markup, 
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.exception(f"Buy option error: {e}")

def sell_option(bot, chat_id, message_id, token_address):
    """Display sell options for a token"""
    try:
        # Get wallet address (simplified for AURACLE)
        wallet_address = config.WALLET_ADDRESS
        token_balance, decimal_balance = auracle_trading.get_token_balance(wallet_address, token_address)
        
        if token_balance:
            text = "<b>AURACLE SELL:</b> Select the (%) of your tokens to sell or enter a specific number of tokens"
            keyboard = [
                [InlineKeyboardButton("5", callback_data=f"SELLX_{token_address}_5"),
                 InlineKeyboardButton("10", callback_data=f"SELLX_{token_address}_10"),
                 InlineKeyboardButton("15", callback_data=f"SELLX_{token_address}_15")],
                [InlineKeyboardButton("20", callback_data=f"SELLX_{token_address}_20"),
                 InlineKeyboardButton("25", callback_data=f"SELLX_{token_address}_25"),
                 InlineKeyboardButton("30", callback_data=f"SELLX_{token_address}_30")],
                [InlineKeyboardButton("35", callback_data=f"SELLX_{token_address}_35"),
                 InlineKeyboardButton("40", callback_data=f"SELLX_{token_address}_40"),
                 InlineKeyboardButton("45", callback_data=f"SELLX_{token_address}_45")],
                [InlineKeyboardButton("50", callback_data=f"SELLX_{token_address}_50"),
                 InlineKeyboardButton("55", callback_data=f"SELLX_{token_address}_55"),
                 InlineKeyboardButton("60", callback_data=f"SELLX_{token_address}_60")],
                [InlineKeyboardButton("65", callback_data=f"SELLX_{token_address}_65"),
                 InlineKeyboardButton("70", callback_data=f"SELLX_{token_address}_70"),
                 InlineKeyboardButton("75", callback_data=f"SELLX_{token_address}_75")],
                [InlineKeyboardButton("80", callback_data=f"SELLX_{token_address}_80"),
                 InlineKeyboardButton("85", callback_data=f"SELLX_{token_address}_85"),
                 InlineKeyboardButton("90", callback_data=f"SELLX_{token_address}_90")],
                [InlineKeyboardButton("95", callback_data=f"SELLX_{token_address}_95"),
                 InlineKeyboardButton("100", callback_data=f"SELLX_{token_address}_100"),
                 InlineKeyboardButton("X", callback_data=f"CUSTOM_SELL_PERCENT_{token_address}")],
                [InlineKeyboardButton("RAPID FIRE SELL", callback_data=f"BATCHSELL_{token_address}"),
                 InlineKeyboardButton("CANCEL", callback_data=f"EXIT_FUN_{token_address}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
        else:
            text = "You have zero balance for this token"
            keyboard = [
                [InlineKeyboardButton("MENU", callback_data=f"EXIT_FUN_{token_address}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

        bot.edit_message_text(
            chat_id=chat_id, 
            message_id=message_id, 
            text=text, 
            reply_markup=reply_markup, 
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.exception(f"Sell option error: {e}")

def buy(bot, chat_id, token_address, amount):
    """Execute a buy order"""
    try:
        balance = auracle_trading.get_wallet_balance()

        if amount > 0 and amount <= balance:
            _, symbol, _, _, _, _ = auracle_trading.get_token_metadata(token_address)
            formatted_amount = f"{amount:.8f}".rstrip('0').rstrip('.')
            
            bot.send_message(
                chat_id, 
                f"🔥 AURACLE BUYING {formatted_amount} SOL WORTH OF {symbol}\n\n"
                f"Remember to check your current SOL balance for gas fees. Please wait."
            )

            # Use AURACLE trading system
            token_info = {
                "mint": token_address,
                "symbol": symbol,
                "name": symbol,
                "liquidity": 10000,  # Default values
                "volume24h": 5000,
                "priceChange24h": 0,
                "fdv": 100000,
                "holders": 100
            }
            
            success = auracle_trading.trade_handler.buy_token(token_info, amount)
            
            if success:
                bot.send_message(chat_id, f"✅ Successfully bought {symbol} for {formatted_amount} SOL")
            else:
                bot.send_message(chat_id, f"❌ Failed to buy {symbol}")
        else:
            bot.send_message(chat_id, "❌ Invalid amount or insufficient balance")
            
    except Exception as e:
        logger.exception(f"Buy error: {e}")
        bot.send_message(chat_id, f"❌ Error processing buy order: {str(e)}")

def sell(bot, chat_id, token_address, amount):
    """Execute a sell order"""
    try:
        wallet_address = config.WALLET_ADDRESS
        token_balance, decimal_balance = auracle_trading.get_token_balance(wallet_address, token_address)

        if amount > 0 and amount <= 100:
            _, symbol, _, _, _, decimals = auracle_trading.get_token_metadata(token_address)
            
            bot.send_message(
                chat_id, 
                f"🔥 AURACLE SELLING {amount}% OF YOUR {symbol} SUPPLY\n\n"
                f"Remember to check your current SOL balance for gas fees. Please wait."
            )

            # Calculate tokens to sell
            tokens_to_sell = math.floor(amount * token_balance / 100 * math.pow(10, decimals))
            
            # Use AURACLE trading system
            if token_address in auracle_trading.trade_handler.open_positions:
                success = auracle_trading.trade_handler.sell_token(token_address, f"manual_{amount}%")
                
                if success:
                    bot.send_message(chat_id, f"✅ Successfully sold {amount}% of {symbol}")
                else:
                    bot.send_message(chat_id, f"❌ Failed to sell {symbol}")
            else:
                bot.send_message(chat_id, f"❌ No open position found for {symbol}")
        else:
            bot.send_message(chat_id, "❌ Invalid percentage (must be 1-100)")
            
    except Exception as e:
        logger.exception(f"Sell error: {e}")
        bot.send_message(chat_id, f"❌ Error processing sell order: {str(e)}")

def custom_buy_option(bot, chat_id, message_id, address):
    """Display custom buy amount input"""
    keyboard = [[InlineKeyboardButton("⬅️ BACK", callback_data=f"EXIT_FUN_{address}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(
        chat_id=chat_id, 
        message_id=message_id, 
        text="Enter the amount of SOL to spend:", 
        reply_markup=reply_markup
    )

def custom_sell_option(bot, chat_id, message_id, address):
    """Display custom sell percentage input"""
    keyboard = [[InlineKeyboardButton("⬅️ BACK", callback_data=f"EXIT_FUN_{address}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(
        chat_id=chat_id, 
        message_id=message_id, 
        text="Enter the token percentage to sell:", 
        reply_markup=reply_markup
    )

def input_token_address(update: Update, context: CallbackContext) -> None:
    """Handle token address input"""
    chat_id = update.effective_chat.id
    message_id = update.callback_query.message.message_id
    user_states[chat_id] = BUY_SELL_TOKEN_ADDRESS
    
    keyboard = [
        [InlineKeyboardButton("☰ MENU", callback_data="EXIT")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    chat_log = context.bot.edit_message_text(
        chat_id=chat_id, 
        message_id=message_id, 
        text="Enter the token address to buy/sell:", 
        reply_markup=reply_markup
    )
    user_logs[chat_id] = chat_log.message_id

def batch_buy_amount_option(update: Update, context: CallbackContext, token: str):
    """Handle batch buy amount option"""
    chat_id = update.effective_chat.id
    message_id = update.callback_query.message.message_id
    text = '<b>Enter SOL Amount to spend per transaction:</b>'
    keyboard = [[InlineKeyboardButton("⬅️ BACK", callback_data=f"BUYOPT_{token}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    chat_log = context.bot.edit_message_text(
        chat_id=chat_id, 
        message_id=message_id, 
        text=text, 
        reply_markup=reply_markup, 
        parse_mode=ParseMode.HTML
    )
    user_logs[chat_id] = chat_log.message_id

def batch_sell_amount_option(update: Update, context: CallbackContext, token: str):
    """Handle batch sell amount option"""
    chat_id = update.effective_chat.id
    message_id = update.callback_query.message.message_id
    text = '<b>Enter the number of tokens to sell per transaction:</b>'
    keyboard = [[InlineKeyboardButton("⬅️ BACK", callback_data=f"SELLOPT_{token}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    chat_log = context.bot.edit_message_text(
        chat_id=chat_id, 
        message_id=message_id, 
        text=text, 
        reply_markup=reply_markup, 
        parse_mode=ParseMode.HTML
    )
    user_logs[chat_id] = chat_log.message_id

"""
AURACLE Telegram Bot Module
===========================

Telegram integration for notifications and remote control.
"""

import threading
import time
from typing import Optional, Dict, Any
import requests
import config

class AuracleTelegramBot:
    """
    Telegram bot for AURACLE remote control and monitoring.
    
    Provides:
    - Real-time trade notifications
    - Bot status monitoring
    - Remote control commands
    - Error alerts
    """
    
    def __init__(self, bot_token: str, chat_id: str):
        """
        Initialize Telegram bot.
        
        Args:
            bot_token (str): Telegram bot token
            chat_id (str): Chat ID for notifications
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.auracle_bot = None
        self.running = False
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
        print("📱 Telegram bot initialized")
        print(f"📱 Chat ID: {chat_id}")
    
    def set_auracle_bot(self, auracle_bot):
        """Set reference to main AURACLE bot."""
        self.auracle_bot = auracle_bot
    
    def start(self):
        """Start Telegram bot in background thread."""
        self.running = True
        print("📱 Telegram bot thread started")

        # Try to send startup messages, but don't fail if network is unavailable
        try:
            self.send_message("🚀 AURACLE Bot Started")
            self.send_message(f"🔧 Mode: {config.get_trading_mode_string()}")
            self.send_message(f"💼 Wallet: {config.WALLET_ADDRESS[:8]}...")
        except Exception as e:
            print(f"⚠️ Telegram startup messages failed: {type(e).__name__}")
        
        # Start command listening
        self._listen_for_commands()
    
    def send_message(self, message: str):
        """
        Send message to Telegram chat.
        
        Args:
            message (str): Message to send
        """
        try:
            # Always log the message locally for debugging
            print(f"📱 TELEGRAM: {message[:50]}...")
            
            # Try to send to Telegram API
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, data=payload, timeout=5)
            
            if response.status_code == 200:
                print(f"📱 TELEGRAM SENT: {message[:50]}...")
            else:
                print(f"⚠️ Telegram API error: {response.status_code}")
                # Don't print full response in production to avoid spam
            
        except requests.exceptions.RequestException as e:
            # Network-related errors (DNS, connection, timeout)
            print(f"⚠️ Telegram network error: {type(e).__name__}")
            # Don't print full error to avoid spam
        except Exception as e:
            # Other errors
            print(f"⚠️ Telegram error: {type(e).__name__}")
    
    def send_trade_notification(self, action: str, token: Dict[str, Any], amount: float, pnl: Optional[float] = None):
        """
        Send trade notification to Telegram.
        
        Args:
            action (str): Trade action (BUY/SELL)
            token (Dict): Token information
            amount (float): Trade amount
            pnl (float, optional): Profit/loss percentage
        """
        symbol = token.get("symbol", token.get("name", "Unknown"))
        
        if action == "BUY":
            message = f"✅ <b>BUY EXECUTED</b>\n💰 Token: {symbol}\n💎 Amount: {amount:.4f} SOL\n🕐 Time: {time.strftime('%H:%M:%S')}"
        elif action == "SELL":
            pnl_str = f"{pnl:+.2f}%" if pnl else "Unknown"
            emoji = "🟢" if pnl and pnl > 0 else "🔴"
            message = f"{emoji} <b>SELL EXECUTED</b>\n💰 Token: {symbol}\n💎 Amount: {amount:.4f} SOL\n📊 P&L: {pnl_str}\n🕐 Time: {time.strftime('%H:%M:%S')}"
        else:
            message = f"📊 <b>{action}</b>\n💰 Token: {symbol}\n💎 Amount: {amount:.4f} SOL"
        
        self.send_message(message)
    
    def send_status_update(self):
        """Send bot status update."""
        if not self.auracle_bot:
            return
        
        try:
            status = self.auracle_bot.get_status()
            
            message = f"""
📊 <b>AURACLE Status Report</b>
⏰ Uptime: {status.get('uptime', 'Unknown')}
🔄 Scans: {status['statistics']['scans_completed']}
🎯 Trades: {status['statistics']['trades_executed']}
💼 Open Positions: {status['portfolio']['open_positions']}
🏦 Mode: {status['trading_mode']}
💰 Balance: {status.get('balance', 'Unknown')} SOL
            """.strip()
            
            self.send_message(message)
            
        except Exception as e:
            self.send_message(f"❌ Status update error: {str(e)}")
    
    def send_error_alert(self, error_message: str):
        """
        Send error alert to Telegram.
        
        Args:
            error_message (str): Error message
        """
        message = f"⚠️ <b>AURACLE ERROR</b>\n{error_message}"
        self.send_message(message)
    
    def _listen_for_commands(self):
        """Listen for Telegram commands."""
        while self.running:
            try:
                # Send periodic status updates every 5 minutes
                time.sleep(300)
                
                if self.auracle_bot:
                    self.send_status_update()
                    
            except Exception as e:
                print(f"❌ Telegram command error: {str(e)}")
                time.sleep(30)
    
    def stop(self):
        """Stop Telegram bot."""
        self.running = False
        self.send_message("🛑 AURACLE Bot Stopped")
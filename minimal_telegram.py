"""
Minimal Telegram Bot implementation for AURACLE bot
Fallback when python-telegram-bot is not available
"""
import asyncio
import json
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class Update:
    """Mock Update class"""
    def __init__(self, data=None):
        self.message = Message(data or {})
        self.callback_query = None
        self.effective_user = User(data or {})
        self.effective_chat = Chat(data or {})

class Message:
    """Mock Message class"""
    def __init__(self, data):
        self.text = data.get('text', '')
        self.from_user = User(data.get('from', {}))
        self.chat = Chat(data.get('chat', {}))
        self.message_id = data.get('message_id', 0)
    
    async def reply_text(self, text, **kwargs):
        print(f"TELEGRAM REPLY: {text}")
        return MockMessage(text)

class User:
    """Mock User class"""
    def __init__(self, data):
        self.id = data.get('id', 0)
        self.username = data.get('username', 'unknown')
        self.first_name = data.get('first_name', 'User')

class Chat:
    """Mock Chat class"""
    def __init__(self, data):
        self.id = data.get('id', 0)
        self.type = data.get('type', 'private')

class Bot:
    """Mock Bot class"""
    def __init__(self, token):
        self.token = token
        logger.info(f"Initialized mock Telegram Bot with token: {token[:10]}...")
    
    async def send_message(self, chat_id, text, **kwargs):
        print(f"TELEGRAM MESSAGE TO {chat_id}: {text}")
        return MockMessage(text)
    
    async def send_photo(self, chat_id, photo, **kwargs):
        print(f"TELEGRAM PHOTO TO {chat_id}: {kwargs.get('caption', 'Photo')}")
        return MockMessage("Photo sent")

class MockMessage:
    """Mock message response"""
    def __init__(self, text):
        self.text = text
        self.message_id = 1

class Application:
    """Mock Application class"""
    def __init__(self):
        self.bot = None
        self.handlers = []
    
    @classmethod
    def builder(cls):
        return MockApplicationBuilder()
    
    def add_handler(self, handler):
        self.handlers.append(handler)
    
    async def initialize(self):
        logger.info("Mock Telegram application initialized")
    
    async def start(self):
        logger.info("Mock Telegram application started")
    
    async def stop(self):
        logger.info("Mock Telegram application stopped")
    
    def run_polling(self):
        """Run polling in mock mode"""
        logger.info("Mock Telegram bot running in polling mode")
        logger.info("Commands available: /start, /help, /status")
        
        # Simulate some basic commands
        try:
            while True:
                asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Mock bot stopped")

class MockApplicationBuilder:
    """Mock Application Builder"""
    def __init__(self):
        self._token = None
        self._app = Application()
    
    def token(self, token):
        self._token = token
        self._app.bot = Bot(token)
        return self
    
    def build(self):
        return self._app

class CommandHandler:
    """Mock Command Handler"""
    def __init__(self, command, callback):
        self.command = command
        self.callback = callback

class CallbackQueryHandler:
    """Mock Callback Query Handler"""
    def __init__(self, callback):
        self.callback = callback

class MessageHandler:
    """Mock Message Handler"""
    def __init__(self, filters, callback):
        self.filters = filters
        self.callback = callback

class filters:
    """Mock filters"""
    class TEXT:
        pass
    
    class PHOTO:
        pass

class InlineKeyboardButton:
    """Mock Inline Keyboard Button"""
    def __init__(self, text, callback_data=None, url=None):
        self.text = text
        self.callback_data = callback_data
        self.url = url

class InlineKeyboardMarkup:
    """Mock Inline Keyboard Markup"""
    def __init__(self, keyboard):
        self.keyboard = keyboard

class ContextTypes:
    """Mock Context Types"""
    DEFAULT_TYPE = None
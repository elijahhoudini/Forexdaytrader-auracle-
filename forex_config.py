"""
Forex Configuration Module
==========================

Configuration settings specific to Forex trading, replacing Solana blockchain settings.
"""

import os
from typing import Dict, Any, List
import logging

# Try to load dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
    load_dotenv('.env.forex.example')  # Load Forex-specific example
except ImportError:
    def load_dotenv():
        pass

# ==================== FOREX TRADING CONFIGURATION ====================

# Core Trading Settings - LIVE TRADING MODE
FOREX_DEMO_MODE = os.getenv('FOREX_DEMO_MODE', 'false').lower() == 'true'
AUTONOMOUS_TRADING = os.getenv('AUTONOMOUS_TRADING', 'true').lower() == 'true'

# API Keys and Access
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
TWELVE_DATA_API_KEY = os.getenv('TWELVE_DATA_API_KEY')
OANDA_API_TOKEN = os.getenv('OANDA_API_TOKEN')
OANDA_ACCOUNT_ID = os.getenv('OANDA_ACCOUNT_ID')

# Trading Pairs
TRADING_PAIRS = os.getenv('TRADING_PAIRS', 'EURUSD,GBPUSD,USDJPY,USDCHF,AUDUSD,USDCAD').split(',')

# Account Settings
FOREX_ACCOUNT_BALANCE = float(os.getenv('FOREX_ACCOUNT_BALANCE', '10000'))
MAX_RISK_PER_TRADE = float(os.getenv('MAX_RISK_PER_TRADE', '0.02'))  # 2% risk per trade
MAX_FOREX_POSITIONS = int(os.getenv('MAX_FOREX_POSITIONS', '5'))
MAX_CONCURRENT_POSITIONS = int(os.getenv('MAX_CONCURRENT_POSITIONS', '3'))

# Trading Timing
SCAN_INTERVAL_SECONDS = int(os.getenv('SCAN_INTERVAL_SECONDS', '300'))  # 5 minutes
MAX_DAILY_TRADES = int(os.getenv('MAX_DAILY_TRADES', '10'))
DAILY_LOSS_LIMIT = float(os.getenv('DAILY_LOSS_LIMIT', '200'))
MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', '0.10'))  # 0.1 lots

# ==================== METATRADER INTEGRATION ====================

MT5_ENABLED = os.getenv('MT5_ENABLED', 'false').lower() == 'true'
MT5_LOGIN = os.getenv('MT5_LOGIN')
MT5_PASSWORD = os.getenv('MT5_PASSWORD')
MT5_SERVER = os.getenv('MT5_SERVER')

# ==================== WEBHOOK INTEGRATION ====================

FOREX_WEBHOOK_URL = os.getenv('FOREX_WEBHOOK_URL')
WEBHOOK_ENABLED = bool(FOREX_WEBHOOK_URL)

# ==================== TELEGRAM INTEGRATION ====================

TELEGRAM_ENABLED = os.getenv('TELEGRAM_ENABLED', 'false').lower() == 'true'
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# ==================== RISK MANAGEMENT ====================

# Daily limits
MAX_DAILY_LOSS = float(os.getenv('MAX_DAILY_LOSS', '500'))
MAX_DRAWDOWN = float(os.getenv('MAX_DRAWDOWN', '1000'))

# Position sizing
POSITION_SIZE_METHOD = os.getenv('POSITION_SIZE_METHOD', 'fixed')
KELLY_CRITERION_ENABLED = os.getenv('KELLY_CRITERION_ENABLED', 'false').lower() == 'true'

# Stop loss and take profit
DEFAULT_STOP_LOSS_PIPS = int(os.getenv('DEFAULT_STOP_LOSS_PIPS', '50'))
DEFAULT_TAKE_PROFIT_PIPS = int(os.getenv('DEFAULT_TAKE_PROFIT_PIPS', '150'))
TRAILING_STOP_ENABLED = os.getenv('TRAILING_STOP_ENABLED', 'true').lower() == 'true'

# ==================== TECHNICAL ANALYSIS SETTINGS ====================

# Signal thresholds
SIGNAL_CONFIDENCE_THRESHOLD = int(os.getenv('SIGNAL_CONFIDENCE_THRESHOLD', '60'))
RSI_OVERSOLD_THRESHOLD = int(os.getenv('RSI_OVERSOLD_THRESHOLD', '30'))
RSI_OVERBOUGHT_THRESHOLD = int(os.getenv('RSI_OVERBOUGHT_THRESHOLD', '70'))

# Moving averages
MA_FAST_PERIOD = int(os.getenv('MA_FAST_PERIOD', '12'))
MA_SLOW_PERIOD = int(os.getenv('MA_SLOW_PERIOD', '26'))
MA_SIGNAL_PERIOD = int(os.getenv('MA_SIGNAL_PERIOD', '9'))

# Bollinger Bands
BB_PERIOD = int(os.getenv('BB_PERIOD', '20'))
BB_STD_DEV = float(os.getenv('BB_STD_DEV', '2.0'))

# Trend strength
ADX_TREND_THRESHOLD = int(os.getenv('ADX_TREND_THRESHOLD', '25'))
MIN_TREND_STRENGTH = int(os.getenv('MIN_TREND_STRENGTH', '20'))

# ==================== TIMEFRAME SETTINGS ====================

PRIMARY_TIMEFRAME = os.getenv('PRIMARY_TIMEFRAME', '1hour')
SECONDARY_TIMEFRAME = os.getenv('SECONDARY_TIMEFRAME', '4hour')
QUICK_SCALP_TIMEFRAME = os.getenv('QUICK_SCALP_TIMEFRAME', '15min')

ANALYSIS_PERIODS = int(os.getenv('ANALYSIS_PERIODS', '100'))
MIN_HISTORY_REQUIRED = int(os.getenv('MIN_HISTORY_REQUIRED', '50'))

# ==================== LOGGING AND MONITORING ====================

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', './logs/auracle_forex.log')
TRADE_LOG_PATH = os.getenv('TRADE_LOG_PATH', './logs/trades.csv')

ENABLE_PERFORMANCE_TRACKING = os.getenv('ENABLE_PERFORMANCE_TRACKING', 'true').lower() == 'true'
DAILY_REPORT_TIME = os.getenv('DAILY_REPORT_TIME', '17:00')
WEEKLY_REPORT_DAY = os.getenv('WEEKLY_REPORT_DAY', 'friday')

# ==================== DATA STORAGE ====================

DATA_STORAGE_PATH = os.getenv('DATA_STORAGE_PATH', './data/forex')
BACKUP_ENABLED = os.getenv('BACKUP_ENABLED', 'true').lower() == 'true'
BACKUP_INTERVAL_HOURS = int(os.getenv('BACKUP_INTERVAL_HOURS', '24'))
BACKUP_RETENTION_DAYS = int(os.getenv('BACKUP_RETENTION_DAYS', '30'))

# ==================== ADVANCED FEATURES ====================

CURRENCY_STRENGTH_ENABLED = os.getenv('CURRENCY_STRENGTH_ENABLED', 'true').lower() == 'true'
CORRELATION_ANALYSIS_ENABLED = os.getenv('CORRELATION_ANALYSIS_ENABLED', 'true').lower() == 'true'

NEWS_SENTIMENT_ENABLED = os.getenv('NEWS_SENTIMENT_ENABLED', 'false').lower() == 'true'
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

ECONOMIC_CALENDAR_ENABLED = os.getenv('ECONOMIC_CALENDAR_ENABLED', 'false').lower() == 'true'
CALENDAR_API_KEY = os.getenv('CALENDAR_API_KEY')

# ==================== TESTING AND DEVELOPMENT ====================

BACKTESTING_ENABLED = os.getenv('BACKTESTING_ENABLED', 'false').lower() == 'true'
PAPER_TRADING_ENABLED = os.getenv('PAPER_TRADING_ENABLED', 'false').lower() == 'true'
FORWARD_TESTING_ENABLED = os.getenv('FORWARD_TESTING_ENABLED', 'false').lower() == 'true'

DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
VERBOSE_LOGGING = os.getenv('VERBOSE_LOGGING', 'false').lower() == 'true'
SAVE_RAW_DATA = os.getenv('SAVE_RAW_DATA', 'false').lower() == 'true'

# ==================== BOT IDENTIFICATION ====================

BOT_NAME = "AURACLE Forex Trading Bot"
BOT_VERSION = "2.0.0-forex"
BOT_MODE = "Forex Trading"

# ==================== LEGACY SETTINGS (DISABLED) ====================

# These are kept for compatibility but disabled for Forex trading
SOLANA_ENABLED = False
JUPITER_API_ENABLED = False
WALLET_PRIVATE_KEY = None
SOLANA_RPC_ENDPOINT = None

# ==================== HELPER FUNCTIONS ====================

def get_trading_mode_string() -> str:
    """Get human-readable trading mode description."""
    if FOREX_DEMO_MODE:
        return "🔶 FOREX DEMO MODE (Safe - No real trades)"
    else:
        return "🔴 FOREX LIVE MODE (REAL MONEY TRADING - LIVE EXECUTION)"

def get_enabled_apis() -> List[str]:
    """Get list of enabled API providers."""
    apis = []
    if ALPHA_VANTAGE_API_KEY:
        apis.append("Alpha Vantage")
    if TWELVE_DATA_API_KEY:
        apis.append("Twelve Data")
    if OANDA_API_TOKEN:
        apis.append("OANDA")
    return apis

def get_enabled_integrations() -> List[str]:
    """Get list of enabled integrations."""
    integrations = []
    if MT5_ENABLED:
        integrations.append("MetaTrader 5")
    if WEBHOOK_ENABLED:
        integrations.append("Webhook")
    if TELEGRAM_ENABLED:
        integrations.append("Telegram")
    return integrations

def validate_config() -> Dict[str, Any]:
    """Validate configuration and return status."""
    print("🔍 Validating AURACLE Forex configuration...")
    
    status = {
        'valid': True,
        'warnings': [],
        'errors': []
    }
    
    # Check trading mode
    print(f"📊 Trading mode: {get_trading_mode_string()}")
    
    # Check API availability
    enabled_apis = get_enabled_apis()
    if enabled_apis:
        print(f"✅ API providers: {', '.join(enabled_apis)}")
    else:
        status['errors'].append("No Forex API providers configured")
        print("❌ No Forex API providers configured")
    
    # Check integrations
    enabled_integrations = get_enabled_integrations()
    if enabled_integrations:
        print(f"✅ Integrations: {', '.join(enabled_integrations)}")
    else:
        print("ℹ️  No trading integrations enabled - demo mode only")
    
    # Check trading pairs
    if TRADING_PAIRS:
        print(f"✅ Trading pairs: {', '.join(TRADING_PAIRS)}")
    else:
        status['errors'].append("No trading pairs configured")
    
    # Check risk settings
    if MAX_RISK_PER_TRADE > 0.05:  # More than 5%
        status['warnings'].append(f"High risk per trade: {MAX_RISK_PER_TRADE*100}%")
    
    if DAILY_LOSS_LIMIT > FOREX_ACCOUNT_BALANCE * 0.1:  # More than 10% of balance
        status['warnings'].append(f"High daily loss limit: ${DAILY_LOSS_LIMIT}")
    
    print(f"✅ Account balance: ${FOREX_ACCOUNT_BALANCE}")
    print(f"✅ Max risk per trade: {MAX_RISK_PER_TRADE*100}%")
    print(f"✅ Max daily loss: ${DAILY_LOSS_LIMIT}")
    
    # Warnings and errors
    for warning in status['warnings']:
        print(f"⚠️  Warning: {warning}")
    
    for error in status['errors']:
        print(f"❌ Error: {error}")
        status['valid'] = False
    
    if status['valid']:
        print("✅ Configuration validation passed")
    else:
        print("❌ Configuration validation failed")
    
    return status

# Auto-validate on import
if __name__ != "__main__":
    validate_config()

# Configuration summary for other modules
CONFIG_SUMMARY = {
    'bot_name': BOT_NAME,
    'bot_version': BOT_VERSION,
    'demo_mode': FOREX_DEMO_MODE,
    'autonomous': AUTONOMOUS_TRADING,
    'trading_pairs': TRADING_PAIRS,
    'account_balance': FOREX_ACCOUNT_BALANCE,
    'max_positions': MAX_FOREX_POSITIONS,
    'apis_enabled': get_enabled_apis(),
    'integrations_enabled': get_enabled_integrations()
}
"""
AURACLE Configuration Module
===========================

Global settings and constants for the AURACLE autonomous trading bot.
Configuration includes trading parameters, risk management, and system settings.
"""

import os
from typing import Dict, Any

# ==================== TRADING CONFIGURATION ====================

# Trading Amounts
MAX_BUY_AMOUNT_SOL = float(os.getenv("MAX_BUY_AMOUNT_SOL", "0.01"))  # Minimum trade amount: 0.01 SOL per trade
MIN_LIQUIDITY_THRESHOLD = int(os.getenv("MIN_LIQUIDITY_THRESHOLD", "1000"))
POSITION_SIZE_PERCENTAGE = float(os.getenv("POSITION_SIZE_PERCENTAGE", "0.1"))

# Trading Strategy
PROFIT_TARGET_PERCENTAGE = float(os.getenv("PROFIT_TARGET_PERCENTAGE", "0.15"))  # 15% profit target (more realistic)
STOP_LOSS_PERCENTAGE = float(os.getenv("STOP_LOSS_PERCENTAGE", "-0.08"))  # -8% stop loss (less aggressive)
SCAN_INTERVAL_SECONDS = int(os.getenv("SCAN_INTERVAL_SECONDS", "45"))  # 45 second intervals for better performance

# Dynamic Allocation Settings
DYNAMIC_ALLOCATION_ENABLED = True  # Enable dynamic allocation for high-confidence trades
HIGH_CONFIDENCE_MULTIPLIER = 1.5  # Multiply base amount by this for high-confidence trades
HIGH_CONFIDENCE_PATTERNS = ["DEM02", "DEM04"]  # Token patterns that indicate high confidence

# ==================== RISK MANAGEMENT ====================

# Risk Limits
MAX_DAILY_TRADES = 50  # Maximum trades per day
MAX_OPEN_POSITIONS = 10  # Maximum concurrent positions
BLACKLIST_DURATION_HOURS = 24  # Hours to keep tokens blacklisted

# Safety Checks
ENABLE_FRAUD_DETECTION = True
ENABLE_LIQUIDITY_CHECKS = True
ENABLE_VOLUME_VALIDATION = True

# ==================== SYSTEM CONFIGURATION ====================

# Logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE = True
LOG_TO_CONSOLE = True
MAX_LOG_FILE_SIZE_MB = 10

# Data Storage
DATA_DIRECTORY = "data"
TRADE_LOG_FILE = "data/trade_logs.json"
ERROR_LOG_FILE = "data/error_logs.json"
FLAG_LOG_FILE = "data/flag_logs.json"

# ==================== EXTERNAL SERVICES ====================

# Telegram Bot (Enabled for live trading)
TELEGRAM_ENABLED = os.getenv("TELEGRAM_ENABLED", "true").lower() == "true"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7661187219:AAHuqb1IB9QtYxHeDbTbnkobwK1rFtyvqvk")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "7661187219")

# Solana Network
SOLANA_RPC_ENDPOINT = os.getenv("SOLANA_RPC_ENDPOINT", "https://api.mainnet-beta.solana.com")
SOLANA_COMMITMENT = "confirmed"

# Jupiter Aggregator Settings
JUPITER_API_URL = "https://quote-api.jup.ag/v6"
JUPITER_SLIPPAGE_BPS = int(os.getenv("JUPITER_SLIPPAGE_BPS", "50"))  # 0.5% default slippage
JUPITER_PRIORITY_FEE = int(os.getenv("JUPITER_PRIORITY_FEE", "1000"))  # 1000 microlamports

# Wallet Configuration (Live trading enabled)
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS", "Emac86gtaA1YQg62F8QG5eam7crgD1c1TQj5C8nYHGrr")
WALLET_PRIVATE_KEY = os.getenv("WALLET_PRIVATE_KEY", "")
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"  # Demo mode by default for safety

# Runtime configuration state
_runtime_config = {
    "demo_mode": DEMO_MODE
}

# ==================== TRAVELER 5798 SPECIFIC ====================

# Bot Identity
BOT_NAME = "AURACLE"
BOT_VERSION = "1.0.0"
TRAVELER_ID = "5798"
BOT_DESCRIPTION = "Autonomous AI Solana Trading Assistant"

# Operational Settings
AUTONOMOUS_MODE = True  # Run without human intervention
LEARNING_MODE = False  # Enable ML model training (future feature)
BACKTESTING_MODE = False  # Historical data testing mode

# ==================== HELPER FUNCTIONS ====================

def get_config_dict() -> Dict[str, Any]:
    """
    Returns all configuration as a dictionary.
    Useful for logging and debugging.
    """
    return {
        "trading": {
            "max_buy_amount_sol": MAX_BUY_AMOUNT_SOL,
            "min_liquidity_threshold": MIN_LIQUIDITY_THRESHOLD,
            "profit_target": PROFIT_TARGET_PERCENTAGE,
            "stop_loss": STOP_LOSS_PERCENTAGE,
            "scan_interval": SCAN_INTERVAL_SECONDS,
            "dynamic_allocation_enabled": DYNAMIC_ALLOCATION_ENABLED,
            "high_confidence_multiplier": HIGH_CONFIDENCE_MULTIPLIER,
            "high_confidence_patterns": HIGH_CONFIDENCE_PATTERNS
        },
        "risk": {
            "max_daily_trades": MAX_DAILY_TRADES,
            "max_open_positions": MAX_OPEN_POSITIONS,
            "fraud_detection": ENABLE_FRAUD_DETECTION
        },
        "system": {
            "bot_name": BOT_NAME,
            "version": BOT_VERSION,
            "traveler_id": TRAVELER_ID,
            "autonomous_mode": AUTONOMOUS_MODE,
            "demo_mode": get_demo_mode()
        }
    }

def get_demo_mode() -> bool:
    """Get current demo mode status."""
    return _runtime_config.get("demo_mode", DEMO_MODE)

def set_demo_mode(enabled: bool) -> bool:
    """
    Set demo mode at runtime.

    Args:
        enabled (bool): True to enable demo mode, False to disable

    Returns:
        bool: True if change was successful
    """
    try:
        _runtime_config["demo_mode"] = enabled
        print(f"🔄 Demo mode {'enabled' if enabled else 'disabled'}")
        return True
    except Exception as e:
        print(f"❌ Failed to set demo mode: {e}")
        return False

def is_live_trading_enabled() -> bool:
    """Check if live trading is enabled (demo mode is off)."""
    return not get_demo_mode()

def get_trading_mode_string() -> str:
    """Get a user-friendly string describing current trading mode."""
    if get_demo_mode():
        return "🔶 DEMO MODE (Safe - No real trades)"
    else:
        return "🔥 LIVE TRADING (Real money at risk)"

def validate_config() -> bool:
    """
    Validates configuration settings.
    Returns True if all settings are valid.
    """
    if MAX_BUY_AMOUNT_SOL <= 0:
        print("❌ MAX_BUY_AMOUNT_SOL must be positive")
        return False
    if MIN_LIQUIDITY_THRESHOLD < 0:
        print("❌ MIN_LIQUIDITY_THRESHOLD must be non-negative")
        return False
    if PROFIT_TARGET_PERCENTAGE <= 0:
        print("❌ PROFIT_TARGET_PERCENTAGE must be positive")
        return False
    if STOP_LOSS_PERCENTAGE >= 0:
        print("❌ STOP_LOSS_PERCENTAGE must be negative")
        return False

    # Show current trading mode
    print(f"📊 Trading mode: {get_trading_mode_string()}")

    # Validate Telegram configuration
    if TELEGRAM_ENABLED:
        if not TELEGRAM_BOT_TOKEN:
            print("⚠️  TELEGRAM_BOT_TOKEN not configured - disabling Telegram notifications")
            return False
        if not TELEGRAM_CHAT_ID:
            print("⚠️  TELEGRAM_CHAT_ID not configured - disabling Telegram notifications")
            return False
        print("✅ Telegram bot configured and enabled")

    # Validate wallet configuration for live trading
    if not get_demo_mode():
        if not WALLET_ADDRESS:
            print("❌ WALLET_ADDRESS required for live trading")
            return False
        print("✅ Live trading enabled with wallet:", WALLET_ADDRESS[:8] + "...")
    else:
        print("⚠️  Demo mode enabled - no real trades will be executed")

    return True

# Environment validation
if not validate_config():
    raise ValueError("Invalid configuration detected. Please check your settings.")

# Create data directory if it doesn't exist
os.makedirs(DATA_DIRECTORY, exist_ok=True)
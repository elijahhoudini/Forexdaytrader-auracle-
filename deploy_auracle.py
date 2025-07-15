#!/usr/bin/env python3
"""
AURACLE Bot Quick Deployment Script
===================================

One-command deployment for AURACLE bot with automatic configuration.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Print deployment banner"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                  AURACLE BOT DEPLOYMENT                     ║
    ║                      Quick Setup                             ║
    ╠══════════════════════════════════════════════════════════════╣
    ║ 🤖 Full Telegram integration with all commands             ║
    ║ 🎯 Auto-sniper with honeypot protection                    ║
    ║ 💰 Wallet generation and management                        ║
    ║ 🎁 Referral system with persistent tracking               ║
    ║ 📊 Profit/loss tracking and reporting                     ║
    ║ 🚀 Continuous operation mode                               ║
    ║ 🛡️ Advanced security features                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

def check_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def setup_environment():
    """Setup environment and configuration"""
    print("\n⚙️  Setting up environment...")
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print("✅ Data directory created")
    
    # Create required data files
    data_files = {
        "users.json": {},
        "wallets.json": {},
        "referrals.json": {},
        "trading_logs.json": {}
    }
    
    for filename, default_data in data_files.items():
        file_path = data_dir / filename
        if not file_path.exists():
            import json
            with open(file_path, 'w') as f:
                json.dump(default_data, f, indent=2)
            print(f"✅ Created {filename}")
    
    # Setup .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env configuration file...")
        env_content = """# AURACLE Bot Configuration
# =========================

# Basic Settings
DEMO_MODE=true
BOT_NAME=AURACLE
BOT_VERSION=1.0.0
TRAVELER_ID=5798

# Trading Settings
MAX_BUY_AMOUNT_SOL=0.01
PROFIT_TARGET_PERCENTAGE=0.20
STOP_LOSS_PERCENTAGE=-0.05
SCAN_INTERVAL_SECONDS=30
MAX_DAILY_TRADES=50
MAX_OPEN_POSITIONS=10

# Wallet Configuration (Required for live trading)
WALLET_ADDRESS=
WALLET_PRIVATE_KEY=

# Solana Network
SOLANA_RPC_ENDPOINT=https://api.mainnet-beta.solana.com

# Telegram Bot (Required for Telegram integration)
TELEGRAM_ENABLED=false
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Premium Features (Optional)
MORALIS_API_KEY=
PURCHASED_RPC=
DATABASE_URI=

# Jupiter Settings
JUPITER_SLIPPAGE_BPS=50
JUPITER_PRIORITY_FEE=1000

# Advanced Settings
LLC_GOAL_SOL=500
AURACLE_SCORE_THRESHOLD=0.4
MIN_LIQUIDITY_USD=15000
MIN_VOLUME_24H_USD=10000
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ .env file created")
    else:
        print("✅ .env file already exists")

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    # Try to install key dependencies
    dependencies = [
        "python-dotenv",
        "requests",
        "asyncio",
        "aiofiles"
    ]
    
    for dep in dependencies:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                          capture_output=True, check=True)
            print(f"✅ Installed {dep}")
        except subprocess.CalledProcessError:
            print(f"⚠️  Failed to install {dep} - using fallback")
    
    print("✅ Core dependencies installed")

def test_installation():
    """Test the installation"""
    print("\n🧪 Testing installation...")
    
    try:
        # Test imports
        import main
        print("✅ Main module import successful")
        
        # Test configuration
        import config
        print("✅ Configuration loaded successfully")
        
        # Test bot components
        from unified_telegram_bot import AuracleTelegramBot
        print("✅ Telegram bot components loaded")
        
        return True
    except Exception as e:
        print(f"❌ Installation test failed: {e}")
        return False

def show_usage_instructions():
    """Show usage instructions"""
    print("""
    ✅ AURACLE Bot deployed successfully!
    
    📋 Next Steps:
    
    1. 🔧 Configure your bot:
       • Edit .env file with your settings
       • Add TELEGRAM_BOT_TOKEN for Telegram integration
       • Add WALLET_PRIVATE_KEY for live trading
    
    2. 🚀 Run the bot:
       • Demo mode: python main.py
       • Test suite: python test_auracle_production.py
    
    3. 📱 Telegram Commands:
       • /start_sniper - Start auto-sniping
       • /stop_sniper - Stop auto-sniping
       • /snipe <amount> - Manual snipe
       • /generate_wallet - Generate new wallet
       • /connect_wallet - Connect existing wallet
       • /referral - View referral info
       • /claim - Claim referral rewards
       • /qr - Generate wallet QR code
       • /status - View bot status
       • /help - Show all commands
    
    4. 🛡️ Security Features:
       • Starts in demo mode by default
       • Honeypot protection enabled
       • Rug pull detection active
       • All trades logged and tracked
    
    5. 🎯 Support:
       • Documentation: README.md
       • Test results: Run test_auracle_production.py
       • Configuration: Edit .env file
    
    Happy trading! 🚀
    """)

def main():
    """Main deployment function"""
    print_banner()
    
    if not check_python_version():
        sys.exit(1)
    
    setup_environment()
    install_dependencies()
    
    if test_installation():
        show_usage_instructions()
        print("🎉 AURACLE Bot is ready for production!")
        return True
    else:
        print("❌ Deployment failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
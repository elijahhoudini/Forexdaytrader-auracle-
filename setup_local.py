#!/usr/bin/env python3
"""
Local Environment Setup for AURACLE Bot
=======================================

This script sets up the bot for local laptop/terminal usage by:
1. Creating minimal configuration files
2. Installing essential dependencies only
3. Setting up local data directories
4. Providing a simple launch interface
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Print setup banner."""
    print("=" * 60)
    print("🚀 AURACLE Bot - Local Environment Setup")
    print("=" * 60)
    print("Setting up for local laptop/terminal usage...")
    print()

def check_python_version():
    """Check Python version compatibility."""
    print("📋 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def create_local_env():
    """Create a minimal .env file for local usage."""
    print("📝 Creating local .env configuration...")
    
    env_content = """# AURACLE Bot - Local Configuration
# This file contains minimal settings for local laptop usage

# Demo Mode (Safe for testing - no real trades)
DEMO_MODE=true

# Telegram Integration (Optional - can be disabled)
TELEGRAM_ENABLED=false
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# Wallet Configuration (Required for live trading)
WALLET_PRIVATE_KEY=your_solana_private_key_here
WALLET_ADDRESS=your_wallet_address_here

# Trading Configuration (Conservative defaults)
MAX_BUY_AMOUNT_SOL=0.01
PROFIT_TARGET_PERCENTAGE=0.15
STOP_LOSS_PERCENTAGE=-0.08
SCAN_INTERVAL_SECONDS=60
MAX_DAILY_TRADES=50
MAX_OPEN_POSITIONS=10

# Network Configuration
SOLANA_RPC_ENDPOINT=https://api.mainnet-beta.solana.com

# Optional Premium Features (Leave empty to use free alternatives)
PURCHASED_RPC=
MORALIS_API_KEY=
DATABASE_URI=
"""
    
    env_file = Path(".env")
    if env_file.exists():
        print("⚠️  .env file already exists, creating .env.local as backup")
        env_file = Path(".env.local")
    
    env_file.write_text(env_content)
    print(f"✅ Created {env_file}")
    
    return env_file

def setup_data_directories():
    """Create necessary data directories."""
    print("📁 Setting up data directories...")
    
    directories = [
        "data",
        "data/storage",
        "data/logs",
        "data/backups"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def install_dependencies():
    """Install minimal dependencies for local usage."""
    print("📦 Installing dependencies...")
    
    try:
        # Use minimal requirements for local setup
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "-r", "requirements.minimal.txt"
        ], check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("💡 Try running manually: pip install -r requirements.minimal.txt")
        return False

def create_launch_script():
    """Create a simple launch script for local usage."""
    print("🚀 Creating launch script...")
    
    launcher_content = """#!/usr/bin/env python3
'''
AURACLE Bot - Local Launcher
============================

Simple launcher for local laptop usage.
'''

import os
import sys
import subprocess

def main():
    print("🚀 AURACLE Bot - Local Launcher")
    print("=" * 40)
    
    # Set local environment
    os.environ.setdefault("DEMO_MODE", "true")
    os.environ.setdefault("TELEGRAM_ENABLED", "false")
    
    # Choose bot mode
    print("Choose bot mode:")
    print("1. AURACLE (Autonomous trading)")
    print("2. Solbot (Telegram controlled)")
    print("3. Demo mode test")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        print("🤖 Starting AURACLE in autonomous mode...")
        os.system("python start_unified.py --bot auracle")
    elif choice == "2":
        print("📱 Starting Solbot in Telegram mode...")
        os.system("python start_unified.py --bot solbot")
    elif choice == "3":
        print("🔶 Starting demo mode test...")
        os.system("python -c \\"import auracle; print('Demo test completed')\\"")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
"""
    
    launcher_file = Path("launch_local.py")
    launcher_file.write_text(launcher_content)
    
    # Make executable on Unix-like systems
    if os.name != 'nt':
        os.chmod(launcher_file, 0o755)
    
    print(f"✅ Created {launcher_file}")
    return launcher_file

def create_gitignore_updates():
    """Update .gitignore for local development."""
    print("📄 Updating .gitignore for local development...")
    
    local_ignores = """
# Local development files
.env.local
launch_local.py
data/logs/*
data/backups/*
*.local
.vscode/
.idea/
"""
    
    gitignore_path = Path(".gitignore")
    if gitignore_path.exists():
        current_content = gitignore_path.read_text()
        if "# Local development files" not in current_content:
            gitignore_path.write_text(current_content + local_ignores)
            print("✅ Updated .gitignore")
    else:
        gitignore_path.write_text(local_ignores)
        print("✅ Created .gitignore")

def print_next_steps(env_file, launcher_file):
    """Print next steps for user."""
    print("\n" + "=" * 60)
    print("🎉 Local setup completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print(f"1. Edit {env_file} with your configuration")
    print("2. Set DEMO_MODE=false when ready for live trading")
    print("3. Add your wallet private key and Telegram bot token")
    print(f"4. Run: python {launcher_file}")
    print("\nOr run directly:")
    print("  python start_unified.py --bot auracle")
    print("  python start_unified.py --bot solbot")
    print("\nFor help: python start_unified.py --help")
    print("\n⚠️  Always test in DEMO_MODE=true first!")

def main():
    """Main setup function."""
    print_banner()
    
    if not check_python_version():
        sys.exit(1)
    
    # Setup steps
    env_file = create_local_env()
    setup_data_directories()
    
    # Install dependencies (optional, can be done manually)
    install_success = install_dependencies()
    if not install_success:
        print("⚠️  Dependency installation failed, continue with manual installation")
    
    launcher_file = create_launch_script()
    create_gitignore_updates()
    
    print_next_steps(env_file, launcher_file)

if __name__ == "__main__":
    main()
#!/bin/bash
# start_telegram_wallet.sh - Start wallet setup via Telegram
# Created: July 17, 2025

echo "======================================"
echo "🤖 AURACLE Telegram Wallet Setup 🤖"
echo "======================================"
echo "Starting Telegram bot for secure wallet setup..."
echo "This will allow you to set your wallet key via Telegram."
echo "======================================"

# Make script executable
chmod +x telegram_setup_wallet.py

# Run the Python script
python telegram_setup_wallet.py

# Notify user if the script exits
echo "======================================"
echo "Bot stopped. If you set your wallet key successfully,"
echo "you can now start the bot with ./start_secure.sh"
echo "======================================"

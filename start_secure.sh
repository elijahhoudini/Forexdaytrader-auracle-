#!/bin/bash
# start_secure.sh - Start the AURACLE bot with secure wallet configuration
# Created: July 17, 2025

# Check if wallet is configured
if [ -z "$WALLET_PRIVATE_KEY" ]; then
    echo "❌ Error: Wallet key not found in environment variables"
    echo "Please run ./setup_wallet.sh first to securely set your wallet key"
    exit 1
fi

echo "===================================="
echo "🚀 Starting AURACLE Trading Bot 🚀"
echo "===================================="
echo "✅ Wallet key found in environment"
echo "🔍 Starting bot in live mode..."
echo "===================================="

# Run the bot
python start.py

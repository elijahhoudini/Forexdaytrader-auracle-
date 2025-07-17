#!/bin/bash
# start_secure.sh - Start the AURACLE bot with secure wallet configuration
# Created: July 17, 2025

# Check if wallet is configured
if [ -z "$WALLET_PRIVATE_KEY" ]; then
    echo "❌ Error: Wallet key not found in environment variables"
    echo "You can set your wallet key using one of these methods:"
    echo "1. Run ./setup_wallet.sh to set your key in the terminal"
    echo "2. Run ./start_telegram_wallet.sh to set your key via Telegram"
    echo ""
    echo "Which method would you like to use? (1/2): "
    read method_choice
    
    if [ "$method_choice" = "1" ]; then
        ./setup_wallet.sh
        # Check if the setup was successful
        if [ -z "$WALLET_PRIVATE_KEY" ]; then
            echo "❌ Wallet setup failed. Please try again."
            exit 1
        fi
    elif [ "$method_choice" = "2" ]; then
        echo "Starting Telegram setup. Please check your Telegram bot."
        echo "After setting the key, restart this script."
        ./start_telegram_wallet.sh
        exit 0
    else
        echo "❌ Invalid choice. Please run this script again."
        exit 1
    fi
fi

echo "===================================="
echo "🚀 Starting AURACLE Trading Bot 🚀"
echo "===================================="
echo "✅ Wallet key found in environment"
echo "🔍 Starting bot in live mode..."
echo "===================================="

# Run the bot
python start.py

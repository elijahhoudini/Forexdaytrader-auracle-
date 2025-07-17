#!/bin/bash
# Start live trading without Telegram integration
# Created: July 17, 2025

echo "======================================"
echo "🚀 AURACLE Live Trading Starter 🚀"
echo "======================================"
echo "This script starts AURACLE in live trading mode"
echo "without using the Telegram integration."
echo "======================================"

# Make sure we're in demo mode until explicitly enabled
export DEMO_MODE=true

# Ask for wallet key if not set
if [ -z "$WALLET_PRIVATE_KEY" ]; then
    echo ""
    echo "🔐 Wallet Setup"
    echo "----------------"
    read -s -p "Enter your wallet private key: " WALLET_PRIVATE_KEY
    echo ""
    
    if [ -z "$WALLET_PRIVATE_KEY" ]; then
        echo "❌ No private key provided. Exiting."
        exit 1
    fi
    
    # Export the key for this session
    export WALLET_PRIVATE_KEY
    
    echo "✅ Private key set for this session"
    echo ""
fi

# Ask if they really want to enable live trading
echo ""
echo "⚠️ LIVE TRADING CONFIRMATION ⚠️"
echo "-------------------------------"
echo "Live trading involves real money and carries financial risk."
echo ""

read -p "Enable live trading with real transactions? (yes/no): " CONFIRM_LIVE

if [[ "$CONFIRM_LIVE" != "yes" ]]; then
    echo ""
    echo "❌ Live trading not confirmed. Starting in demo mode."
    export DEMO_MODE=true
else
    echo ""
    echo "✅ Live trading confirmed. DEMO_MODE=false"
    export DEMO_MODE=false
    
    # Additional safety settings for live mode
    echo "Setting safety limits for live trading:"
    echo " - Maximum buy amount: 0.05 SOL"
    echo " - Maximum daily trades: 10"
    echo " - Maximum open positions: 3"
    export MAX_BUY_AMOUNT_SOL=0.05
    export MAX_DAILY_TRADES=10
    export MAX_OPEN_POSITIONS=3
    export PROFIT_TARGET_PERCENTAGE=0.15
    export STOP_LOSS_PERCENTAGE=-0.05
fi

# Set required environment variables
export AUTONOMOUS_MODE=true
export USE_AI_TRADING=true
export DISABLE_SNIPER=true
export PROFIT_ONLY_MODE=true

# Start the trading bot
echo ""
echo "Starting AURACLE Trading Bot..."
echo "======================================"
python start.py


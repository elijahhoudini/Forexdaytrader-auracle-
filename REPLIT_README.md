# AURACLE Bot - Replit Deployment Guide

🚀 **One-Click Deployment on Replit**

## Quick Start

1. **Import this repository** to your Replit account
2. **Click "Run"** - The bot will start automatically in safe demo mode
3. **Done!** - Your bot is now running with full functionality

## Features Working Out of the Box

✅ **Trade Logic**: Automated buy/sell with dynamic allocation
✅ **AI Logic**: Token filtering and risk assessment 
✅ **Telegram Integration**: Offline-capable with graceful error handling
✅ **Trade Execution**: Demo trading with realistic simulation
✅ **Position Management**: Stop loss, take profit, and position monitoring
✅ **Network Resilience**: Works offline with demo tokens

## Default Configuration (Safe for Testing)

```
Demo Mode: ✅ Enabled (No real money at risk)
Max Buy Amount: 0.01 SOL per trade
Profit Target: 15%
Stop Loss: -8%
Scan Interval: 45 seconds
Max Positions: 10
Max Daily Trades: 50
```

## What You'll See

The bot will:
- Start in demo mode with realistic token simulation
- Show token discovery and AI filtering
- Execute demo trades with position tracking
- Monitor positions for profit/loss targets
- Handle network errors gracefully
- Display trading statistics and performance

## Sample Output

```
🚀 INITIALIZING AURACLE v1.0.0
👤 Traveler ID: 5798
🤖 Mode: Autonomous
📊 Trading: 🔶 DEMO MODE (Safe - No real trades)

[scanner] Generated 5 demo tokens for testing
[AI] ✅ LIGHT passed AI filters - L:$20749 V:$8869 H:99 PC:6.2%
📈 High confidence trade detected: LIGHT - Allocating 0.015 SOL
🔶 DEMO BUY: LIGHT - 0.015 SOL
[trade] ✅ Successfully bought LIGHT for 0.015 SOL

📊 LIGHT: +3.96% (Age: 0m)
🎯 Take profit triggered for LIGHT: 15.2%
✅ Sold LIGHT - P&L: 15.2%
```

## Going Live (Optional)

To enable real trading, add these environment variables in Replit:

```
DEMO_MODE=false
WALLET_ADDRESS=your_wallet_address
WALLET_PRIVATE_KEY=your_private_key
SOLANA_RPC_ENDPOINT=https://api.mainnet-beta.solana.com
```

## Telegram Integration (Optional)

To enable Telegram notifications:

```
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

## Performance

The bot is optimized for Replit with:
- Efficient resource usage
- Graceful error handling
- Offline capability
- Minimal external dependencies
- Real-time position monitoring

## Safety Features

- **Demo Mode Default**: Always starts safely
- **Position Limits**: Maximum 10 concurrent positions
- **Daily Limits**: Maximum 50 trades per day
- **Stop Loss**: -8% automatic loss protection
- **Take Profit**: 15% automatic profit taking
- **Network Resilience**: Works without internet

## Troubleshooting

**Bot not starting?**
- Make sure all requirements are installed
- Check the console for error messages

**No trades happening?**
- Bot may have hit position limits (normal behavior)
- Check if demo tokens meet trading criteria

**Telegram not working?**
- Network issues are handled gracefully
- Bot continues trading without Telegram

## Support

The bot is fully self-contained and handles all common errors automatically. It's designed to run continuously on Replit without intervention.

---

**Ready to run? Just click the "Run" button in Replit!**
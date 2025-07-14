# AURACLE Bot - Replit Deployment

🚀 **One-Click Deployment: Import → Run → Done!**

## Quick Start

1. **Import this repository** to your Replit account
2. **Click "Run"** - The bot starts automatically in safe demo mode
3. **Done!** - Your bot is now running with full AI and trading functionality

## What You Get

✅ **AI Logic**: Token filtering and risk assessment working immediately  
✅ **Trading Logic**: Automated buy/sell with dynamic allocation  
✅ **Demo Mode**: Safe testing with no real money at risk  
✅ **Position Management**: Stop loss, take profit, and position monitoring  
✅ **Comprehensive Logging**: All trades and system events tracked  

## Sample Output

```
🚀 AURACLE v1.0.0 - Unified Entry Point
👤 Traveler ID: 5798
📊 Trading: 🔶 DEMO MODE (Safe)

🔄 SCAN CYCLE #1
🔍 Found 2 tokens to analyze
📊 $LIGHT: APPROVED (Score: 6/8)
✅ AURACLE APPROVES: $LIGHT
💰 BUY EXECUTED: $LIGHT - 0.01 SOL
📊 $LIGHT: +15.2% (Target reached)
💰 SELL EXECUTED: $LIGHT - Profit: 15.2%
```

## Going Live (Optional)

To enable real trading, add these secrets in Replit:

**Required for live trading:**
- `WALLET_PRIVATE_KEY` - Your Solana wallet private key
- `DEMO_MODE=false` - Enable live trading

**Optional for enhanced features:**
- `TELEGRAM_BOT_TOKEN` - For notifications and control
- `TELEGRAM_CHAT_ID` - For enhanced Telegram features
- `PURCHASED_RPC` - For faster RPC performance
- `MORALIS_API_KEY` - For enhanced token metadata

⚠️ **WARNING: Only enable live trading after testing in demo mode!**

## Features

- **Demo Mode Default**: Always starts safely
- **Max Buy Amount**: 0.01 SOL per trade (configurable)
- **Profit Target**: 15% (configurable)
- **Stop Loss**: -8% (configurable)
- **Scan Interval**: 45 seconds (configurable)
- **Max Positions**: 10 (configurable)
- **Max Daily Trades**: 50 (configurable)

## Safety Features

- **Demo Mode**: No real money at risk by default
- **Position Limits**: Maximum concurrent positions
- **Daily Limits**: Maximum daily trading volume
- **Stop Loss Protection**: Automatic loss prevention
- **Fraud Detection**: AI-powered risk assessment
- **Network Resilience**: Works offline with demo tokens

## Troubleshooting

**Bot not starting?**
- Dependencies auto-install on first run in Replit
- Check console for any error messages

**Want to see more output?**
- Bot runs continuously with real-time updates
- Check `data/` directory for detailed logs

**Ready to go live?**
- Test thoroughly in demo mode first
- Add wallet private key in Replit secrets
- Set `DEMO_MODE=false` when ready

---

**Ready to run? Just click the "Run" button in Replit!**

*All AI logic and trading functions are preserved and fully functional*


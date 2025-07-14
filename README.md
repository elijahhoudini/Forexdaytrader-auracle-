# AURACLE - AI Solana Trading Bot

🤖 **AURACLE** is an autonomous AI-powered Solana trading bot with intelligent token discovery, risk assessment, and automated trading execution.

## 🚀 Quick Start (Replit)

**Import → Run → (Add secrets for live trading)**

1. **Import this repository** to Replit
2. **Click "Run"** - The bot starts automatically in safe demo mode
3. **Done!** Your bot is running with full AI and trading functionality

## 📊 What You Get Out of the Box

✅ **AI Token Discovery**: Automated scanning and filtering  
✅ **Risk Assessment**: Multi-layered fraud detection and safety  
✅ **Automated Trading**: Smart buy/sell with stop-loss/take-profit  
✅ **Position Management**: Real-time monitoring and portfolio tracking  
✅ **Demo Mode**: Safe testing with no real money at risk  
✅ **Comprehensive Logging**: Detailed trade and performance tracking  

## 🔧 Configuration

### Demo Mode (Default - Safe)
No setup required. The bot runs in demo mode by default:
- Simulated trades with realistic tokens
- No real money at risk
- All AI and trading logic fully functional
- Perfect for testing and learning

### Live Trading (Optional)
To enable real trading, add these secrets in Replit:

**Required:**
- `WALLET_PRIVATE_KEY` - Your Solana wallet private key
- `DEMO_MODE=false` - Enable live trading

**Optional:**
- `TELEGRAM_BOT_TOKEN` - For notifications and control
- `TELEGRAM_CHAT_ID` - For enhanced Telegram features
- `PURCHASED_RPC` - For faster RPC performance
- `MORALIS_API_KEY` - For enhanced token metadata

## 🎯 Features

### AI & Trading
- **Autonomous Operation**: Fully automated trading with minimal intervention
- **Smart Token Discovery**: Multi-DEX scanning for new opportunities
- **Risk Management**: Advanced fraud detection and safety mechanisms
- **Dynamic Allocation**: Intelligent position sizing based on confidence
- **Portfolio Optimization**: Automated profit/loss management

### Safety & Security
- **Demo Mode Default**: Always starts safely
- **Position Limits**: Maximum concurrent positions and daily trades
- **Stop Loss Protection**: Automatic loss prevention
- **Blacklist Management**: Suspicious token filtering
- **Real-time Monitoring**: Continuous risk assessment

### Telegram Integration (Optional)
- **Trade Notifications**: Real-time alerts for all trades
- **Bot Control**: Start/stop and mode switching
- **Performance Monitoring**: Live statistics and portfolio updates
- **Error Alerts**: Immediate notification of issues

## 📈 Sample Output

```
🚀 AURACLE v1.0.0 - Unified Entry Point
👤 Traveler ID: 5798
📊 Trading mode: 🔶 DEMO MODE (Safe)

🔄 SCAN CYCLE #1
🔍 Found 2 tokens to analyze
📊 $LIGHT: APPROVED (Score: 6/8)
✅ AURACLE APPROVES: $LIGHT
💰 BUY EXECUTED: $LIGHT - 0.01 SOL
📊 $LIGHT: +15.2% (Target reached)
💰 SELL EXECUTED: $LIGHT - Profit: 15.2%
```

## ⚠️ Important Notes

- **Demo Mode**: Always enabled by default for maximum safety
- **Real Trading**: Only enable after thorough testing in demo mode
- **Risk Management**: Never invest more than you can afford to lose
- **Monitoring**: Always monitor bot performance and market conditions

## 🔧 Local Development

For local development, see [README_LOCAL.md](README_LOCAL.md)

## 📞 Support

- Create an issue on GitHub for bugs or questions
- Check logs in the `data/` directory for troubleshooting
- All core AI and trading logic is preserved and fully functional

---

**Built for Traveler 5798** - *"Autonomous intelligence, infinite possibilities"*

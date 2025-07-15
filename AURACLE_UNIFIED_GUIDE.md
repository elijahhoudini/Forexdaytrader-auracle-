# AURACLE Unified Telegram Bot - Usage Guide

## Overview
The AURACLE Unified Telegram Bot combines all AURACLE trading intelligence into a single Telegram interface. Now you can control all trading operations, monitoring, and settings directly from Telegram.

## Quick Start

### 1. Start the Bot
```bash
python start_unified.py
```
or
```bash
python main.py
```

### 2. Open Telegram
- Start a chat with your bot
- Use `/start` to initialize

### 3. Start AURACLE
- Use `/start_auracle` to begin AI trading
- Monitor with `/status`
- Stop with `/stop_auracle`

## Commands Overview

### 🎯 Core AURACLE Commands
- `/start_auracle` - Start AURACLE trading intelligence
- `/stop_auracle` - Stop AURACLE trading intelligence
- `/status` - Show comprehensive system status
- `/scan` - Force immediate token scan
- `/trade <token> <amount>` - Execute manual trade
- `/positions` - Show current trading positions
- `/settings` - Configure trading parameters

### 💼 Wallet Management
- `/wallet` - Show wallet information and balance
- `/generate_wallet` - Generate new wallet
- `/connect_wallet` - Connect existing wallet

### ⚡ Quick Trading
- `/start_sniper` - Start sniper mode for quick trades
- `/stop_sniper` - Stop sniper mode
- `/snipe <amount>` - Execute quick snipe trade

### 🎁 Referral System
- `/referral` - Get your referral code
- `/claim` - Claim referral rewards
- `/qr` - Generate QR code for sharing

### 📚 Information
- `/help` - Show all available commands
- `/start` - Show welcome message and quick actions

## Usage Examples

### Starting AURACLE
```
/start_auracle
```
Response:
```
✅ AURACLE Trading Intelligence Started!

🤖 Status: Active
👤 Traveler ID: 5798
💰 Wallet: Emac86gt...
📊 Mode: Autonomous Trading

Use /status to monitor progress
Use /stop_auracle to stop
```

### Manual Trading
```
/trade EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v 0.01
```
Response:
```
✅ Trade executed successfully!

📊 Transaction: a7b3c9d2...
💰 Amount: 0.01 SOL
🎯 Token: EPjFWdd5...
⚡ Status: Completed
```

### Checking Status
```
/status
```
Response:
```
📊 AURACLE Status Report

🤖 AURACLE: 🟢 Active
💰 Balance: 0.5432 SOL
📈 Total Trades: 15
💵 Total Profit: 0.0842 SOL

🔍 Scans: 247
🎯 Evaluations: 58
⚡ Trades: 15
⏰ Uptime: 2:34:12
```

### Configuring Settings
```
/settings
```
This opens an interactive menu to configure:
- 💰 Max Buy Amount per trade
- 🎯 Profit Target percentage
- 🛑 Stop Loss percentage
- 🤖 Auto Trade on/off

## Key Features

### 1. Autonomous Trading
- AURACLE scans for tokens automatically
- Uses advanced AI to evaluate opportunities
- Executes trades based on your settings
- Monitors positions and manages risk

### 2. Real-time Control
- Start/stop trading from anywhere
- Monitor performance in real-time
- Execute manual trades when needed
- Adjust settings on the fly

### 3. Intelligent Risk Management
- Automatic stop-loss protection
- Position sizing based on risk
- Fraud detection and avoidance
- Liquidity analysis before trades

### 4. Comprehensive Monitoring
- Track all trades and performance
- Real-time balance updates
- Detailed transaction history
- Performance analytics

## Safety Features

### 1. Two-Factor Control
- Bot requires explicit `/start_auracle` command
- Can be stopped instantly with `/stop_auracle`
- No trading without your permission

### 2. Configurable Limits
- Set maximum buy amounts
- Configure profit targets
- Set stop-loss percentages
- Enable/disable auto trading

### 3. Real-time Alerts
- Immediate notification of all trades
- Error alerts and warnings
- Performance updates
- System status changes

## Configuration

### Environment Variables
Set these in your environment or config.py:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id
WALLET_ADDRESS=your_wallet_address
WALLET_PRIVATE_KEY=your_private_key
```

### Trading Parameters
Default settings (adjustable via `/settings`):
- Max Buy Amount: 0.01 SOL
- Profit Target: 20%
- Stop Loss: 5%
- Auto Trade: OFF (manual approval required)

## Troubleshooting

### Bot Not Responding
1. Check bot token is valid
2. Ensure bot is running: `python start_unified.py`
3. Verify chat ID is correct
4. Check internet connection

### Trading Not Working
1. Verify wallet is connected
2. Check SOL balance is sufficient
3. Ensure AURACLE is started with `/start_auracle`
4. Check network status

### Performance Issues
1. Restart bot if needed
2. Check system resources
3. Review error logs
4. Use `/status` to check system health

## Support

For issues or questions:
1. Use `/help` for command reference
2. Check system status with `/status`
3. Review this guide
4. Contact support team

## Best Practices

1. **Start Small**: Begin with small amounts to test the system
2. **Monitor Actively**: Keep an eye on performance and adjust settings
3. **Use Stop Losses**: Always set appropriate stop-loss levels
4. **Stay Informed**: Monitor market conditions and news
5. **Keep Secure**: Never share your private keys or bot tokens

## Advanced Usage

### Automated Trading Flow
1. Set up wallet and configure settings
2. Start AURACLE with `/start_auracle`
3. Monitor with periodic `/status` checks
4. Adjust settings as needed
5. Stop when desired with `/stop_auracle`

### Manual Override
Even with auto-trading enabled, you can:
- Execute manual trades with `/trade`
- Force scans with `/scan`
- Check positions with `/positions`
- Modify settings with `/settings`

## Security Notes

- Bot runs locally - your keys never leave your system
- All trades are executed from your wallet
- You have full control to start/stop at any time
- No third-party access to your funds

---

**Remember**: Trading cryptocurrency involves risk. Start with small amounts and never trade more than you can afford to lose.

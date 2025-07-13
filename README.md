# AURACLE: Autonomous AI Solana Trading Bot

🤖 **AURACLE** is an autonomous AI-powered Solana trading bot designed for Traveler 5798. It features automated token discovery, risk assessment, and intelligent trading execution on the Solana blockchain.

## 🎯 Features

### Core Functionality
- **Autonomous Trading**: Fully automated buy/sell operations with configurable parameters
- **Token Discovery**: Multi-DEX scanning for new tokens and trading opportunities
- **Risk Management**: Advanced fraud detection and safety mechanisms
- **Portfolio Management**: Automated position monitoring with profit targets and stop losses
- **Comprehensive Logging**: Detailed trade, error, and performance logging
- **Telegram Integration**: Live mode control and trade notifications via Telegram

### Safety Features
- **Demo Mode**: Safe trading simulation (enabled by default)
- **Blacklist Management**: Permanent and temporary token blacklisting
- **Fraud Detection**: Pattern-based suspicious token identification
- **Risk Assessment**: Multi-factor risk evaluation for each trade
- **Position Limits**: Configurable maximum positions and daily trade limits
- **Stop Loss Protection**: Automated loss prevention mechanisms

### Telegram Bot Features
- **Demo Mode Toggle**: Switch between demo and live trading via `/demo` and `/live` commands
- **Real-time Status**: Monitor bot performance and wallet balance with `/status`
- **Configuration View**: Check current settings with `/config`
- **Trade Notifications**: Receive instant alerts for all trades
- **Safe by Default**: Always starts in demo mode for maximum safety

## 🏗️ Architecture

### Modular Design
```
auracle.py          # Main system controller and trading loop
├── wallet.py       # Wallet interface and transaction signing
├── trade.py        # Trade execution engine and position management
├── scanner.py      # Token discovery and opportunity detection
├── risk.py         # Risk assessment and fraud detection
├── logger.py       # Comprehensive logging system
├── config.py       # Global configuration and constants
└── data/           # Log files and data storage
    ├── trade_logs.json
    ├── error_logs.json
    ├── system_logs.json
    └── performance_logs.json
```

## 🚀 Quick Start

### For Replit (Recommended - One-Click Setup)

1. **Copy this repository to Replit**
   - Fork or import this repository to your Replit account
   - That's it! Click the "Run" button to start the bot

2. **Optional: Configure Telegram control**
   - Go to "Secrets" tab in Replit
   - Add your Telegram bot configuration:
     ```
     TELEGRAM_ENABLED=true
     TELEGRAM_BOT_TOKEN=your_bot_token
     TELEGRAM_CHAT_ID=your_chat_id
     ```

3. **Optional: Configure for live trading**
   - Use Telegram commands to control the bot:
     - `/demo` - Switch to safe demo mode
     - `/live` - Switch to live trading mode
     - `/status` - Check bot status
     - `/config` - View configuration
   - Or configure via Replit Secrets:
     ```
     WALLET_ADDRESS=your_wallet_address
     SOLANA_RPC_ENDPOINT=https://api.mainnet-beta.solana.com
     DEMO_MODE=false
     ```

### For Local Development

**Prerequisites:**
- Python 3.10 or higher (Python 3.11+ recommended for best compatibility)

1. **Clone the repository**
   ```bash
   git clone https://github.com/elijahhoudini/Main-bot.git
   cd Main-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the bot**
   ```bash
   python3 start.py
   ```

### Default Configuration

The bot runs in **safe demo mode** by default with these settings:
- Demo wallet (no real trading)
- Minimum trade amounts (0.01 SOL per trade)
- 60-second scan intervals
- All safety features enabled

This allows you to test the bot immediately without any setup!

## 🤖 Telegram Bot Controls

### Commands

| Command | Description |
|---------|-------------|
| `/start` | Show main control panel |
| `/demo` | Enable safe demo mode (no real trades) |
| `/live` | Enable live trading mode (⚠️ real money) |
| `/status` | Show current bot status and performance |
| `/config` | Display current configuration |
| `/help` | Show all available commands |

### Trading Mode Control

- **Demo Mode** 🔶: Safe trading simulation, no real money at risk
- **Live Mode** 🔥: Real trading with actual funds (requires confirmation)

The bot **always starts in demo mode** for maximum safety. Use the `/live` command to enable real trading when you're ready.

## ⚙️ Configuration

### Default Settings (Safe Demo Mode)

```python
# Trading Parameters
MAX_BUY_AMOUNT_SOL = 0.01             # Minimum trade amount: 0.01 SOL per trade
PROFIT_TARGET_PERCENTAGE = 0.20      # 20% profit target
STOP_LOSS_PERCENTAGE = -0.05         # -5% stop loss to limit losses
SCAN_INTERVAL_SECONDS = 60           # 1 minute between scans

# Safety Settings
DEMO_MODE = True                     # Safe demo mode by default
AUTONOMOUS_MODE = True               # Fully automated
ENABLE_FRAUD_DETECTION = True        # Advanced safety checks
MAX_DAILY_TRADES = 50                # Daily trade limit
MAX_OPEN_POSITIONS = 10              # Concurrent positions limit
```

### Customization via Environment Variables

You can override any setting using environment variables:

```bash
# Trading amounts
export MAX_BUY_AMOUNT_SOL=0.01
export MIN_LIQUIDITY_THRESHOLD=1000

# Trading strategy
export PROFIT_TARGET_PERCENTAGE=0.15
export STOP_LOSS_PERCENTAGE=-0.05
export SCAN_INTERVAL_SECONDS=30

# Safety settings
export DEMO_MODE=false
export MAX_DAILY_TRADES=100
```

## 🔧 Replit Deployment

### One-Click Setup
1. **Import repository** - Fork or import this repo to Replit
2. **Click "Run"** - The bot will start automatically in safe demo mode
3. **Done!** - The bot is now running with all safety features enabled

### Going Live (Optional)
To enable real trading, add these secrets in Replit:
- `WALLET_ADDRESS` - Your Solana wallet public key
- `WALLET_PRIVATE_KEY` - Your wallet private key (keep secure!)
- `DEMO_MODE` - Set to `false` to enable live trading
- `MAX_BUY_AMOUNT_SOL` - Maximum SOL per trade (default: 0.01)
- `SOLANA_RPC_ENDPOINT` - Solana RPC endpoint (default: mainnet-beta)
- `TELEGRAM_BOT_TOKEN` - Optional Telegram notifications
- `TELEGRAM_CHAT_ID` - Telegram chat ID for notifications
- `SCAN_INTERVAL_SECONDS` - Time between scans (default: 60)
- `PROFIT_TARGET_PERCENTAGE` - Profit target (default: 0.20 = 20%)
- `STOP_LOSS_PERCENTAGE` - Stop loss (default: -0.05 = -5%)

## 📊 Monitoring & Logging

### Log Files
- **`data/trade_logs.json`**: All trading activities
- **`data/error_logs.json`**: System errors and exceptions
- **`data/system_logs.json`**: System events and status
- **`data/performance_logs.json`**: Performance metrics
- **`data/flag_logs.json`**: Risk flags and suspicious activities

### Console Output
```
🚀 INITIALIZING AURACLE v1.0.0
👤 Traveler ID: 5798
🤖 Mode: Autonomous
============================================================
[WALLET] Wallet initialized successfully
[SCANNER] Initialized with 4 DEX sources
[RISK] Risk evaluator initialized - Safety checks: True
[SYSTEM] AURACLE Logger initialized
[AURACLE] 🔄 Starting autonomous trading loop
[AURACLE] 📊 Scan #1: 3 tokens found
[AURACLE] ✅ Successfully bought TOKEN1 with 0.01 SOL
[TRADE] 🎯 Selling TOKEN1 — profit_target — P&L: 22.34%
```

## 🛡️ Security & Risk Management

### Built-in Protections
- **Blacklist System**: Automatic and manual token blocking
- **Fraud Detection**: AI-powered suspicious pattern recognition
- **Liquidity Validation**: Minimum liquidity requirements
- **Position Limits**: Maximum concurrent positions
- **Daily Limits**: Maximum daily trading volume
- **Stop Loss**: Automatic loss prevention

### Risk Assessment Criteria
- Token liquidity levels
- Holder distribution
- Volume/liquidity ratios
- Price volatility patterns
- Token age and verification status
- Historical fraud patterns

## 🎛️ Advanced Features

### Performance Monitoring
- Real-time trade success rates
- Portfolio value tracking
- Risk utilization metrics
- Scanning efficiency statistics

### Telegram Integration (Optional)
- Trade notifications
- Error alerts
- Performance summaries
- Manual override commands

### Backtesting Mode
```python
BACKTESTING_MODE = True  # Enable historical testing
```

## 🔄 Maintenance

### Log Rotation
- Automatic log rotation when files exceed 10MB
- Timestamped archived logs
- Configurable retention policies

### Health Checks
- Wallet connectivity monitoring
- RPC endpoint validation
- Memory usage tracking
- Error rate monitoring

## 🐛 Troubleshooting

### Common Issues
1. **Wallet Connection Failed**
   - Check wallet address configuration
   - Verify RPC endpoint accessibility
   - Ensure sufficient SOL balance

2. **No Tokens Found**
   - Verify DEX API connectivity
   - Check scan interval settings
   - Review liquidity thresholds

3. **High Error Rate**
   - Monitor RPC rate limits
   - Check network connectivity
   - Review system resources

### Debug Mode
```python
LOG_LEVEL = "DEBUG"  # Enable detailed logging
```

## 📋 System Requirements

### Minimum Requirements
- **Python**: 3.10 or higher
- **CPU**: 1 core, 2.0 GHz
- **RAM**: 512 MB
- **Storage**: 1 GB free space
- **Network**: Stable internet connection

### Recommended Requirements
- **Python**: 3.11 or higher (for best compatibility with all dependencies)
- **CPU**: 2+ cores, 2.5+ GHz
- **RAM**: 1+ GB
- **Storage**: 5+ GB free space
- **Network**: Low-latency connection

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Add comprehensive docstrings
- Include type hints
- Write unit tests

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

**IMPORTANT**: This trading bot is for educational and research purposes. Cryptocurrency trading involves significant risk of financial loss. Use at your own risk and never invest more than you can afford to lose.

- Not financial advice
- Past performance doesn't guarantee future results
- Always test thoroughly before live trading
- Monitor bot performance regularly

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Join the community discussion
- Check the troubleshooting guide

---

**Built with ❤️ for Traveler 5798**

*"Autonomous intelligence, infinite possibilities"*

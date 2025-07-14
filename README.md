# AURACLE + Solana Trading Bot: Unified Trading Platform

🤖 **AURACLE** is an autonomous AI-powered Solana trading bot with an integrated Telegram-based Solana Trading Bot. This unified platform combines automated token discovery, risk assessment, and intelligent trading execution on the Solana blockchain with comprehensive Telegram-based controls.

## 🎯 Two Bot Modes

### 1. AURACLE Bot (Autonomous Mode)
- **Fully Autonomous**: Automated trading with minimal user intervention
- **AI-Powered**: Intelligent token discovery and risk assessment
- **Advanced Risk Management**: Multi-layered fraud detection and safety mechanisms

### 2. Solana Trading Bot (Telegram Mode)
- **Telegram Interface**: Full bot control via Telegram commands
- **Multi-DEX Trading**: Buy and sell across multiple Solana DEXs
- **Advanced Features**: Sniping, limit orders, portfolio tracking, and more
- **User-Controlled**: Manual trading decisions with bot assistance

## 🎯 Features

### AURACLE Bot Features
- **Autonomous Trading**: Fully automated buy/sell operations with configurable parameters
- **Token Discovery**: Multi-DEX scanning for new tokens and trading opportunities
- **Risk Management**: Advanced fraud detection and safety mechanisms
- **Portfolio Management**: Automated position monitoring with profit targets and stop losses
- **Comprehensive Logging**: Detailed trade, error, and performance logging
- **Telegram Integration**: Live mode control and trade notifications via Telegram

### Solana Trading Bot Features
- **Telegram Interface**: Complete bot control via Telegram commands
- **Sniping Features**: Automatically monitor and execute trades on newly listed tokens
- **Multi-DEX Trading**: Buy and sell tokens across multiple decentralized exchanges
- **Limit Orders**: Set custom buy/sell price limits for automated execution
- **Portfolio Management**: Track wallet portfolio with real-time updates
- **Referral System**: Built-in referral system for user engagement
- **Token Watchlist**: Create and maintain watchlists to monitor price changes

### Safety Features (Both Bots)
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

### Unified Architecture
```
start_unified.py     # Main entry point - choose which bot to run
├── AURACLE Bot/
│   ├── auracle.py          # Main system controller and trading loop
│   ├── wallet.py           # Wallet interface and transaction signing
│   ├── trade.py            # Trade execution engine and position management
│   ├── scanner.py          # Token discovery and opportunity detection
│   ├── risk.py             # Risk assessment and fraud detection
│   ├── logger.py           # Comprehensive logging system
│   └── config.py           # Global configuration and constants
├── Solana Trading Bot/
│   └── src/solbot/
│       ├── main.py         # Telegram bot main controller
│       ├── callback_handlers/  # Telegram callback handlers
│       ├── command_handlers/   # Telegram command handlers
│       ├── message_handlers/   # Telegram message handlers
│       ├── web3/              # Web3 and blockchain interactions
│       ├── database/          # Database operations
│       └── utils/             # Utility functions
└── data/                   # Log files and data storage
    ├── trade_logs.json
    ├── error_logs.json
    ├── system_logs.json
    └── performance_logs.json
```

## 🚀 Quick Start (Streamlined Setup)

### Minimal Requirements
The repository has been streamlined to require **only two essential components**:

1. **WALLET_PRIVATE_KEY** - Your Solana wallet private key for trading
2. **TELEGRAM_BOT_TOKEN** - Your Telegram bot token for the interface

### One-Click Setup
1. **Copy this repository to Replit** or clone locally
2. **Create a `.env` file** with minimal configuration:
   ```env
   WALLET_PRIVATE_KEY=your_solana_private_key_here
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   DEMO_MODE=true
   ```
3. **Run the bot**:
   ```bash
   # Install dependencies (if running locally)
   pip install -r requirements.txt
   
   # Run Telegram bot
   python start_unified.py --bot solbot
   
   # Run AURACLE bot (autonomous)
   python start_unified.py --bot auracle
   ```

### What's Removed ✅
- **Database dependency** - Uses file-based storage automatically
- **Moralis API requirement** - Uses free Jupiter/Solana APIs
- **Premium RPC requirement** - Falls back to free public endpoints
- **Complex setup** - Works out of the box with minimal configuration

### Enhanced Features (Optional)
All other configuration is now **optional** with sensible defaults:
- `TELEGRAM_CHAT_ID` - Enhances Telegram features
- `PURCHASED_RPC` - For faster RPC performance
- `MORALIS_API_KEY` - For enhanced token metadata
- `DATABASE_URI` - For persistent storage across restarts

See [STREAMLINED_SETUP.md](STREAMLINED_SETUP.md) for detailed setup instructions.

### For Local Development

**Prerequisites:**
- Python 3.10 or higher (Python 3.11+ recommended for best compatibility)

1. **Clone the repository**
   ```bash
   git clone https://github.com/elijahhoudini/Final-.git
   cd Final-
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the bot**
   ```bash
   # Run AURACLE bot (autonomous)
   python start_unified.py --bot auracle
   
   # Run Solana Trading Bot (Telegram)
   python start_unified.py --bot solbot
   
   # Default (AURACLE)
   python start_unified.py
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

## ⚙️ Configuration (Streamlined)

### Required Configuration
```env
WALLET_PRIVATE_KEY=your_solana_private_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
DEMO_MODE=true  # Keep enabled for testing
```

### Optional Configuration
All other settings have sensible defaults and are optional:

```env
# Enhanced Telegram features
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
TELEGRAM_ENABLED=true

# Premium services (will use free alternatives otherwise)
PURCHASED_RPC=your_premium_rpc_endpoint
MORALIS_API_KEY=your_moralis_api_key
DATABASE_URI=your_postgresql_connection_string

# Trading parameters (has defaults)
MAX_BUY_AMOUNT_SOL=0.01
PROFIT_TARGET_PERCENTAGE=0.20
STOP_LOSS_PERCENTAGE=-0.05
SCAN_INTERVAL_SECONDS=60
MAX_DAILY_TRADES=50
MAX_OPEN_POSITIONS=10
```

### Automatic Fallbacks
- **No database?** → Uses file-based storage in `data/storage/`
- **No Moralis API?** → Uses free Jupiter/Solana APIs
- **No premium RPC?** → Uses free public RPC endpoints
- **Missing config?** → Uses conservative defaults

### File Storage
When using file storage (default), data is stored in:
- `data/storage/priv_keys.json` - Encrypted private keys
- `data/storage/orders.json` - Trading orders
- `data/storage/watchlists.json` - Token watchlists
- `data/storage/strategies.json` - Trading strategies
- And more...

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

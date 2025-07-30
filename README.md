# AURACLE Forex Trading Bot: Autonomous Currency Trading Platform

🤖 **AURACLE** is an autonomous AI-powered Forex trading bot designed for professional currency trading. This advanced platform combines real-time market analysis, technical indicators, and intelligent trade execution across major currency pairs with comprehensive risk management and alert systems.

## 🎯 Trading Modes

### 1. Autonomous Mode
- **Fully Autonomous**: Automated Forex trading with minimal user intervention
- **AI-Powered**: Intelligent currency pair analysis and signal generation
- **Advanced Risk Management**: Multi-layered position sizing and safety mechanisms
- **24/5 Operation**: Continuous monitoring during Forex market hours

### 2. Manual/Interactive Mode
- **Telegram Interface**: Full bot control via Telegram commands
- **Manual Execution**: User-controlled trade decisions with AI assistance
- **Real-time Analysis**: Live technical analysis and recommendations
- **Position Management**: Advanced portfolio tracking and management

## 🎯 Local Terminal Features

### ✅ What's New for Forex Trading
- **Forex Market Integration**: Real-time data from Alpha Vantage, Twelve Data, and OANDA APIs
- **Technical Analysis**: Advanced indicators including RSI, MACD, Bollinger Bands, ADX
- **MetaTrader Support**: MT5 integration for professional trading platforms
- **Currency Pairs**: Major pairs (EUR/USD, GBP/USD, USD/JPY, etc.)
- **Risk Management**: Kelly criterion, position sizing, stop losses, take profits
- **Demo Trading**: Safe testing with simulated trades before going live

### ✅ Removed Solana Dependencies
- No more blockchain-specific operations
- No token scanning or wallet management
- No Jupiter aggregator dependencies
- No Solana RPC requirements
- Clean Forex-focused architecture

### ✅ Forex Optimizations
- **Terminal Interface**: Real-time price feeds and position monitoring
- **Local Data Storage**: Historical data and trade logs in `./data/forex/`
- **Environment Configuration**: Forex-specific `.env` setup
- **Error Handling**: Robust API failover and connection management
- **Testing Modes**: Demo, paper trading, and backtesting capabilities

## 🎯 Features

### AURACLE Forex Bot Features
- **Autonomous Forex Trading**: Fully automated buy/sell operations with configurable parameters
- **Currency Pair Analysis**: Real-time analysis of major currency pairs (EUR/USD, GBP/USD, USD/JPY, etc.)
- **Technical Indicators**: RSI, MACD, Bollinger Bands, ADX, Stochastic, Moving Averages
- **Risk Management**: Advanced position sizing, stop losses, take profits, daily loss limits
- **Multiple API Support**: Alpha Vantage, Twelve Data, OANDA with automatic failover
- **MetaTrader Integration**: MT5 support for professional trading platforms
- **Portfolio Management**: Real-time PnL tracking, position monitoring, performance analytics
- **Comprehensive Logging**: Detailed trade logs, performance metrics, and error tracking
- **Telegram Integration**: Live notifications and manual control via Telegram

### Solana Trading Bot Features
- **Telegram Interface**: Complete bot control via Telegram commands
- **Sniping Features**: Automatically monitor and execute trades on newly listed tokens
- **Multi-DEX Trading**: Buy and sell tokens across multiple decentralized exchanges
- **Limit Orders**: Set custom buy/sell price limits for automated execution
- **Portfolio Management**: Track wallet portfolio with real-time updates
- **Referral System**: Built-in referral system for user engagement
- **Token Watchlist**: Create and maintain watchlists to monitor price changes

### Safety Features (Forex Trading)
- **Demo Mode**: Safe trading simulation (enabled by default)
- **Risk Management**: Advanced position sizing and stop losses
- **Daily Loss Limits**: Configurable maximum daily losses
- **Position Limits**: Maximum concurrent positions and trade frequency
- **API Failover**: Multiple data sources for reliability
- **Real-time Monitoring**: Continuous position and PnL tracking

### Forex Bot Features  
- **Real-time Analysis**: Live technical indicator calculations and signal generation
- **Multiple Timeframes**: Support for 1min to daily timeframes
- **Currency Strength**: Advanced currency strength analysis across pairs
- **Economic Calendar**: Integration with economic events and news
- **Performance Tracking**: Detailed trade logs and PnL analysis
- **MetaTrader Integration**: Professional platform connectivity

## 🏗️ Forex Architecture

### AURACLE Forex Architecture
```
start_forex.py         # Main entry point for Forex trading
├── AURACLE Forex Bot/
│   ├── auracle_forex.py      # Main Forex trading controller
│   ├── forex_market_data.py  # Market data from multiple APIs
│   ├── forex_trading_engine.py # Trade execution and position management
│   ├── forex_technical_indicators.py # Technical analysis indicators
│   ├── forex_config.py       # Forex-specific configuration
│   └── logger.py             # Logging system (reused)
├── Legacy Solana Bot/ (DISABLED)
│   └── *.py files            # Original Solana functionality (kept for reference)
└── data/forex/               # Forex-specific data storage
    ├── historical/           # Historical price data
    ├── trades/              # Trade logs and history
    └── performance/         # Performance analytics
```

## 🚀 Quick Start (Forex Trading)

### Setup and Installation

1. **Setup the Forex Bot**:
   ```bash
   python start_forex.py --setup
   ```

2. **Configure API Keys** (Get free keys from):
   ```bash
   # Edit .env file with your credentials:
   ALPHA_VANTAGE_API_KEY=your_free_api_key    # https://www.alphavantage.co/
   TWELVE_DATA_API_KEY=your_free_api_key      # https://twelvedata.com/
   OANDA_API_TOKEN=your_demo_token            # https://oanda.com/
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.forex.txt
   ```

4. **Test the Bot**:
   ```bash
   python start_forex.py --mode test
   ```

### Trading Modes

1. **Interactive Mode** (Recommended for beginners):
   ```bash
   python start_forex.py --mode manual
   # Commands: analyze EURUSD, trade EURUSD long 0.01, status, quit
   ```

2. **Autonomous Mode** (Advanced users):
   ```bash
   python start_forex.py --mode auto
   # Fully automated trading based on technical signals
   ```

### Supported Currency Pairs
- **EUR/USD** - Euro/US Dollar (Most liquid)
- **GBP/USD** - British Pound/US Dollar  
- **USD/JPY** - US Dollar/Japanese Yen
- **USD/CHF** - US Dollar/Swiss Franc
- **AUD/USD** - Australian Dollar/US Dollar
- **USD/CAD** - US Dollar/Canadian Dollar
- **NZD/USD** - New Zealand Dollar/US Dollar

### Key Configuration Options
```bash
# Trading settings
FOREX_DEMO_MODE=true              # Safe demo trading
AUTONOMOUS_TRADING=false          # Manual control
MAX_RISK_PER_TRADE=0.02          # 2% risk per trade
MAX_DAILY_TRADES=10              # Daily trade limit
DAILY_LOSS_LIMIT=200             # $200 daily loss limit

# Technical analysis
SIGNAL_CONFIDENCE_THRESHOLD=60   # Minimum signal strength
PRIMARY_TIMEFRAME=1hour          # Analysis timeframe
RSI_OVERSOLD_THRESHOLD=30        # RSI oversold level
```
python setup_local.py

# Test the bot
python start_local.py --test

# Run the bot
python start_local.py --bot auracle
```

See [README_LOCAL.md](README_LOCAL.md) for detailed local setup instructions.

### For Replit Deployment (Legacy)

**Works on Replit but local setup is recommended**

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
   pip install -r requirements.local.txt
   
   # Run local launcher (recommended)
   python start_local.py --bot auracle
   
   # Or use original launcher
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
- Python 3.8 or higher (Python 3.10+ recommended for best compatibility)

1. **Clone the repository**
   ```bash
   git clone https://github.com/elijahhoudini/Final-.git
   cd Final-
   ```

2. **Quick setup** (Recommended)
   ```bash
   # Run automated setup
   python setup_local.py
   
   # Test the bot
   python start_local.py --test
   
   # Run the bot
   python start_local.py --bot auracle
   ```

3. **Manual setup** (Alternative)
   ```bash
   # Install dependencies
   pip install -r requirements.local.txt
   
   # Copy environment template
   cp .env.local .env
   
   # Edit .env with your configuration
   nano .env
   
   # Run the bot
   python start_local.py --bot auracle
   ```

4. **Using Make** (For developers)
   ```bash
   # Install dependencies and run test
   make install
   make test
   
   # Run the bot
   make run
   ```

See [README_LOCAL.md](README_LOCAL.md) for detailed local setup instructions.

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

## 🔧 Replit Deployment (Legacy)

**⚠️ Note: Local setup is now recommended for better performance and control**

### One-Click Setup
1. **Import repository** - Fork or import this repo to Replit
2. **Click "Run"** - The bot will start automatically in safe demo mode
3. **Done!** - The bot is now running with all safety features enabled

For new users, we recommend using the local setup instead: [README_LOCAL.md](README_LOCAL.md)

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

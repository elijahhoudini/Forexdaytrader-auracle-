# AURACLE Bot - Local Setup Guide

🚀 **AURACLE Bot optimized for local laptop/terminal usage** - No Replit dependencies!

## Quick Start (Local Terminal)

### 1. Prerequisites
- Python 3.8+ (Python 3.10+ recommended)
- Internet connection for blockchain interactions

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/elijahhoudini/Final-.git
cd Final-

# Install dependencies
pip install -r requirements.local.txt

# Or use minimal requirements
pip install -r requirements.minimal.txt
```

### 3. Configuration
```bash
# Copy the local environment template
cp .env.local .env

# Edit .env with your settings (optional for demo mode)
nano .env
```

### 4. Run the Bot
```bash
# Quick test
python start_local.py --test

# Run autonomous bot
python start_local.py --bot auracle

# Run Telegram bot
python start_local.py --bot solbot

# Interactive mode
python start_local.py
```

## Features for Local Use

### ✅ What Works Out of the Box
- **Demo Mode**: Safe trading simulation with no real money
- **File Storage**: No database required - uses local files
- **Free APIs**: Uses public Solana RPC and Jupiter API
- **Local Logging**: All logs stored in `./data/` directory
- **Minimal Dependencies**: Only essential packages required

### ✅ Local Optimizations
- **No Replit Dependencies**: Removed all Replit-specific code
- **Terminal Interface**: Clean terminal output with progress indicators
- **Local Data Storage**: Data persists in `./data/` directory
- **Environment Variables**: Use `.env` file for configuration
- **Error Handling**: Graceful handling of network issues

### ✅ Safe Defaults
- **Demo Mode**: Always starts in safe demo mode
- **Conservative Trading**: Small position sizes (0.01 SOL)
- **Risk Management**: Built-in stop loss and profit targets
- **Telegram Optional**: Can run without Telegram integration

## Configuration

### Required (Live Trading)
```env
WALLET_PRIVATE_KEY=your_solana_private_key_here
DEMO_MODE=false
```

### Optional (Enhanced Features)
```env
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
```

### Safe Demo Mode (Default)
```env
DEMO_MODE=true
TELEGRAM_ENABLED=false
```

## Local File Structure
```
Final-/
├── start_local.py          # Local launcher
├── setup_local.py          # Setup wizard
├── .env.local             # Local config template
├── requirements.local.txt  # Local dependencies
├── data/                  # Local data storage
│   ├── logs/              # Log files
│   ├── storage/           # Trading data
│   └── backups/           # Backup files
└── ... (other files)
```

## Commands

### Basic Usage
```bash
# Test configuration
python start_local.py --test

# Run setup wizard
python start_local.py --setup

# Interactive mode
python start_local.py
```

### Advanced Usage
```bash
# Run with specific bot
python start_local.py --bot auracle
python start_local.py --bot solbot

# Original startup (still works)
python start_unified.py --bot auracle
```

## Local Development

### Setup Development Environment
```bash
# Run setup wizard
python start_local.py --setup

# Or manually
python setup_local.py
```

### Testing
```bash
# Quick test
python start_local.py --test

# Run specific tests
python -m pytest test_*.py
```

### Logs and Data
- **Logs**: `./data/logs/`
- **Trading Data**: `./data/storage/`
- **Configuration**: `.env` file
- **All data persists locally**

## Troubleshooting

### Common Issues

**1. Missing Dependencies**
```bash
pip install -r requirements.local.txt
```

**2. Configuration Errors**
```bash
# Check config
python start_local.py --test

# Use demo mode
echo "DEMO_MODE=true" >> .env
```

**3. Permission Errors**
```bash
# Make scripts executable
chmod +x start_local.py
chmod +x setup_local.py
```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python start_local.py --test
```

## Security Notes

### For Local Usage
- **Always test in demo mode first**
- **Keep private keys secure**
- **Start with small amounts**
- **Monitor performance regularly**

### File Permissions
```bash
# Secure .env file
chmod 600 .env

# Secure private key files
chmod 600 data/storage/priv_keys.json
```

## What's Changed from Replit

### ✅ Removed
- Replit-specific startup scripts
- Always-online requirements  
- Complex dependency management
- Database requirements

### ✅ Added
- Local environment setup
- Terminal-optimized interface
- File-based storage
- Simplified configuration
- Local development tools

### ✅ Improved
- Faster startup time
- Better error handling
- Local data persistence
- Simplified dependencies

## Support

For local setup issues:
1. Run `python start_local.py --test`
2. Check `./data/logs/` for error logs
3. Verify `.env` configuration
4. Ensure Python 3.8+ is installed

For trading issues:
1. Always test in demo mode first
2. Check wallet configuration
3. Verify network connectivity
4. Review trading logs

---

**🎉 Ready to trade locally? Start with `python start_local.py --test`**
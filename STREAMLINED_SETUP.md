# Streamlined Setup Guide

## Quick Setup (Minimal Configuration)

The repository has been streamlined to require only two essential components:

### Required
1. **WALLET_PRIVATE_KEY** - Your Solana wallet private key for trading
2. **TELEGRAM_BOT_TOKEN** - Your Telegram bot token for the interface

### Example .env file
```env
WALLET_PRIVATE_KEY=your_solana_private_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
DEMO_MODE=true
```

## What's Changed

### ✅ Database Dependency Removed
- **Before**: Required PostgreSQL database with `DATABASE_URI`
- **After**: Uses file-based storage in `data/storage/` directory
- **Benefit**: No database setup required, works out of the box

### ✅ Moralis API Dependency Removed
- **Before**: Required `MORALIS_API_KEY` for token information
- **After**: Uses free Jupiter API and public Solana RPC for token info
- **Benefit**: No API key signup required

### ✅ Premium RPC Dependency Removed
- **Before**: Relied on `PURCHASED_RPC` for performance
- **After**: Automatically falls back to free public RPC endpoints
- **Benefit**: Works without premium services

### ✅ Optional Configuration
All other settings now have sensible defaults:
- `TELEGRAM_CHAT_ID` - Optional, some features may be limited
- `SOLANA_RPC_ENDPOINT` - Defaults to free public endpoint
- `DEMO_MODE` - Defaults to `true` for safety
- Trading parameters have conservative defaults

## API Dependencies Summary

### Still Required
- **TELEGRAM_BOT_TOKEN** - For Telegram bot interface
- **WALLET_PRIVATE_KEY** - For blockchain transactions

### Now Optional (with fallbacks)
- **TELEGRAM_CHAT_ID** - Enhances Telegram features
- **PURCHASED_RPC** - Falls back to free public RPCs
- **MORALIS_API_KEY** - Falls back to Jupiter/Solana APIs
- **DATABASE_URI** - Falls back to file storage

### Completely Removed
- Premium WebSocket endpoints
- Complex database setup requirements
- Mandatory API key registrations

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/elijahhoudini/Final-.git
   cd Final-
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create minimal .env file**
   ```bash
   cp .env.example .env
   # Edit .env with your wallet private key and Telegram bot token
   ```

4. **Run the bot**
   ```bash
   # Run Telegram bot
   python start_unified.py --bot solbot
   
   # Run AURACLE bot
   python start_unified.py --bot auracle
   ```

## Enhanced Features (Optional)

To enable premium features, you can optionally add:
- `PURCHASED_RPC` - For faster RPC performance
- `MORALIS_API_KEY` - For enhanced token metadata
- `DATABASE_URI` - For persistent storage across restarts

## File Storage Structure

When using file storage (default), data is stored in:
```
data/storage/
├── priv_keys.json      # Encrypted private keys
├── referrals.json      # Referral relationships
├── fees.json           # User fee preferences
├── orders.json         # Trading orders
├── watchlists.json     # Token watchlists
├── strategies.json     # Trading strategies
└── volumes.json        # Trading volume data
```

## Testing the Setup

Run the test script to verify everything works:
```bash
python test_streamlined_setup.py
```

This will test:
- File storage functionality
- Token information retrieval
- RPC endpoint connectivity
- Configuration validation

## Troubleshooting

### Common Issues

1. **Network connectivity errors**
   - The bot will retry with different RPC endpoints
   - Some features may be limited without internet

2. **Missing Telegram features**
   - Ensure `TELEGRAM_BOT_TOKEN` is set
   - Add `TELEGRAM_CHAT_ID` for full functionality

3. **Performance issues**
   - Consider adding `PURCHASED_RPC` for faster responses
   - File storage may be slower than database for large datasets

### Getting Help

- Check the logs in `data/` directory
- Ensure all required environment variables are set
- Test with demo mode first before live trading
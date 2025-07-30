# AURACLE Autonomous AI Trading Bot - Usage Guide

## Quick Start

### 1. Environment Setup

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

**Required Variables:**
```env
WALLET_PRIVATE_KEY=your_solana_wallet_private_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
LIVE_MODE=false  # Set to true for live trading
```

**Recommended Variables:**
```env
TELEGRAM_ADMIN_CHAT_ID=admin_chat_id_here
TELEGRAM_AUTH_PASSWORD=secure_password_here
PURCHASED_RPC=your_premium_rpc_endpoint
PURCHASED_WSS=your_premium_websocket_endpoint
```

### 2. Testing Mode

Start in demo mode (safe, no real trades):
```bash
python autonomous_ai_trader.py
```

Or run the demonstration:
```bash
python demo_autonomous_trader.py
```

### 3. Live Trading Mode

⚠️ **DANGER**: Only use with small amounts initially!

```bash
LIVE_MODE=true python autonomous_ai_trader.py
```

## Telegram Commands

Once your bot is running, use these commands in Telegram:

### Trading Controls
- `/pause` - Pause all trading
- `/resume` - Resume trading  
- `/stop` - Emergency stop (cancels pending trades)
- `/force_sell SYMBOL` - Force sell specific token

### Information
- `/status` - Current bot status and metrics
- `/positions` - List open trading positions
- `/performance` - Performance statistics
- `/logs 20` - Show recent log entries
- `/journal 2024-01-15` - Show trade journal for date

### Configuration
- `/settings` - Display current settings
- `/blacklist` - Show/manage token blacklist
- `/auth PASSWORD` - Authorize your account

### Emergency
- Send "STOP" (all caps) for immediate emergency stop
- Send "SELL ALL" (all caps) to force sell all positions

## Safety Features

### Cold Start Checks
Before trading begins, the bot validates:
- ✅ Wallet balance ≥ 0.01 SOL minimum
- ✅ Valid private key and wallet connection
- ✅ All required environment variables present
- ✅ Network connectivity to Solana RPC and Jupiter API
- ✅ Telegram bot functionality

### Real-Time Protection
- 🛡️ **Price Impact Limits**: Rejects trades with >2% price impact
- 🛡️ **Token Blacklist**: Blocks known scam/rug tokens
- 🛡️ **SPL Token Filter**: Only trades valid SPL tokens (no NFTs)
- 🛡️ **Kill Switch**: Auto-stops on excessive API errors
- 🛡️ **Private Key Security**: Read-once memory storage

### Transaction Monitoring
- 📡 **WebSocket Confirmations**: Real-time transaction status
- 🔄 **Redundant Execution**: 3 retry attempts with exponential backoff
- ⏱️ **Timeout Detection**: Auto-retry trades stalled >10 seconds
- 🔧 **Fallback RPCs**: Multiple backup RPC endpoints

## Configuration Options

### Trading Parameters
```env
MAX_BUY_AMOUNT_SOL=0.001          # Maximum SOL per trade
PROFIT_TARGET_PERCENTAGE=0.20      # 20% profit target
STOP_LOSS_PERCENTAGE=-0.05         # 5% stop loss
SCAN_INTERVAL_SECONDS=60           # Scan frequency
MAX_DAILY_TRADES=50                # Daily trade limit
MAX_OPEN_POSITIONS=10              # Concurrent position limit
```

### Risk Management
```env
MAX_PRICE_IMPACT_PERCENT=2.0       # Price impact threshold
DEFAULT_SLIPPAGE_BPS=100           # Default 1% slippage
MAX_RETRY_ATTEMPTS=3               # Retry limit
EXECUTION_TIMEOUT_SECONDS=10       # Trade timeout
```

### Security Settings
```env
MIN_WALLET_BALANCE_SOL=0.01        # Minimum balance requirement
MAX_API_ERRORS=10                  # Error threshold for kill switch
API_ERROR_WINDOW_MINUTES=5         # Error tracking window
CLEAR_PRIVATE_KEY_AFTER_LOAD=true  # Clear key from memory
```

## Logging and Monitoring

### Log Files
- `logs/autonomous_trader.log` - Main application logs
- `logs/trade_log_YYYYMMDD.json` - Daily trade journals

### Trade Journal Format
Each trade is logged with complete metadata:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "token_mint": "...",
  "token_symbol": "DEMO",
  "action": "buy",
  "amount_sol": 0.001,
  "expected_price": 0.00001,
  "actual_price": 0.000011,
  "slippage_percent": 1.2,
  "price_impact_percent": 0.8,
  "execution_delay_ms": 750,
  "transaction_hash": "...",
  "wallet_balance_before": 0.1,
  "wallet_balance_after": 0.099,
  "sentiment_score": 0.75,
  "confidence_score": 0.85,
  "retry_count": 1,
  "status": "confirmed"
}
```

## Performance Optimization

### RPC Configuration
For best performance, use premium RPC endpoints:
```env
PURCHASED_RPC=https://your-premium-rpc.com
PURCHASED_WSS=wss://your-premium-websocket.com
```

### Fallback RPCs
The bot automatically uses these fallbacks if primary RPC fails:
- `https://api.mainnet-beta.solana.com`
- `https://solana-api.projectserum.com`
- `https://rpc.ankr.com/solana`

### Network Health Monitoring
- Automatic RPC health checks every 5 minutes
- WebSocket reconnection on disconnection
- Intelligent routing to fastest available endpoint

## Troubleshooting

### Common Issues

1. **"No module named 'solana'"**
   ```bash
   pip install solana solders
   ```

2. **"Kill switch activated"**
   - Check logs for API errors
   - Verify RPC endpoint health
   - Clear kill switch: `rm KILL_SWITCH_ACTIVE`

3. **"Insufficient wallet balance"**
   - Ensure wallet has ≥0.01 SOL
   - Check `WALLET_PRIVATE_KEY` is correct

4. **"Telegram bot not responding"**
   - Verify `TELEGRAM_BOT_TOKEN` is valid
   - Check `TELEGRAM_CHAT_ID` is correct
   - Authorize with `/auth PASSWORD`

### Debug Mode
Enable detailed logging:
```env
LOG_LEVEL=DEBUG
ENABLE_PERFORMANCE_LOGGING=true
```

### Testing Connection
```bash
python -c "
import asyncio
from safety_checks import SafetyChecks
async def test():
    safety = SafetyChecks()
    result = await safety.check_network_connectivity()
    print('Network OK' if result else 'Network Issues')
asyncio.run(test())
"
```

## Production Deployment

### Pre-Deployment Checklist
- [ ] Test extensively in demo mode
- [ ] Verify all environment variables
- [ ] Confirm wallet has sufficient balance
- [ ] Test Telegram commands
- [ ] Set conservative trading parameters
- [ ] Monitor initial trades closely

### Recommended Settings for Live Trading
```env
LIVE_MODE=true
MAX_BUY_AMOUNT_SOL=0.001          # Start small!
PROFIT_TARGET_PERCENTAGE=0.15      # Conservative 15%
STOP_LOSS_PERCENTAGE=-0.03         # Tight 3% stop loss
MAX_DAILY_TRADES=20                # Limited daily trades
MAX_OPEN_POSITIONS=3               # Max 3 concurrent positions
```

### Monitoring
- Monitor Telegram for real-time updates
- Check trade journal daily
- Review performance statistics weekly
- Adjust parameters based on results

## Support

For issues or questions:
1. Check the logs in `logs/` directory
2. Run `python demo_autonomous_trader.py` to test functionality
3. Verify environment configuration
4. Review this guide for troubleshooting steps

⚠️ **Important**: This bot trades with real money in live mode. Always test thoroughly in demo mode first and start with small amounts. Trading cryptocurrencies involves substantial risk of loss.
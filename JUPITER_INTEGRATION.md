# Jupiter Swap Integration Guide

## Overview

The AURACLE bot now includes full Jupiter swap integration for real token trading on Solana. This integration provides secure, efficient, and well-monitored trading capabilities while maintaining all existing safety features.

## Key Features

### ⚡ Real Trading Capabilities
- **Jupiter V6 API Integration**: Latest Jupiter swap API for optimal pricing and execution
- **Real-time Quote Generation**: Sub-second quote generation for accurate pricing
- **Automatic Route Optimization**: Jupiter finds the best trading routes across multiple DEXs
- **Slippage Protection**: Configurable slippage limits to protect against MEV attacks

### 🛡️ Advanced Risk Management
- **Price Impact Analysis**: Automatic rejection of trades with excessive price impact
- **Position Size Limits**: Configurable maximum trade sizes and position limits
- **Balance Monitoring**: Real-time balance validation and reserve management
- **Transaction Validation**: Multi-layer validation before trade execution

### 📊 Performance Monitoring
- **Real-time Metrics**: Live performance tracking for all operations
- **Execution Time Monitoring**: Automatic detection of slow transactions
- **Success Rate Tracking**: Comprehensive statistics on trade success rates
- **Error Analysis**: Detailed error tracking and resolution

## Configuration

### Environment Variables

```bash
# Jupiter API Configuration
JUPITER_ENABLED=true                    # Enable Jupiter integration
JUPITER_DEFAULT_SLIPPAGE_BPS=50        # Default slippage (0.5%)
JUPITER_MAX_SLIPPAGE_BPS=300           # Maximum slippage (3%)
JUPITER_MAX_PRICE_IMPACT=5.0           # Maximum price impact (5%)

# Trading Limits
JUPITER_MAX_TRADE_SIZE_SOL=1.0         # Maximum trade size (1 SOL)
JUPITER_MIN_LIQUIDITY_USD=10000        # Minimum liquidity ($10k)

# Performance Settings
JUPITER_QUOTE_TIMEOUT=10               # Quote timeout (10s)
JUPITER_SWAP_TIMEOUT=30                # Swap timeout (30s)
JUPITER_CONFIRMATION_TIMEOUT=30        # Confirmation timeout (30s)

# Transaction Settings
JUPITER_COMPUTE_UNIT_PRICE=1000        # Compute unit price (microlamports)
JUPITER_PRIORITY_FEE=1000              # Priority fee (lamports)
JUPITER_MAX_RETRIES=3                  # Maximum retry attempts
```

### Configuration in Code

```python
# config.py
JUPITER_ENABLED = True
JUPITER_DEFAULT_SLIPPAGE_BPS = 50  # 0.5%
JUPITER_MAX_PRICE_IMPACT = 5.0     # 5%
JUPITER_MAX_TRADE_SIZE_SOL = 1.0   # 1 SOL
```

## Usage

### Basic Trading

```python
from jupiter_swap import JupiterSwapClient, initialize_jupiter_client
from solana.rpc.api import Client

# Initialize RPC client
rpc_client = Client("https://api.mainnet-beta.solana.com")

# Initialize Jupiter client
jupiter_client = initialize_jupiter_client(rpc_client, wallet_keypair)

# Buy tokens
signature = await jupiter_client.buy_token(
    token_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    sol_amount=0.1,
    slippage_bps=100  # 1% slippage
)

# Sell tokens
signature = await jupiter_client.sell_token(
    token_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    token_amount=100_000_000,  # 100 USDC (in smallest units)
    slippage_bps=100  # 1% slippage
)
```

### Risk Management

```python
from jupiter_risk import JupiterRiskManager, initialize_risk_manager

# Initialize risk manager
risk_manager = initialize_risk_manager(logger)

# Assess trade risk
risk_assessment = risk_manager.assess_swap_risk(
    quote=jupiter_quote,
    token_data=token_info,
    trade_amount_sol=0.1,
    current_balance=1.0
)

# Check risk recommendation
if risk_assessment["recommendation"] == "PROCEED":
    # Execute trade
    pass
elif risk_assessment["recommendation"] == "CAUTION":
    # Proceed with warnings
    pass
else:
    # Reject trade
    pass
```

## Safety Features

### Demo Mode Protection
- **Default Demo Mode**: Bot starts in safe demo mode
- **Easy Toggle**: Switch between demo and live trading
- **Simulation**: Full trade simulation in demo mode
- **No Real Transactions**: Zero risk in demo mode

### Risk Assessment
- **Price Impact Limits**: Automatic rejection of high-impact trades
- **Slippage Protection**: Configurable slippage tolerance
- **Position Size Limits**: Maximum trade and position sizes
- **Balance Reserves**: Maintains minimum balance for fees

### Error Handling
- **Network Resilience**: Automatic retry on network errors
- **Timeout Management**: Configurable timeouts for all operations
- **Graceful Degradation**: Fallback to demo mode on errors
- **Comprehensive Logging**: Detailed error tracking

## Monitoring and Logging

### Trade Logging
```json
{
  "action": "BUY",
  "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  "sol_amount": 0.1,
  "expected_tokens": "100000000",
  "price_impact": 0.5,
  "signature": "5J7Y...",
  "execution_time": 2.5,
  "risk_score": 15
}
```

### Performance Metrics
```json
{
  "signature": "5J7Y...",
  "execution_time": 2.5,
  "timestamp": "2024-01-15T10:30:00Z",
  "status": "completed"
}
```

### Risk Statistics
```json
{
  "risk_flags_count": 5,
  "price_impact_violations": 2,
  "slippage_violations": 1,
  "transactions_monitored": 100,
  "average_execution_time": 3.2
}
```

## Testing

### Run Integration Tests
```bash
python test_jupiter_integration.py
```

### Test Results
- **Quote Generation**: Tests Jupiter quote API
- **Swap Execution**: Tests trade execution
- **Risk Management**: Tests risk assessment
- **Error Handling**: Tests error scenarios
- **Performance**: Tests execution speed

## Troubleshooting

### Common Issues

#### 1. Quote Generation Failures
```
❌ Failed to get Jupiter quote for buy
```
**Solution**: Check network connection, increase timeout, verify token mint address

#### 2. High Price Impact
```
⚠️ High price impact: 8.5% - skipping trade
```
**Solution**: Reduce trade size, increase price impact limit, or wait for better market conditions

#### 3. Slippage Violations
```
❌ Slippage too high: 500 > 300 BPS
```
**Solution**: Increase slippage tolerance or reduce trade size

#### 4. Insufficient Balance
```
❌ Insufficient balance: 0.05 < 0.1 SOL
```
**Solution**: Add more SOL to wallet or reduce trade size

### Debug Mode
```python
# Enable debug logging
LOG_LEVEL = "DEBUG"

# Run tests with verbose output
python test_jupiter_integration.py --verbose
```

### Performance Optimization
```python
# Optimize for speed
JUPITER_QUOTE_TIMEOUT = 5      # Reduce quote timeout
JUPITER_SWAP_TIMEOUT = 15      # Reduce swap timeout

# Optimize for reliability
JUPITER_MAX_RETRIES = 5        # Increase retry attempts
JUPITER_CONFIRMATION_TIMEOUT = 60  # Increase confirmation timeout
```

## Migration Guide

### From Demo to Live Trading

1. **Set Environment Variables**
   ```bash
   export DEMO_MODE=false
   export WALLET_PRIVATE_KEY=your_private_key
   export JUPITER_ENABLED=true
   ```

2. **Update Configuration**
   ```python
   # config.py
   DEMO_MODE = False
   JUPITER_ENABLED = True
   ```

3. **Test with Small Amounts**
   ```python
   # Start with minimal trade sizes
   MAX_BUY_AMOUNT_SOL = 0.01
   ```

4. **Monitor Performance**
   ```bash
   # Watch logs for performance issues
   tail -f data/trade_logs.json
   ```

### Rollback to Demo Mode
```python
# Emergency rollback
config.set_demo_mode(True)

# Or restart bot with demo mode
export DEMO_MODE=true
```

## Best Practices

### Trading Configuration
- **Start Small**: Begin with minimal trade sizes
- **Monitor Performance**: Watch execution times and success rates
- **Adjust Limits**: Tune slippage and price impact limits based on market conditions
- **Regular Testing**: Run integration tests regularly

### Risk Management
- **Conservative Limits**: Start with conservative risk limits
- **Balance Monitoring**: Monitor wallet balance regularly
- **Position Sizing**: Use appropriate position sizes relative to portfolio
- **Stop Losses**: Implement stop losses for risk management

### Monitoring
- **Real-time Alerts**: Set up alerts for failed trades
- **Performance Tracking**: Monitor execution times and success rates
- **Risk Statistics**: Review risk statistics regularly
- **Log Analysis**: Analyze logs for patterns and issues

## API Reference

### JupiterSwapClient
```python
class JupiterSwapClient:
    async def get_quote(input_mint, output_mint, amount, slippage_bps)
    async def execute_swap(quote)
    async def buy_token(token_mint, sol_amount, token_data, slippage_bps)
    async def sell_token(token_mint, token_amount, slippage_bps)
    async def get_token_price(token_mint)
```

### JupiterRiskManager
```python
class JupiterRiskManager:
    def validate_quote(quote, trade_amount_sol)
    def validate_token_for_trading(token_data)
    def validate_balance_for_trade(current_balance, trade_amount)
    def assess_swap_risk(quote, token_data, trade_amount_sol, current_balance)
    def monitor_transaction_performance(signature, start_time)
    def get_risk_statistics()
```

## Support

For issues or questions:
- Check the troubleshooting guide above
- Review the test results
- Check the logs in `data/` directory
- Create an issue on GitHub

## Contributing

To contribute to the Jupiter integration:
1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests
4. Update documentation
5. Submit a pull request
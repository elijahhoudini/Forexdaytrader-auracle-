# Blockchain Integration for Replit

This document provides instructions for running the blockchain integration module on Replit.

## Overview

The blockchain integration module provides comprehensive Solana blockchain functionality including:

- **Jupiter API Integration**: Token swaps and price quotes
- **Wallet Management**: Secure wallet operations and key management
- **Transaction Management**: Building, signing, and sending transactions
- **RPC Management**: Solana RPC connection management
- **Priority Fee Calculation**: Optimal fee calculation for transactions
- **Solscan Integration**: Blockchain analytics and token information

## Quick Start

### 1. Installation

```bash
# Install required dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in your project root:

```env
# RPC Configuration
RPC_ENDPOINT=https://api.mainnet-beta.solana.com
RPC_TIMEOUT=30
MAX_RETRIES=3

# API Keys
SOLSCAN_API_KEY=your_solscan_api_key_here

# Wallet Configuration
WALLET_PATH=./wallet.json

# Transaction Configuration
DEFAULT_SLIPPAGE=0.005
MAX_SLIPPAGE=0.05
PRIORITY_FEE_MULTIPLIER=1.2
```

### 3. Running the Integration

```bash
# Run the main blockchain integration
python main_blockchain_integration.py

# Run tests
python test_blockchain_integration.py
```

## Module Structure

```
blockchain/
├── __init__.py                    # Package initialization
├── blockchain_config.py           # Configuration management
├── blockchain_logger.py           # Logging utilities
├── retry_decorator.py             # Retry functionality
├── jupiter_client.py              # Jupiter API client
├── rpc_manager.py                 # RPC connection management
├── wallet_manager.py              # Wallet operations
├── transaction_manager.py         # Transaction handling
├── priority_fee_calculator.py     # Fee calculation
└── solscan_client.py              # Solscan API client
```

## Usage Examples

### Basic Usage

```python
from blockchain import BlockchainIntegration

# Initialize
blockchain = BlockchainIntegration()
await blockchain.initialize(wallet_path="./wallet.json")

# Get wallet balance
balance = await blockchain.get_wallet_balance()
print(f"Balance: {balance} SOL")

# Perform Jupiter swap
signature = await blockchain.perform_jupiter_swap(
    input_mint="So11111111111111111111111111111111111111112",  # SOL
    output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    amount=1000000,  # 0.001 SOL
    slippage_bps=50  # 0.5%
)
```

### Advanced Features

```python
# Calculate priority fees
fee = await blockchain.calculate_priority_fee(urgency="high")

# Get token information
token_info = await blockchain.get_token_info(
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
)

# Get account information
account_info = await blockchain.get_account_info(
    "your_account_address_here"
)
```

## Replit-Specific Configuration

### Environment Variables

In your Replit project, set these environment variables in the "Secrets" tab:

```
RPC_ENDPOINT=https://api.mainnet-beta.solana.com
SOLSCAN_API_KEY=your_api_key_here
WALLET_PATH=./wallet.json
```

### Replit Run Command

Add this to your `.replit` file:

```toml
run = "python main_blockchain_integration.py"

[packager]
language = "python3"
ignoredPackages = ["unit_tests"]

[packager.features]
enabledForHosting = false
packageSearch = true
guessImports = true

[languages.python3]
pattern = "**/*.py"
syntax = "python"
```

### Dependencies

Ensure your `requirements.txt` includes:

```
solana>=0.34.0
solders>=0.21.0
aiohttp>=3.8.0
python-dotenv>=1.0.0
base58>=2.1.0
cryptography>=43.0.0
```

## Security Considerations

### Wallet Security

1. **Never commit wallet files to version control**
2. **Use environment variables for sensitive data**
3. **Implement proper access controls**
4. **Use secure random number generation**

### API Security

1. **Store API keys in environment variables**
2. **Implement rate limiting**
3. **Use HTTPS for all API calls**
4. **Validate all inputs**

## Error Handling

The integration includes comprehensive error handling:

```python
try:
    result = await blockchain.perform_jupiter_swap(...)
    if result:
        print(f"Swap successful: {result}")
    else:
        print("Swap failed")
except Exception as e:
    print(f"Error: {e}")
```

## Logging

Configure logging levels:

```python
from blockchain import BlockchainLogger

logger = BlockchainLogger("my_app", log_level="DEBUG")
```

## Testing

Run the test suite:

```bash
# Run all tests
python -m pytest test_blockchain_integration.py -v

# Run specific test
python -m pytest test_blockchain_integration.py::TestJupiterClient -v
```

## Troubleshooting

### Common Issues

1. **RPC Connection Failures**
   - Check RPC endpoint URL
   - Verify network connectivity
   - Ensure RPC endpoint is accessible

2. **Wallet Loading Issues**
   - Verify wallet file exists
   - Check wallet file permissions
   - Ensure wallet file format is correct

3. **Transaction Failures**
   - Check account balance
   - Verify transaction parameters
   - Ensure proper fee calculation

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Optimization

### Connection Pooling

The integration uses connection pooling for optimal performance:

```python
# RPC connections are automatically pooled
# HTTP sessions are reused for API calls
```

### Retry Logic

Built-in retry mechanisms for:
- RPC calls
- API requests
- Transaction operations

### Caching

Priority fee calculations are cached for better performance.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the test suite for examples
3. Open an issue in the repository

## License

This blockchain integration module is part of the AURACLE project.
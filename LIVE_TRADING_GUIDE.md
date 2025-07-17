# AURACLE Live Trading Guide
# July 17, 2025

## Introduction

This guide explains how to safely set up and run AURACLE in live trading mode. The bot has been updated to focus on AI-driven profitable trading rather than token sniping.

## Security Warning

**NEVER SHARE YOUR PRIVATE KEYS!** Private keys should never be:
- Posted in chat messages
- Stored in GitHub repositories
- Included in unencrypted files
- Shared with others
- Stored in cloud services without encryption

## Secure Setup Process

### Step 1: Initial Setup

1. Make sure all dependencies are installed:
   ```
   pip install -r requirements.txt
   ```

2. Verify that the bot runs in demo mode first:
   ```
   python start.py
   ```

### Step 2: Configure for Live Trading

1. Edit the `.env` file to configure your trading parameters (already done):
   - The environment is already configured with safe initial values
   - DEMO_MODE is set to false
   - Trading limits are set to conservative values

2. Configure your wallet securely using one of these methods:

   **Option A: Terminal Method**
   ```
   ./setup_wallet.sh
   ```
   - This will prompt for your private key in the terminal
   - The key is only stored in memory, never in files
   - You will need to run this each time you start a new terminal session

   **Option B: Telegram Method (More Secure)**
   ```
   ./start_telegram_wallet.sh
   ```
   - This starts a Telegram bot that allows you to set your key via Telegram
   - Send `/set_wallet_key` to your bot in Telegram
   - Follow the prompts to securely set your key
   - Your message containing the key will be deleted immediately
   - Ideal for remote management of the bot

### Step 3: Start Live Trading

1. Launch the bot with secure wallet configuration:
   ```
   ./start_secure.sh
   ```
   - If no wallet key is configured, the script will prompt you to choose a setup method

2. Monitor the initial execution closely:
   - Watch the first few scans to ensure tokens are being discovered correctly
   - Verify that the risk management system is functioning properly
   - Confirm that trades align with your risk tolerance

## Risk Management

The bot is configured with multiple layers of risk management:

- **Position Limits**: Maximum 3 open positions at once
- **Daily Trade Limits**: Maximum 10 trades per day
- **Investment Limits**: Maximum 0.05 SOL per trade
- **Stop Loss**: -5% to limit downside risk
- **Profit Targets**: 15% to ensure realistic gains
- **Trailing Stops**: Lock in profits as they increase
- **Minimum Liquidity**: $2000 USD to avoid illiquid tokens
- **AI Confidence**: Minimum 65% confidence required for trades
- **Profit-Only Mode**: Focus on profitable opportunities

## Advanced Configuration

For advanced users who want to fine-tune the bot:

1. Edit `.env` file parameters to adjust:
   - Risk tolerance
   - Trading frequency
   - Position sizing
   - AI confidence thresholds

2. Modify risk.py for custom risk evaluation logic

3. Update config.py for additional advanced settings

## Monitoring and Maintenance

1. Check the bot's status regularly using:
   ```
   python bot_status.py
   ```

2. Review trading logs in the `data` directory

3. Schedule regular backups of your configuration

4. Update the bot software regularly for bug fixes and improvements

## Emergency Stop

If you need to stop the bot immediately:

```
python stop_bot.py
```

This will gracefully close all active processes and ensure no new trades are initiated.

## Legal and Compliance

Remember that you are responsible for ensuring compliance with all relevant laws and regulations in your jurisdiction. Automated trading may be subject to various regulatory requirements depending on your location.

## Getting Help

If you encounter issues or have questions:

1. Check the documentation in the project's README
2. Search for similar issues in the project repository
3. Reach out to the community for support

Happy trading, and may your profits be high and your risks low!

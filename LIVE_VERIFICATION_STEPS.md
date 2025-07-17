# AURACLE Live Trading Verification Steps
# Created: July 17, 2025

## Pre-Launch Final Checks

Before enabling live trading, complete these verification steps:

1. ✓ Run the bot in demo mode to verify all components function correctly
2. ✓ Check trading logic for both buy and sell decisions
3. ✓ Test risk management features (stop loss, quick profit, trailing stop)
4. ✓ Create secure wallet key handling process
5. ✓ Configure appropriate trading limits

## Enabling Live Mode

Follow these steps to enable live trading:

1. First stop any running bot instance:
   ```
   CTRL+C in terminal or
   python stop_bot.py
   ```

2. Set up your wallet securely:
   ```
   ./setup_wallet.sh
   ```
   When prompted, enter your private key.

3. Verify wallet connection:
   The script will display your wallet address (partially masked)
   Confirm it matches your intended trading wallet.

4. Update .env for live trading:
   ```
   nano .env
   ```
   Change DEMO_MODE=true to DEMO_MODE=false

5. Start the bot in live mode:
   ```
   ./start_secure.sh
   ```

## Initial Live Monitoring Period

During the first few hours of live trading:

1. Monitor all trades closely
2. Watch for any unexpected behaviors
3. Be prepared to stop the bot if needed
4. Verify that trades execute properly on the blockchain
5. Confirm that stop losses and profit taking work correctly

## Adjusting Parameters

After initial testing, you may want to adjust:

1. MAX_BUY_AMOUNT_SOL - Start small, increase gradually
2. PROFIT_TARGET_PERCENTAGE - Adjust based on market conditions
3. STOP_LOSS_PERCENTAGE - Adjust based on risk tolerance
4. AI_CONFIDENCE_THRESHOLD - Increase for higher quality trades

## Safety Reminders

- NEVER share your private key with anyone
- NEVER store your key in plaintext files
- Regularly back up your configuration
- Monitor the bot's performance daily
- Stay informed about market conditions

## Emergency Procedures

If you need to stop trading immediately:

1. Run `python stop_bot.py`
2. Or press CTRL+C in the terminal
3. For emergency funds withdrawal, use a separate wallet UI

## Support

If you encounter issues, please check the documentation or reach out through official channels.

Good luck with your trading!

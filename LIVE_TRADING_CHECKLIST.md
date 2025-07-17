# AURACLE Live Trading Pre-Launch Checklist
# Created: July 17, 2025

## Security Measures
- [✓] Private key is never stored directly in code or configuration files
- [✓] Private key is loaded securely via environment variables 
- [✓] Wallet setup process is separate from bot startup
- [✓] Secure scripts created for managing wallet key
- [✓] Multiple methods to set wallet key (terminal or Telegram)
- [✓] Telegram setup option for enhanced security
- [✓] Bot runs with minimal permissions needed

## Risk Management Configuration
- [✓] Start with small trade amounts (MAX_BUY_AMOUNT_SOL=0.05)
- [✓] Limited number of daily trades (MAX_DAILY_TRADES=10)
- [✓] Limited number of concurrent positions (MAX_OPEN_POSITIONS=3)
- [✓] Stop loss configured to limit downside (-5%)
- [✓] Profit targets set realistically (15%)
- [✓] Trailing stop enabled to lock in profits
- [✓] AI confidence threshold set to reduce false positives (65%)

## Bot Configuration
- [✓] DEMO_MODE=false for live trading
- [✓] AUTONOMOUS_MODE=true for automated trading
- [✓] USE_AI_TRADING=true to enable AI-driven decisions
- [✓] DISABLE_SNIPER=true to focus on profitable AI trades
- [✓] Reasonable scan interval (30 seconds)
- [✓] Profit-only mode enabled to focus on gains

## Before First Live Run
- [ ] Test wallet connection with small amount of SOL
- [ ] Run in read-only mode first (observe but don't trade)
- [ ] Verify token discovery working correctly
- [ ] Double check all risk parameters
- [ ] Ensure sufficient SOL in wallet for trading + fees

## Monitoring Setup
- [ ] Set up monitoring alerts for unusual activity
- [ ] Configure regular portfolio status reports
- [ ] Ensure error logging is comprehensive
- [ ] Monitor initial trades closely

## Performance Tracking
- [ ] Baseline performance metrics established
- [ ] Profit tracking system verified
- [ ] Daily reports configured

## IMPORTANT REMINDER
Remember that all trading carries risk. Start with small amounts and gradually 
increase as you gain confidence in the system's performance. Be prepared to 
intervene manually if needed.

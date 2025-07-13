"""
AURACLE: Autonomous AI Solana Trading Bot
========================================

Main system controller and trading loop for Traveler 5798's assistant.
Coordinates all subsystems for autonomous token discovery and trading.
"""

import time
import signal
import sys
import threading
from datetime import datetime
from typing import Dict, Any

# Import AURACLE modules
from scanner import TokenScanner
from trade import TradeHandler
from risk import RiskEvaluator
from logger import AuracleLogger
from wallet import Wallet
from telegram_bot import AuracleTelegramBot
import config

class Auracle:
    """
    Main AURACLE system controller.

    Orchestrates autonomous trading operations by coordinating:
    - Token scanning and discovery
    - Risk assessment and fraud detection
    - Trade execution and position management
    - Logging and performance monitoring
    """

    def __init__(self):
        """Initialize AURACLE system with all components."""
        print("=" * 60)
        print(f"🚀 INITIALIZING {config.BOT_NAME} v{config.BOT_VERSION}")
        print(f"👤 Traveler ID: {config.TRAVELER_ID}")
        print(f"🤖 Mode: {'Autonomous' if config.AUTONOMOUS_MODE else 'Manual'}")
        print(f"📊 Trading: {config.get_trading_mode_string()}")
        print("=" * 60)

        # Initialize core components
        self.logger = AuracleLogger()
        self.wallet = Wallet()
        self.trade_handler = TradeHandler(self.wallet)
        self.scanner = TokenScanner(self.trade_handler, self)  # Pass self to scanner
        self.risk = RiskEvaluator()

        # Initialize Telegram bot if configured
        self.telegram_bot = None
        if config.TELEGRAM_ENABLED and config.TELEGRAM_BOT_TOKEN:
            try:
                self.telegram_bot = AuracleTelegramBot(
                    config.TELEGRAM_BOT_TOKEN, 
                    config.TELEGRAM_CHAT_ID
                )
                self.telegram_bot.set_auracle_bot(self)
                print("✅ Telegram bot initialized")
            except Exception as e:
                print(f"⚠️ Telegram bot initialization failed: {e}")

        # System state
        self.running = False
        self.trading_active = True
        self.stats = {
            "scans_completed": 0,
            "tokens_evaluated": 0,
            "trades_executed": 0,
            "start_time": datetime.utcnow()
        }

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        print("✅ AURACLE initialization complete")
        self.logger.log_system("AURACLE initialized successfully")

    def run(self):
        """
        Main trading loop.

        Continuously scans for tokens, evaluates them, and executes trades
        based on the configured strategy and risk parameters.
        """
        import asyncio

        self.running = True
        session_start = datetime.utcnow()

        self.logger.log_system("AURACLE main loop starting")
        print("🔄 Starting main trading loop...")

        # Start Telegram bot in background thread
        if self.telegram_bot:
            telegram_thread = threading.Thread(target=self.telegram_bot.start, daemon=True)
            telegram_thread.start()
            self.send_startup_notification()

        # Start async scanner loop
        try:
            asyncio.run(self._async_main_loop())
        except KeyboardInterrupt:
            print("\n🛑 Received keyboard interrupt, shutting down...")
        finally:
            self._shutdown()
            session_end = datetime.utcnow()
            session_duration = session_end - session_start

            print(f"\n📊 Trading Session Summary:")
            print(f"   Duration: {session_duration}")
            print(f"   Scans: {self.stats['scans_completed']}")
            print(f"   Trades: {self.stats['trades_executed']}")
            print("🏁 AURACLE - Session Ended")
            print("=" * 60)

    async def _async_main_loop(self):
        """Async main loop that runs the scanner and monitors positions."""
        scan_count = 0
        last_status_time = time.time()

        # Start scanner task
        import asyncio
        scanner_task = asyncio.create_task(self.scanner.scan_loop())

        try:
            while self.running:
                scan_count += 1

                # Monitor existing positions
                self.trade_handler.monitor_positions()

                # Update statistics
                self.stats["scans_completed"] += 1

                # Send periodic status updates
                if time.time() - last_status_time > 300:  # Every 5 minutes
                    self.send_status_update()
                    self._display_portfolio_status()
                    last_status_time = time.time()

                # Sleep for a short time before next monitoring cycle
                await asyncio.sleep(30)

        except Exception as e:
            self.logger.log_error(f"Main loop error: {str(e)}")
            print(f"❌ Main loop error: {str(e)}")
        finally:
            scanner_task.cancel()
            try:
                await scanner_task
            except asyncio.CancelledError:
                pass

    def _scan_for_opportunities(self):
        """
        Scan for new trading opportunities.

        Returns:
            List[Dict]: List of token opportunities
        """
        try:
            tokens = self.scanner.scan()
            self.stats["tokens_evaluated"] += len(tokens)

            if tokens:
                self.logger.log_system(f"Found {len(tokens)} potential opportunities")

            return tokens

        except Exception as e:
            self.logger.log_error(f"Scanner error: {str(e)}")
            return []

    def _process_token(self, token: Dict[str, Any]):
        """
        Process a single token through the trading pipeline.

        Args:
            token (Dict): Token data to process
        """
        try:
            # Step 1: Risk evaluation
            risk_result = self.risk.evaluate(token)

            if not risk_result.get("safe", False):
                self.logger.log_flag(
                    token["mint"], 
                    f"Risk assessment failed: {risk_result.get('reason', 'Unknown')}", 
                    token
                )
                return

            # Step 2: Trading decision
            if self.trade_handler.should_buy(token) and self.trading_active:
                # Calculate dynamic trade amount based on confidence
                trade_amount = self.trade_handler.calculate_trade_amount(token)

                success = self.trade_handler.buy_token(token, trade_amount)

                if success:
                    self.stats["trades_executed"] += 1
                    self.logger.log_trade("BUY", token, trade_amount)

                    # Send Telegram notification if configured
                    if self.telegram_bot:
                        symbol = token.get("symbol", "Unknown")
                        message = f"✅ AURACLE BUY: {symbol} - {trade_amount} SOL"
                        try:
                            self.telegram_bot.send_message(message)
                        except:
                            pass  # Don't let telegram errors stop trading
                else:
                    self.logger.log_trade("BUY_FAILED", token, trade_amount)

        except Exception as e:
            self.logger.log_error(f"Error processing token {token.get('mint', 'unknown')}: {str(e)}")

    def get_status(self) -> Dict[str, Any]:
        """
        Get current system status and performance metrics.

        Returns:
            Dict: Current status information
        """
        uptime = datetime.utcnow() - self.stats["start_time"]
        portfolio = self.trade_handler.get_portfolio_summary()

        return {
            "status": "running" if self.running else "stopped",
            "trading_mode": config.get_trading_mode_string(),
            "uptime": str(uptime),
            "statistics": self.stats,
            "portfolio": portfolio,
            "configuration": {
                "max_buy_amount": config.MAX_BUY_AMOUNT_SOL,
                "scan_interval": config.SCAN_INTERVAL_SECONDS,
                "profit_target": config.PROFIT_TARGET_PERCENTAGE,
                "stop_loss": config.STOP_LOSS_PERCENTAGE
            }
        }

    def toggle_trading(self) -> bool:
        """
        Toggle trading on/off.

        Returns:
            bool: New trading state
        """
        self.trading_active = not self.trading_active
        status = "enabled" if self.trading_active else "disabled"
        self.logger.log_system(f"Trading {status}")
        return self.trading_active

    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        print(f"\n🛑 Received signal {signum}, initiating shutdown...")
        self.running = False

    def _shutdown(self):
        """Graceful shutdown procedure."""
        print("\n🔄 Shutting down AURACLE...")

        try:
            # Close any open positions if in demo mode
            if config.get_demo_mode():
                for mint in list(self.trade_handler.open_positions.keys()):
                    self.trade_handler.sell_token(mint, "shutdown")

            # Log session summary
            session_summary = self.logger.get_session_summary()
            self.logger.log_system("AURACLE session ended", session_summary)

            # Final status report
            print("\n📊 Final Session Report:")
            print(f"   Scans Completed: {self.stats['scans_completed']}")
            print(f"   Tokens Evaluated: {self.stats['tokens_evaluated']}")
            print(f"   Trades Executed: {self.stats['trades_executed']}")
            print(f"   Session Duration: {datetime.utcnow() - self.stats['start_time']}")

        except Exception as e:
            print(f"⚠️ Error during shutdown: {e}")

        finally:
            print("=" * 60)
            print("🤖 AURACLE - Traveler 5798's Assistant - Session Ended")
            print("=" * 60)

    def send_startup_notification(self):
        """Sends a startup notification via Telegram, if enabled."""
        if self.telegram_bot:
            message = f"🚀 {config.BOT_NAME} v{config.BOT_VERSION} started in {config.get_trading_mode_string()} mode."
            try:
                self.telegram_bot.send_message(message)
            except Exception as e:
                self.logger.log_error(f"Telegram startup notification failed: {e}")

    def send_status_update(self):
        """Sends a status update via Telegram, if enabled."""
        if self.telegram_bot:
            status = self.get_status()
            message = f"📊 Status Update:\n"
            message += f"Uptime: {status['uptime']}\n"
            message += f"Scans Completed: {status['statistics']['scans_completed']}\n"
            message += f"Trades Executed: {status['statistics']['trades_executed']}\n"
            message += f"Portfolio Value: {status['portfolio']['total_value']:.2f} SOL"
            try:
                self.telegram_bot.send_message(message)
            except Exception as e:
                self.logger.log_error(f"Telegram status update failed: {e}")
    
    def _display_portfolio_status(self):
        """Display current portfolio status to console."""
        try:
            portfolio = self.trade_handler.get_portfolio_summary()
            
            print("\n" + "=" * 50)
            print("📊 PORTFOLIO STATUS")
            print("=" * 50)
            print(f"Open Positions: {portfolio['open_positions']}")
            print(f"Total Invested: {portfolio['total_invested_sol']:.4f} SOL")
            print(f"Total P&L: {portfolio['total_pnl_sol']:+.4f} SOL")
            print(f"Portfolio Value: {portfolio['total_value']:.4f} SOL")
            print(f"Daily Trades: {portfolio['daily_trades']}")
            
            if portfolio['positions']:
                print("\nOpen Positions:")
                for pos in portfolio['positions']:
                    age_minutes = (datetime.utcnow() - pos['buy_time']).total_seconds() / 60
                    current_pnl = pos.get('current_pnl_percent', 0)
                    print(f"  {pos['symbol']:>8} | {pos['buy_price_sol']:.4f} SOL | {current_pnl:+6.1f}% | {age_minutes:.0f}m")
            
            print("=" * 50)
            
        except Exception as e:
            print(f"❌ Error displaying portfolio status: {e}")


def main():
    """
    Main entry point for AURACLE bot.

    Validates configuration and starts the trading system.
    """
    try:
        # Validate configuration
        if not config.validate_config():
            print("❌ Configuration validation failed. Please check config.py")
            sys.exit(1)

        # Display configuration summary
        print("\n🔧 Configuration Summary:")
        print(f"   Max Buy Amount: {config.MAX_BUY_AMOUNT_SOL} SOL")
        print(f"   Scan Interval: {config.SCAN_INTERVAL_SECONDS} seconds")
        print(f"   Profit Target: {config.PROFIT_TARGET_PERCENTAGE:.1%}")
        print(f"   Stop Loss: {config.STOP_LOSS_PERCENTAGE:.1%}")
        print(f"   Max Daily Trades: {config.MAX_DAILY_TRADES}")
        print()

        # Initialize and start AURACLE
        bot = Auracle()
        bot.run()

    except Exception as e:
        print(f"❌ Failed to start AURACLE: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
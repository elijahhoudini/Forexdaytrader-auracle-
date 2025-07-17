"""
AURACLE: Unified Intelligence Core - Autonomous AI Solana Trading Bot
====================================================================

PHASES 1–∞: Autonomous Solana AI Trading Bot for Traveler 5798
Purpose: Generate profits to fund LLC & execute the Director's grand plan

Main system controller and trading loop for Traveler 5798's assistant.
Coordinates all subsystems for autonomous token discovery and trading.
"""

import time
import signal
import sys
import threading
import json
import os
import base58
import logging
import asyncio
import requests
import aiofiles
import cryptography.fernet
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.transaction import Transaction
from solders.instruction import Instruction
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.pubkey import Pubkey
from solana.rpc.commitment import Confirmed

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
    AURACLE Unified Intelligence Core - Main system controller.

    Mission: Generate profits to fund LLC & execute Traveler 5798's grand plan

    Orchestrates autonomous trading operations by coordinating:
    - Token scanning and discovery
    - Risk assessment and fraud detection
    - Trade execution and position management
    - LLC funding goal tracking
    - Logging and performance monitoring
    """

    def __init__(self):
        """Initialize AURACLE Unified Intelligence Core with all components."""
        print("=" * 60)
        print(f"🚀 INITIALIZING {config.BOT_NAME} UNIFIED INTELLIGENCE CORE v{config.BOT_VERSION}")
        print(f"👤 Traveler ID: {config.TRAVELER_ID}")
        print(f"🎯 Mission: Generate profits to fund LLC & execute the Director's grand plan")
        print(f"🤖 Mode: {'Autonomous' if config.AUTONOMOUS_MODE else 'Manual'}")
        print(f"📊 Trading: {config.get_trading_mode_string()}")
        print("=" * 60)

        # Unified Intelligence Core Metrics
        self.llc_reserve = 0.0
        self.total_profit = 0.0
        self.daily_log = []
        self.LLC_GOAL_SOL = float(os.getenv("LLC_GOAL_SOL", "500"))  # 500 SOL goal for LLC funding
        self.profit_target_multiplier = float(os.getenv("PROFIT_TARGET_MULTIPLIER", "1.3"))
        self.stop_loss_multiplier = float(os.getenv("STOP_LOSS_MULTIPLIER", "0.85"))

        # Enhanced backup and encryption system
        self.backup_folder = "auracle_backups"
        self.llc_paperwork_folder = "AURACLE_LLC"
        self.encryption_key = os.getenv("AURACLE_ENC_KEY")
        self.fernet = None
        if self.encryption_key:
            try:
                self.fernet = cryptography.fernet.Fernet(self.encryption_key.encode())
                print("🔐 Encryption system initialized")
            except Exception as e:
                print(f"⚠️ Encryption initialization failed: {e}")

        # Solana client for advanced operations
        self.solana_client = None
        self.keypair = None
        if hasattr(config, 'WALLET_PRIVATE_KEY') and config.WALLET_PRIVATE_KEY:
            try:
                self.solana_client = AsyncClient("https://api.mainnet-beta.solana.com")
                private_key_bytes = base58.b58decode(config.WALLET_PRIVATE_KEY)
                self.keypair = Keypair.from_bytes(private_key_bytes)
                print("🌐 Advanced Solana client initialized")
            except Exception as e:
                print(f"⚠️ Advanced Solana client initialization failed: {e}")

        # Mission statement for Traveler 5798
        self.mission_statement = (
            "Generate autonomous profits through intelligent Solana trading to fund "
            f"LLC incorporation. Target: {self.LLC_GOAL_SOL} SOL reserve for business formation."
        )

        # Initialize core components
        self.logger = AuracleLogger()
        self.wallet = Wallet()
        self.trade_handler = TradeHandler(self.wallet, auracle_instance=self)
        self.scanner = TokenScanner(self.trade_handler, self)  # Pass self to scanner
        self.risk = RiskEvaluator()

        # Enhanced Telegram integration for unified intelligence
        self.telegram_bot = None
        if config.TELEGRAM_ENABLED and config.TELEGRAM_BOT_TOKEN:
            try:
                self.telegram_bot = AuracleTelegramBot(
                    config.TELEGRAM_BOT_TOKEN, 
                    config.TELEGRAM_CHAT_ID
                )
                self.telegram_bot.set_auracle_bot(self)
                print("✅ Unified Intelligence Telegram integration initialized")
                # Send startup notification safely
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.create_task(self.send_intelligence_update(
                            f"🤖 AURACLE UNIFIED INTELLIGENCE CORE ONLINE\n"
                            f"👤 Traveler ID: {config.TRAVELER_ID}\n"
                            f"🎯 Mission: Fund LLC ({self.LLC_GOAL_SOL} SOL goal)\n"
                            f"💰 Current Reserve: {self.llc_reserve:.4f} SOL\n"
                            f"📊 Mode: {config.get_trading_mode_string()}"
                        ))
                    else:
                        # No event loop, use synchronous telegram bot
                        message = (f"🤖 AURACLE UNIFIED INTELLIGENCE CORE ONLINE\n"
                                 f"👤 Traveler ID: {config.TRAVELER_ID}\n"
                                 f"🎯 Mission: Fund LLC ({self.LLC_GOAL_SOL} SOL goal)\n"
                                 f"💰 Current Reserve: {self.llc_reserve:.4f} SOL\n"
                                 f"📊 Mode: {config.get_trading_mode_string()}")
                        self.telegram_bot.send_message_safe(message)
                except Exception as e:
                    print(f"⚠️ Startup notification failed: {e}")
            except Exception as e:
                print(f"⚠️ Telegram bot initialization failed: {e}")

        # System state
        self.running = False
        self.trading_active = True
        self.stats = {
            "scans_completed": 0,
            "tokens_evaluated": 0,
            "trades_executed": 0,
            "llc_contributions": 0,
            "start_time": datetime.utcnow()
        }

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        print("✅ AURACLE Unified Intelligence Core initialization complete")
        self.logger.log_system("AURACLE Unified Intelligence Core initialized successfully")

    def run(self):
        """
        Enhanced main trading loop with unified intelligence features.

        Continuously scans for tokens, evaluates them, and executes trades
        based on the configured strategy and risk parameters. Includes
        LLC funding tracking and intelligent monitoring.
        """
        import asyncio

        self.running = True
        session_start = datetime.utcnow()

        self.logger.log_system("AURACLE Unified Intelligence Core starting")
        print(f"🚀 Starting Auracle System - Traveler {config.TRAVELER_ID}")
        print(f"🎯 Mission: {self.mission_statement}")
        print(f"💰 LLC Goal: {self.LLC_GOAL_SOL} SOL")
        print(f"📊 Current Reserve: {self.llc_reserve:.4f} SOL")
        print("🔄 Starting main trading loop...")

        # Start Telegram bot in background thread
        if self.telegram_bot:
            telegram_thread = threading.Thread(target=self.telegram_bot.start, daemon=True)
            telegram_thread.start()
            self.send_startup_notification()

        # Send startup intelligence update
        async def send_startup_intelligence():
            await self.send_intelligence_update(
                f"🤖 Auracle System Online - Traveler {config.TRAVELER_ID}\n"
                f"🎯 Mission: {self.mission_statement}\n"
                f"💰 LLC Goal: {self.LLC_GOAL_SOL} SOL\n"
                f"📊 Current Reserve: {self.llc_reserve:.4f} SOL\n"
                f"🌐 Network Health: Checking..."
            )

        # Start async scanner loop with intelligence features
        try:
            asyncio.run(self._async_main_loop_with_intelligence())
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
            print(f"   LLC Contributions: {self.stats['llc_contributions']}")
            print(f"   LLC Reserve: {self.llc_reserve:.4f} SOL")
            print("🏁 AURACLE - Session Ended")
            print("=" * 60)

    async def _async_main_loop_with_intelligence(self):
        """Enhanced async main loop with unified intelligence features and automated backups."""
        scan_count = 0
        last_status_time = time.time()
        last_backup_time = time.time()
        position_monitor_interval = 10  # Monitor positions every 10 seconds
        iteration_count = 0

        # Send startup intelligence update
        network_healthy = await self.check_solana_network_health()
        await self.send_intelligence_update(
            f"🤖 Auracle System Online - Traveler {config.TRAVELER_ID}\n"
            f"🎯 Mission: {self.mission_statement}\n"
            f"💰 LLC Goal: {self.LLC_GOAL_SOL} SOL\n"
            f"📊 Current Reserve: {self.llc_reserve:.4f} SOL\n"
            f"🌐 Network Health: {'✅ Good' if network_healthy else '⚠️ Degraded'}\n"
            f"🔐 Encryption: {'✅ Enabled' if self.fernet else '⚠️ Disabled'}"
        )

        # Start scanner task
        scanner_task = asyncio.create_task(self.scanner.scan_loop())

        try:
            while self.running:
                scan_count += 1
                iteration_count += 1

                # Frequent position monitoring for profit optimization
                await self.trade_handler.monitor_positions()

                # Update statistics
                self.stats["scans_completed"] += 1

                # Advanced token scanning with enhanced filters
                if iteration_count % 6 == 0:  # Every minute
                    advanced_tokens = await self.advanced_token_scan()
                    if advanced_tokens:
                        # Process high-scoring tokens
                        for token in advanced_tokens[:1]:  # Process only the best token
                            diversification_weight = self.calculate_diversification_weight()
                            if diversification_weight > 0:
                                await self._process_advanced_token(token, diversification_weight)

                # Send periodic status updates with profit metrics
                if time.time() - last_status_time > 180:  # Every 3 minutes
                    self.send_status_update()
                    self._display_enhanced_portfolio_status()
                    last_status_time = time.time()

                # Network health check every 5 minutes (30 iterations)
                if iteration_count % 30 == 0:
                    network_healthy = await self.check_solana_network_health()
                    if not network_healthy:
                        print("⚠️ Network issues detected, continuing monitoring...")

                # Automated encrypted backups every 30 minutes
                if time.time() - last_backup_time > 1800:  # 30 minutes
                    await self.create_automated_backup()
                    last_backup_time = time.time()

                # Daily intelligence log and LLC report every 24 hours
                if iteration_count % 8640 == 0:  # 24 hours * 60 minutes * 6 (10-second intervals)
                    self.save_daily_intelligence_log()
                    self.generate_llc_report()

                    await self.send_intelligence_update(
                        f"📊 Daily Report - Traveler {config.TRAVELER_ID}\n"
                        f"💰 LLC Progress: {(self.llc_reserve / self.LLC_GOAL_SOL) * 100:.1f}%\n"
                        f"📈 Total Profit: {self.total_profit:.4f} SOL\n"
                        f"🎯 Trades Today: {len(self.daily_log)}\n"
                        f"📄 LLC Report Generated"
                    )

                # Check for LLC funding goal achievement
                if self.llc_reserve >= self.LLC_GOAL_SOL and self.stats.get("llc_goal_achieved") != True:
                    self.stats["llc_goal_achieved"] = True
                    await self.send_intelligence_update(
                        f"🏆 LLC FUNDING GOAL ACHIEVED! 🏆\n"
                        f"💰 Reserve: {self.llc_reserve:.4f} SOL\n"
                        f"📋 Business formation ready!\n"
                        f"📄 Final LLC report being generated..."
                    )
                    self.generate_llc_report()  # Generate final report

                # Sleep for optimized monitoring interval
                await asyncio.sleep(position_monitor_interval)

        except Exception as e:
            self.logger.log_error(f"Main loop error: {str(e)}")
            print(f"❌ Main loop error: {str(e)}")
            await self.send_intelligence_update(
                f"❌ Critical Error - Traveler {config.TRAVELER_ID}\n"
                f"🔧 Error: {str(e)[:100]}...\n"
                f"🔄 Attempting recovery..."
            )
        finally:
            # Cancel both scanner and sniper tasks
            scanner_task.cancel()


            try:
                await scanner_task
            except asyncio.CancelledError:
                pass


            # Stop sniper gracefully

            pass

    async def _async_main_loop(self):
        """Enhanced async main loop with frequent position monitoring for profit optimization."""
        scan_count = 0
        last_status_time = time.time()
        position_monitor_interval = 10  # Monitor positions every 10 seconds for profit capture

        # Start scanner task
        import asyncio
        scanner_task = asyncio.create_task(self.scanner.scan_loop())

        try:
            while self.running:
                scan_count += 1

                # Frequent position monitoring for profit optimization
                await self.trade_handler.monitor_positions()

                # Update statistics
                self.stats["scans_completed"] += 1

                # Send periodic status updates with profit metrics
                if time.time() - last_status_time > 180:  # Every 3 minutes (more frequent)
                    self.send_status_update()
                    self._display_enhanced_portfolio_status()
                    last_status_time = time.time()

                # Sleep for optimized monitoring interval
                await asyncio.sleep(position_monitor_interval)

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

    async def _process_token(self, token: Dict[str, Any]):
        """
        Process a single token through the trading pipeline with LLC contribution tracking.

        Args:
            token (Dict): Token data to process
        """
        try:
            # Enhanced risk evaluation with blacklist check
            if self.is_risky_token(token.get("symbol", "")):
                self.logger.log_flag(
                    token["mint"], 
                    f"Token flagged as risky: {token.get('symbol', 'Unknown')}", 
                    token
                )
                return

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

                success = await self.trade_handler.buy_token(token, trade_amount)

                if success:
                    self.stats["trades_executed"] += 1
                    self.logger.log_trade("BUY", token, trade_amount)

                    # Track trade for daily log
                    self.daily_log.append({
                        "timestamp": datetime.utcnow().isoformat(),
                        "action": "BUY",
                        "symbol": token.get("symbol", "Unknown"),
                        "amount_sol": trade_amount,
                        "mint": token["mint"]
                    })

                    # Send Telegram notification if configured
                    if self.telegram_bot:
                        symbol = token.get("symbol", "Unknown")
                        message = f"✅ AURACLE BUY: {symbol} - {trade_amount} SOL"
                        try:
                            self.telegram_bot.send_message(message)
                        except:
                            pass  # Don't let telegram errors stop trading

                    # Send intelligence update for significant trades
                    if trade_amount >= config.MAX_BUY_AMOUNT_SOL * 0.5:  # For trades >= 50% of max
                        await self.send_intelligence_update(
                            f"💎 Significant Trade Executed\n"
                            f"🪙 Token: {token.get('symbol', 'Unknown')}\n"
                            f"💰 Amount: {trade_amount:.4f} SOL\n"
                            f"🎯 Confidence: {token.get('ai_confidence', 0):.1f}%"
                        )
                else:
                    self.logger.log_trade("BUY_FAILED", token, trade_amount)

        except Exception as e:
            self.logger.log_error(f"Error processing token {token.get('mint', 'unknown')}: {str(e)}")
            await self.send_intelligence_update(
                f"⚠️ Token Processing Error\n"
                f"🪙 Token: {token.get('symbol', 'Unknown')}\n"
                f"❌ Error: {str(e)[:50]}..."
            )

    async def _process_advanced_token(self, token: Dict[str, Any], trade_amount: float):
        """Process token with advanced intelligence and monitoring."""
        try:
            symbol = token["baseToken"]["symbol"]
            token_mint_str = token["baseToken"]["address"]
            price_usd = float(token.get("priceUsd", 0))
            auracle_score = token.get("auracle_score", 0)

            # Enhanced risk evaluation with Auracle scoring
            if auracle_score < 0.3:  # Minimum Auracle score threshold
                self.logger.log_flag(
                    token_mint_str, 
                    f"Token {symbol} below Auracle score threshold: {auracle_score:.3f}", 
                    token
                )
                return

            # Check if already holding this token
            if symbol in [pos.get('symbol') for pos in self.trade_handler.open_positions.values()]:
                return

            # Advanced buy decision with enhanced criteria
            if self.should_buy_advanced_token(token) and self.trading_active:
                success = await self.buy_advanced_token(token, trade_amount)

                if success:
                    self.stats["trades_executed"] += 1

                    # Track trade for daily log
                    trade_entry = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "action": "BUY",
                        "symbol": symbol,
                        "amount_sol": trade_amount,
                        "mint": token_mint_str,
                        "entry_price_usd": price_usd,
                        "auracle_score": auracle_score,
                        "confidence": "HIGH" if auracle_score > 0.7 else "MEDIUM"
                    }
                    self.daily_log.append(trade_entry)

                    # Start monitoring this position
                    asyncio.create_task(self.monitor_and_sell_advanced(token, trade_amount))

                    # Send intelligence update for trades
                    await self.send_intelligence_update(
                        f"💎 Advanced Trade Executed\n"
                        f"🪙 Token: {symbol}\n"
                        f"💰 Amount: {trade_amount:.4f} SOL\n"
                        f"📊 Auracle Score: {auracle_score:.3f}\n"
                        f"💵 Entry Price: ${price_usd:.6f}"
                    )

        except Exception as e:
            self.logger.log_error(f"Error processing advanced token: {e}")
            await self.send_intelligence_update(
                f"⚠️ Advanced Token Processing Error\n"
                f"🪙 Token: {token.get('baseToken', {}).get('symbol', 'Unknown')}\n"
                f"❌ Error: {str(e)[:50]}..."
            )

    def should_buy_advanced_token(self, token: Dict[str, Any]) -> bool:
        """Advanced token evaluation with multiple criteria."""
        try:
            # Check daily trade limit
            if self.daily_trades >= config.MAX_DAILY_TRADES:
                return False

            # Auracle score check
            auracle_score = token.get("auracle_score", 0)
            if auracle_score < 0.4:  # Minimum score for buying
                return False

            # Enhanced liquidity and volume checks
            liquidity = float(token.get("liquidity", {}).get("usd", 0))
            volume_24h = float(token.get("volumeUsd24h", 0))

            if liquidity < 20000 or volume_24h < 15000:
                return False

            # Price stability check
            price_change_24h = abs(float(token.get("priceChange24h", 0)))
            if price_change_24h > 150:  # Too volatile
                return False

            return True

        except Exception as e:
            self.logger.log_error(f"Advanced token evaluation failed: {e}")
            return False

    async def buy_advanced_token(self, token: Dict[str, Any], amount_sol: float) -> bool:
        """Execute advanced token purchase with proper transaction handling."""
        try:
            symbol = token["baseToken"]["symbol"]
            token_mint_str = token["baseToken"]["address"]

            if config.get_demo_mode():
                # Demo mode - simulate purchase
                print(f"📊 DEMO BUY: {symbol} - {amount_sol:.4f} SOL")
                return True

            # Real trading mode - create and send transaction
            if self.solana_client and self.keypair:
                token_mint = Pubkey.from_string(token_mint_str)
                transaction = await self.create_swap_transaction(token_mint, amount_sol)

                if transaction:
                    tx_signature = await self.send_transaction(transaction)
                    if tx_signature:
                        print(f"✅ BUY: {symbol} - {amount_sol:.4f} SOL (Tx: {tx_signature})")
                        return True

            return False

        except Exception as e:
            self.logger.log_error(f"Advanced token purchase failed: {e}")
            return False

    async def monitor_and_sell_advanced(self, token: Dict[str, Any], buy_amount: float):
        """Advanced position monitoring with profit tracking and automated selling."""
        try:
            symbol = token["baseToken"]["symbol"]
            entry_price = float(token.get("priceUsd", 0))
            max_hold_minutes = 60
            elapsed_minutes = 0

            while elapsed_minutes < max_hold_minutes:
                # Get current price from advanced scan
                current_tokens = await self.advanced_token_scan()
                current_token = next((t for t in current_tokens if t["baseToken"]["symbol"] == symbol), None)

                if not current_token:
                    await asyncio.sleep(30)
                    elapsed_minutes += 0.5
                    continue

                current_price = float(current_token.get("priceUsd", entry_price))
                profit_ratio = current_price / entry_price if entry_price > 0 else 1.0

                # Profit target reached
                if profit_ratio >= self.profit_target_multiplier:
                    profit_sol = buy_amount * (profit_ratio - 1)
                    await self.sell_advanced_token(current_token, buy_amount, "PROFIT_TARGET")

                    # Track LLC contribution
                    self.track_llc_contribution(profit_sol)

                    await self.send_intelligence_update(
                        f"💰 PROFIT SELL: {symbol}\n"
                        f"📈 Profit: {profit_ratio:.2%}\n"
                        f"💎 Profit SOL: {profit_sol:.4f}\n"
                        f"🏆 LLC Contribution: {min(profit_sol, self.LLC_GOAL_SOL - self.llc_reserve):.4f}"
                    )
                    return profit_sol

                # Stop loss triggered
                elif profit_ratio <= self.stop_loss_multiplier:
                    loss_sol = buy_amount * (1 - profit_ratio)
                    await self.sell_advanced_token(current_token, buy_amount, "STOP_LOSS")

                    await self.send_intelligence_update(
                        f"🛑 STOP LOSS: {symbol}\n"
                        f"📉 Loss: {profit_ratio:.2%}\n"
                        f"💸 Loss SOL: {loss_sol:.4f}"
                    )
                    return -loss_sol

                await asyncio.sleep(30)
                elapsed_minutes += 0.5

            # Timeout - sell at current price
            profit_sol = buy_amount * (profit_ratio - 1)
            await self.sell_advanced_token(current_token or token, buy_amount, "TIMEOUT")

            if profit_sol > 0:
                self.track_llc_contribution(profit_sol)

            return profit_sol

        except Exception as e:
            self.logger.log_error(f"Advanced monitoring failed: {e}")
            return 0.0

    async def sell_advanced_token(self, token: Dict[str, Any], amount_sol: float, reason: str) -> bool:
        """Execute advanced token sale."""
        try:
            symbol = token["baseToken"]["symbol"]

            if config.get_demo_mode():
                print(f"📊 DEMO SELL: {symbol} - {amount_sol:.4f} SOL ({reason})")
                return True

            # Real trading mode
            if self.solana_client and self.keypair:
                token_mint_str = token["baseToken"]["address"]
                token_mint = Pubkey.from_string(token_mint_str)
                transaction = await self.create_swap_transaction(token_mint, amount_sol)

                if transaction:
                    tx_signature = await self.send_transaction(transaction)
                    if tx_signature:
                        print(f"✅ SELL: {symbol} - {amount_sol:.4f} SOL ({reason}) (Tx: {tx_signature})")
                        return True

            return False

        except Exception as e:
            self.logger.log_error(f"Advanced token sale failed: {e}")
            return False

    async def create_automated_backup(self):
        """Create automated encrypted backup of all trading data."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_data = {
                "timestamp": timestamp,
                "traveler_id": config.TRAVELER_ID,
                "portfolio": dict(self.trade_handler.open_positions),
                "daily_log": self.daily_log.copy(),
                "total_profit": self.total_profit,
                "llc_reserve": self.llc_reserve,
                "stats": self.stats.copy(),
                "trading_session": {
                    "session_start": self.stats["start_time"].isoformat(),
                    "trades_executed": self.stats["trades_executed"],
                    "llc_contributions": self.stats["llc_contributions"]
                }
            }

            filename = f"automated_backup_{timestamp}.json"
            backup_path = await self.save_encrypted_backup(filename, backup_data)

            if backup_path:
                self.logger.log_system(f"Automated backup created: {backup_path}")

                # Clean up old backups (keep last 10)
                await self.cleanup_old_backups()

        except Exception as e:
            print(f"❌ Automated backup failed: {e}")

    async def cleanup_old_backups(self, keep_count: int = 10):
        """Clean up old backup files, keeping only the most recent ones."""
        try:
            if not os.path.exists(self.backup_folder):
                return

            backup_files = [f for f in os.listdir(self.backup_folder) if f.startswith("automated_backup_")]
            backup_files.sort(reverse=True)  # Sort by name (timestamp), newest first

            # Remove old backups
            for old_backup in backup_files[keep_count:]:
                old_path = os.path.join(self.backup_folder, old_backup)
                os.remove(old_path)
                print(f"🗑️ Removed old backup: {old_backup}")

        except Exception as e:
            print(f"⚠️ Backup cleanup failed: {e}")

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
        """Enhanced graceful shutdown procedure with intelligence reporting."""
        print("\n🔄 Shutting down AURACLE Unified Intelligence Core...")

        try:
            # Send final intelligence update
            final_llc_percentage = (self.llc_reserve / self.LLC_GOAL_SOL) * 100

            if self.telegram_bot:
                try:
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    # Send final intelligence report
                    loop.run_until_complete(self.send_intelligence_update(
                        f"🛑 Auracle System Shutdown - Traveler {config.TRAVELER_ID}\n"
                        f"💰 Final LLC Reserve: {self.llc_reserve:.4f} SOL ({final_llc_percentage:.1f}%)\n"
                        f"📊 Session Profit: {self.total_profit:.4f} SOL\n"
                        f"🎯 Trades Executed: {self.stats['trades_executed']}\n"
                        f"🏆 LLC Contributions: {self.stats['llc_contributions']}"
                    ))

                    loop.close()
                except Exception as e:
                    print(f"⚠️ Final intelligence update failed: {e}")

            # Close any open positions if in demo mode
            if config.get_demo_mode():
                import asyncio
                # Create a new event loop for shutdown cleanup
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                # Close all open positions
                for mint in list(self.tradehandler.open_positions.keys()):
                    try:
                        result = loop.run_until_complete(self.trade_handler.sell_token(mint, "shutdown"))
                        if result and result.get("profit_sol", 0) > 0:
                            # Track final profits for LLC contribution
                            self.track_llc_contribution(result["profit_sol"])
                    except Exception as e:
                        print(f"⚠️ Error closing position {mint}: {e}")

                loop.close()

            # Save final intelligence log
            final_log_file = self.save_daily_intelligence_log()
            if final_log_file:
                print(f"📄 Final intelligence log saved: {final_log_file}")

            # Log session summary
            session_summary = self.logger.get_session_summary()
            self.logger.log_system("AURACLE session ended", session_summary)

            # Enhanced final status report
            print("\n📊 Final Session Report:")
            print(f"   Scans Completed: {self.stats['scans_completed']}")
            print(f"   Tokens Evaluated: {self.stats['tokens_evaluated']}")
            print(f"   Trades Executed: {self.stats['trades_executed']}")
            print(f"   LLC Contributions: {self.stats['llc_contributions']}")
            print(f"   LLC Reserve: {self.llc_reserve:.4f} SOL ({final_llc_percentage:.1f}%)")
            print(f"   Total Profit: {self.total_profit:.4f} SOL")
            print(f"   Session Duration: {datetime.utcnow() - self.stats['start_time']}")

        except Exception as e:
            print(f"⚠️ Error during shutdown: {e}")

        finally:
            print("=" * 60)
            print("🤖 AURACLE - Traveler 5798's Unified Intelligence Core - Session Ended")
            print(f"🎯 Mission Progress: LLC Reserve {(self.llc_reserve / self.LLC_GOAL_SOL) * 100:.1f}% Complete")
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

    def _display_enhanced_portfolio_status(self):
        """Display enhanced portfolio status with LLC funding progress."""
        try:
            # Get portfolio data
            portfolio = getattr(self.trade_handler, 'open_positions', {})

            # Calculate portfolio value
            portfolio_value = 0.0
            for position in portfolio.values():
                portfolio_value += position.get('current_value', 0.0)

            # Display enhanced status
            print(f"\n📈 PORTFOLIO STATUS: {len(portfolio)} positions")
            print(f"💰 Total Value: {portfolio_value:.4f} SOL")
            print(f"📊 Total Profit: {self.total_profit:.4f} SOL")
            print(f"🏦 LLC Reserve: {self.llc_reserve:.4f} SOL ({(self.llc_reserve / self.LLC_GOAL_SOL) * 100:.1f}%)")
            print(f"🎯 LLC Goal: {self.LLC_GOAL_SOL:.1f} SOL")

            # Show top positions
            if portfolio:
                sorted_positions = sorted(portfolio.items(), key=lambda x: x[1].get('current_value', 0), reverse=True)
                print("🔝 Top positions:")
                for i, (symbol, position) in enumerate(sorted_positions[:3]):
                    value = position.get('current_value', 0)
                    print(f"   {i+1}. {symbol}: {value:.4f} SOL")

            print()

        except Exception as e:
            self.logger.log_error(f"Portfolio status display failed: {e}")
            print(f"❌ Portfolio status display failed: {e}")

    async def send_intelligence_update(self, message: str):
        """Send unified intelligence updates via Telegram."""
        try:
            if self.telegram_bot:
                import asyncio
                # Use asyncio to send message without blocking
                asyncio.create_task(self.telegram_bot.send_message_safe(message))
            self.logger.log_system(f"Intelligence Update: {message}")
        except Exception as e:
            print(f"⚠️ Intelligence update failed: {e}")

    def track_llc_contribution(self, profit_sol: float):
        """Track profits toward LLC funding goal."""
        if profit_sol > 0:
            self.total_profit += profit_sol

            # Check if we've reached LLC funding milestones
            llc_percentage = (self.llc_reserve / self.LLC_GOAL_SOL) * 100

            if self.total_profit >= self.LLC_GOAL_SOL * 0.1:  # 10% of goal
                contribution = min(profit_sol, self.LLC_GOAL_SOL - self.llc_reserve)
                if contribution > 0 and self.llc_reserve < self.LLC_GOAL_SOL:
                    self.llc_reserve += contribution
                    self.stats["llc_contributions"] += 1

                    milestone_msg = ""
                    if llc_percentage >= 25 and llc_percentage < 30:
                        milestone_msg = "\n🎯 25% LLC funding milestone reached!"
                    elif llc_percentage >= 50 and llc_percentage < 55:
                        milestone_msg = "\n🎯 50% LLC funding milestone reached!"
                    elif llc_percentage >= 75 and llc_percentage < 80:
                        milestone_msg = "\n🎯 75% LLC funding milestone reached!"
                    elif llc_percentage >= 100:
                        milestone_msg = "\n🏆 LLC FUNDING GOAL ACHIEVED! Ready for incorporation!"

                    asyncio.create_task(self.send_intelligence_update(
                        f"💰 LLC CONTRIBUTION: {contribution:.4f} SOL\n"
                        f"📊 LLC Reserve: {self.llc_reserve:.4f}/{self.LLC_GOAL_SOL} SOL ({llc_percentage:.1f}%)\n"
                        f"💎 Total Profit: {self.total_profit:.4f} SOL{milestone_msg}"
                    ))

                    if self.llc_reserve >= self.LLC_GOAL_SOL:
                        self.logger.log_system("LLC funding goal achieved!")
                        # Reset profit tracker after reaching goal
                        self.total_profit = 0

    def save_daily_intelligence_log(self):
        """Save daily intelligence log with LLC funding progress."""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d')
            filename = f"data/auracle_intelligence_log_{timestamp}.json"

            intelligence_data = {
                "date": timestamp,
                "traveler_id": config.TRAVELER_ID,
                "mission_status": {
                    "llc_goal_sol": self.LLC_GOAL_SOL,
                    "llc_reserve": self.llc_reserve,
                    "total_profit": self.total_profit,
                    "funding_percentage": (self.llc_reserve / self.LLC_GOAL_SOL) * 100,
                    "llc_contributions": self.stats["llc_contributions"]
                },
                "trading_stats": self.stats.copy(),
                "daily_trades": self.daily_log.copy(),
                "portfolio_summary": self.trade_handler.get_portfolio_summary()
            }

            os.makedirs("data", exist_ok=True)
            with open(filename, "w") as f:
                json.dump(intelligence_data, f, indent=2, default=str)

            self.logger.log_system(f"Daily intelligence log saved: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Error saving daily intelligence log: {e}")
            return None

    def is_risky_token(self, token_name: str) -> bool:
        """Enhanced risk detection for suspicious tokens."""
        blacklist = [
            "rug", "scam", "honeypot", "jeet", "shitcoin", 
            "elon", "pepe", "moon", "safe", "baby", "doge",
            "cum", "pussy", "shit", "fuck", "damn"
        ]
        token_lower = token_name.lower()
        return any(word in token_lower for word in blacklist)

    async def check_solana_network_health(self) -> bool:
        """Check Solana network health for unified intelligence."""
        try:
            if self.solana_client:
                response = await self.solana_client.get_health()
                return response.get('result') == 'ok'
            else:
                # Fallback to existing wallet method
                balance = await self.wallet.get_balance("SOL")
                return balance is not None
        except Exception as e:
            self.logger.log_error(f"Solana network health check failed: {e}")
            await self.send_intelligence_update(
                f"⚠️ Network Issue Detected: {e}\n"
                f"🔄 Switching to backup monitoring mode"
            )
            return False

    async def save_encrypted_backup(self, filename: str, data: dict) -> str:
        """Save encrypted backup of critical trading data."""
        try:
            if not os.path.exists(self.backup_folder):
                os.makedirs(self.backup_folder)

            filepath = os.path.join(self.backup_folder, filename)
            json_bytes = json.dumps(data, indent=2, default=str).encode()

            if self.fernet:
                encrypted = self.fernet.encrypt(json_bytes)
                async with aiofiles.open(filepath, "wb") as f:
                    await f.write(encrypted)
                print(f"🔐 Encrypted backup saved: {filepath}")
            else:
                async with aiofiles.open(filepath, "w") as f:
                    await f.write(json.dumps(data, indent=2, default=str))
                print(f"📄 Backup saved: {filepath}")

            return filepath
        except Exception as e:
            print(f"❌ Backup save failed: {e}")
            return None

    async def load_encrypted_backup(self, filename: str) -> dict:
        """Load encrypted backup of trading data."""
        try:
            filepath = os.path.join(self.backup_folder, filename)
            if not os.path.exists(filepath):
                return None

            if self.fernet:
                async with aiofiles.open(filepath, "rb") as f:
                    encrypted = await f.read()
                decrypted = self.fernet.decrypt(encrypted)
                return json.loads(decrypted.decode())
            else:
                async with aiofiles.open(filepath, "r") as f:
                    return json.loads(await f.read())
        except Exception as e:
            print(f"❌ Backup load failed: {e}")
            return None

    def generate_llc_report(self) -> str:
        """Generate LLC paperwork and financial reports."""
        try:
            if not os.path.exists(self.llc_paperwork_folder):
                os.makedirs(self.llc_paperwork_folder)

            wallet_address = str(self.keypair.pubkey()) if self.keypair else "N/A"

            report = {
                "wallet_address": wallet_address,
                "date": datetime.now().isoformat(),
                "total_profit": self.total_profit,
                "llc_reserve": self.llc_reserve,
                "trades": self.daily_log.copy(),
                "llc_name": "AURACLE",
                "traveler_id": config.TRAVELER_ID,
                "funding_percentage": (self.llc_reserve / self.LLC_GOAL_SOL) * 100,
                "business_formation_ready": self.llc_reserve >= self.LLC_GOAL_SOL,
                "portfolio_summary": self.trade_handler.get_portfolio_summary()
            }

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.llc_paperwork_folder}/llc_report_{timestamp}.json"

            with open(filename, "w") as f:
                json.dump(report, f, indent=2, default=str)

            print(f"📄 LLC report generated: {filename}")
            return filename
        except Exception as e:
            print(f"❌ LLC report generation failed: {e}")
            return None

    def calculate_diversification_weight(self) -> float:
        """Calculate optimal portfolio diversification weight."""
        try:
            current_holdings = len(self.trade_handler.open_positions)
            max_positions = 5  # Maximum diversification limit

            if current_holdings >= max_positions:
                return 0.0  # Do not buy more tokens if at max diversification

            # Adjust buy amount based on available diversification slots
            base_amount = config.MAX_BUY_AMOUNT_SOL
            diversification_factor = (max_positions - current_holdings) / max_positions

            return base_amount * diversification_factor
        except Exception as e:
            print(f"❌ Diversification calculation failed: {e}")
            return config.MAX_BUY_AMOUNT_SOL

    async def advanced_token_scan(self) -> List[Dict[str, Any]]:
        """Advanced token scanning with enhanced filters."""
        try:
            url = "https://api.dexscreener.io/latest/dex/pairs/solana"
            response = requests.get(url, timeout=10)
            data = response.json()

            candidates = []
            for pair in data.get("pairs", []):
                try:
                    # Enhanced filtering criteria
                    liquidity = float(pair.get("liquidity", {}).get("usd", 0))
                    fdv = float(pair.get("fdv", 0))
                    name = pair["baseToken"]["name"].lower()
                    symbol = pair["baseToken"]["symbol"]
                    age_days = int(pair.get("ageHours", 0)) / 24  # Convert hours to days
                    vol_24h = float(pair.get("volumeUsd24h", 0))
                    price_change_24h = float(pair.get("priceChange24h", 0))

                    # Advanced heuristic filters
                    if (liquidity > 15000 and 
                        fdv < 5_000_000 and 
                        age_days > 1 and 
                        vol_24h > 10000 and 
                        abs(price_change_24h) < 200 and  # Avoid extreme volatility
                        not self.is_risky_token(name) and
                        not self.is_risky_token(symbol)):

                        # Add enhanced scoring
                        score = (
                            min(liquidity / 100000, 1.0) * 0.3 +  # Liquidity score
                            min(vol_24h / 50000, 1.0) * 0.3 +     # Volume score
                            min(age_days / 30, 1.0) * 0.2 +       # Age score
                            (1 - abs(price_change_24h) / 100) * 0.2  # Stability score
                        )

                        pair["auracle_score"] = score
                        candidates.append(pair)

                except (ValueError, KeyError, TypeError):
                    continue  # Skip malformed data

            # Sort by Auracle score descending
            candidates.sort(key=lambda x: x.get("auracle_score", 0), reverse=True)
            return candidates[:3]  # Return top 3 candidates

        except Exception as e:
            self.logger.log_error(f"Advanced token scan failed: {e}")
            return []

    async def create_swap_transaction(self, token_mint: Pubkey, amount_sol: float) -> Transaction:
        """Create advanced swap transaction with proper Solana instructions."""
        try:
            # Note: This is a simplified placeholder for swap transaction construction
            # In production, this should use Jupiter API or Serum/Raydium DEX instructions

            if not self.keypair:
                raise Exception("Keypair not available for transaction creation")

            transfer_instruction = Instruction(
                accounts=[
                    {"pubkey": self.keypair.pubkey(), "is_signer": True, "is_writable": True},
                    {"pubkey": token_mint, "is_signer": False, "is_writable": True},
                ],
                program_id=SYS_PROGRAM_ID,
                data=b"",  # Placeholder - should contain swap instruction data
            )

            transaction = Transaction([transfer_instruction])
            return transaction

        except Exception as e:
            self.logger.log_error(f"Transaction creation failed: {e}")
            return None

    async def send_transaction(self, transaction: Transaction) -> str:
        """Send transaction to Solana network with proper error handling."""
        try:
            if not self.solana_client or not self.keypair:
                raise Exception("Solana client or keypair not available")

            # Get recent blockhash
            recent_blockhash_resp = await self.solana_client.get_latest_blockhash()
            transaction.recent_blockhash = recent_blockhash_resp.value.blockhash

            # Sign transaction
            transaction.sign([self.keypair])

            # Send transaction
            response = await self.solana_client.send_raw_transaction(
                bytes(transaction)
            )

            # Confirm transaction
            await self.solana_client.confirm_transaction(response.value)
            return response.value

        except Exception as e:
            self.logger.log_error(f"Transaction send failed: {e}")
            return None

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
        
        # Initialize the AI trader with trade handler integration if needed
        # Note: Trader initialization is now handled inside the Auracle class
        bot.run()

    except Exception as e:
        print(f"❌ Failed to start AURACLE: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
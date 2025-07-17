"""
AURACLE Sniper Module
====================

Advanced sniping functionality for new token listings.
Integrates with Jupiter API for real trading execution.
"""

import asyncio
import time
import random
from datetime import datetime
from typing import Dict, Any, List, Optional
import config
from enhanced_discovery import EnhancedTokenDiscovery
from risk import RiskEvaluator
from jupiter_api import JupiterTradeExecutor
from wallet import Wallet
import logging

logger = logging.getLogger(__name__)

class AuracleTrader:
    """
    Advanced AI trading system for profitable token opportunities.

    Features:
    - Real-time token discovery
    - Risk assessment and filtering
    - Automated buy/sell execution
    - Profit tracking and optimization
    - Honeypot protection
    """

    def __init__(self, wallet: Optional[Wallet] = None, trade_handler=None):
        self.wallet = wallet or Wallet()
        self.trade_handler = trade_handler  # Integration with trade handler
        self.discovery = EnhancedTokenDiscovery()
        self.risk_evaluator = RiskEvaluator()
        self.jupiter_executor = JupiterTradeExecutor()

        # Sniper state
        self.active = False
        self.stats = {
            "tokens_scanned": 0,
            "trades_executed": 0,
            "successful_trades": 0,
            "total_profit": 0.0,
            "start_time": None
        }

        # Configuration
        self.min_liquidity = config.MIN_LIQUIDITY_USD
        self.max_buy_amount = config.MAX_BUY_AMOUNT_SOL
        self.profit_target = config.PROFIT_TARGET_PERCENTAGE
        self.stop_loss = config.STOP_LOSS_PERCENTAGE

        logger.info("🎯 AURACLE Sniper initialized with trade handler integration")

    async def start_sniping(self, amount_sol: float = 0.01, duration_minutes: int = 60):
        """
        Start autonomous sniping for specified duration.

        Args:
            amount_sol: Amount of SOL to use per trade
            duration_minutes: How long to run sniper
        """
        if self.active:
            logger.warning("Sniper is already active")
            return False

        self.active = True
        self.stats["start_time"] = time.time()

        logger.info(f"🎯 Starting sniper - Amount: {amount_sol} SOL, Duration: {duration_minutes}m")

        try:
            end_time = time.time() + (duration_minutes * 60)

            while self.active and time.time() < end_time:
                await self._snipe_cycle(amount_sol)
                await asyncio.sleep(config.SCAN_INTERVAL_SECONDS)

        except Exception as e:
            logger.error(f"Sniper error: {e}")
        finally:
            self.active = False
            logger.info("🎯 Sniper stopped")

        return True

    async def stop_sniping(self):
        """Stop the sniper"""
        self.active = False
        logger.info("🛑 Stopping sniper...")

    async def manual_snipe(self, amount_sol: float = 0.01) -> Dict[str, Any]:
        """
        Execute a single manual snipe.

        Args:
            amount_sol: Amount of SOL to use

        Returns:
            Snipe result dictionary
        """
        logger.info(f"🎯 Manual snipe - Amount: {amount_sol} SOL")

        try:
            # Discover tokens
            tokens = await self.discovery.discover_tokens()
            if not tokens:
                return {"success": False, "error": "No tokens discovered"}

            # Find best opportunity
            best_token = await self._find_best_opportunity(tokens)
            if not best_token:
                return {"success": False, "error": "No suitable tokens found"}

            # Execute trade
            result = await self._execute_snipe(best_token, amount_sol)

            # Update stats
            self.stats["trades_executed"] += 1
            if result["success"]:
                self.stats["successful_trades"] += 1

            return result

        except Exception as e:
            logger.error(f"Manual snipe error: {e}")
            return {"success": False, "error": str(e)}

    async def _snipe_cycle(self, amount_sol: float):
        """Single snipe cycle for autonomous mode"""
        try:
            # Discover tokens
            tokens = await self.discovery.discover_tokens()
            self.stats["tokens_scanned"] += len(tokens)

            if not tokens:
                logger.debug("No tokens found in this cycle")
                return

            # Process each token
            for token in tokens[:3]:  # Limit to top 3 to avoid spam
                if not self.active:
                    break

                # Check if token meets criteria
                if await self._should_snipe_token(token):
                    result = await self._execute_snipe(token, amount_sol)

                    if result["success"]:
                        logger.info(f"✅ Snipe successful: {token['symbol']}")
                        self.stats["successful_trades"] += 1

                        # Start monitoring for profit taking
                        asyncio.create_task(self._monitor_position(token, amount_sol))
                    else:
                        logger.warning(f"❌ Snipe failed: {token['symbol']} - {result.get('error', 'Unknown')}")

                    self.stats["trades_executed"] += 1

                    # Small delay between trades
                    await asyncio.sleep(2)

        except Exception as e:
            logger.error(f"Snipe cycle error: {e}")

    async def _find_best_opportunity(self, tokens: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find the best token opportunity from list"""
        best_token = None
        best_score = 0

        for token in tokens:
            if await self._should_snipe_token(token):
                score = token.get("opportunity_score", 0)
                if score > best_score:
                    best_score = score
                    best_token = token

        return best_token

    async def _should_snipe_token(self, token: Dict[str, Any]) -> bool:
        """Determine if token should be sniped"""
        try:
            # Basic checks
            if token.get("liquidity", 0) < self.min_liquidity:
                return False

            # Risk evaluation
            risk_result = self.risk_evaluator.evaluate(token)
            if not risk_result.get("safe", False):
                return False

            # Additional sniper-specific checks
            symbol = token.get("symbol", "")
            if len(symbol) < 2 or len(symbol) > 10:
                return False

            # Check for suspicious patterns
            suspicious_patterns = ["test", "fake", "rug", "honey", "scam"]
            if any(pattern in symbol.lower() for pattern in suspicious_patterns):
                return False

            # Volume/liquidity ratio
            volume = token.get("volume24h", 0)
            liquidity = token.get("liquidity", 1)
            if volume / liquidity < 0.01:  # Very low activity
                return False

            return True

        except Exception as e:
            logger.error(f"Error evaluating token for sniping: {e}")
            return False

    async def _execute_snipe(self, token: Dict[str, Any], amount_sol: float) -> Dict[str, Any]:
        """Execute the actual snipe transaction via trade handler"""
        try:
            symbol = token.get("symbol", "UNKNOWN")
            mint = token.get("mint", "")

            logger.info(f"🎯 Executing snipe: {symbol} - {amount_sol} SOL")

            # Use trade handler if available for integrated position management
            if self.trade_handler:
                # Mark token as sniper trade before buying
                token["sniper_trade"] = True
                token["sniper_source"] = "auto"

                success = await self.trade_handler.buy_token(token, amount_sol)

                if success:
                    # Mark the position as a sniper trade in the trade handler
                    if mint in self.trade_handler.open_positions:
                        self.trade_handler.open_positions[mint]["sniper_trade"] = True
                        self.trade_handler.open_positions[mint]["sniper_source"] = "auto"

                        # Track in sniper trades
                        self.trade_handler.sniper_trades[mint] = {
                            "entry_time": datetime.now(),
                            "source": "auto",
                            "symbol": symbol
                        }

                    return {
                        "success": True,
                        "token": symbol,
                        "mint": mint,
                        "amount": amount_sol,
                        "signature": f"sniper_{int(time.time())}",
                        "demo_mode": config.get_demo_mode(),
                        "timestamp": datetime.now().isoformat(),
                        "integrated": True
                    }
                else:
                    return {
                        "success": False,
                        "error": "Trade handler rejected snipe",
                        "token": symbol,
                        "integrated": True
                    }

            # Fallback to direct execution
            if config.get_demo_mode():
                # Demo mode - simulate transaction
                success = random.random() > 0.2  # 80% success rate

                if success:
                    return {
                        "success": True,
                        "token": symbol,
                        "mint": mint,
                        "amount": amount_sol,
                        "signature": f"demo_snipe_{int(time.time())}",
                        "demo_mode": True,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "error": "Demo transaction failed (simulated)",
                        "token": symbol,
                        "demo_mode": True
                    }
            else:
                # Real mode - execute via Jupiter
                result = await self.jupiter_executor.buy_token(mint, amount_sol)

                return {
                    "success": result["success"],
                    "token": symbol,
                    "mint": mint,
                    "amount": amount_sol,
                    "signature": result.get("signature", ""),
                    "error": result.get("error", ""),
                    "demo_mode": False,
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"Snipe execution error: {e}")
            return {
                "success": False,
                "error": str(e),
                "token": token.get("symbol", "UNKNOWN")
            }

    async def _monitor_position(self, token: Dict[str, Any], buy_amount: float):
        """Monitor position for profit taking"""
        try:
            symbol = token.get("symbol", "UNKNOWN")
            entry_price = token.get("price_usd", 0)

            logger.info(f"📊 Monitoring position: {symbol}")

            # Monitor for up to 1 hour
            start_time = time.time()
            max_monitor_time = 3600  # 1 hour

            while time.time() - start_time < max_monitor_time:
                if not self.active:
                    break

                # In demo mode, simulate price movement
                if config.get_demo_mode():
                    current_price = entry_price * random.uniform(0.85, 1.35)
                    price_change = (current_price - entry_price) / entry_price

                    # Check profit target
                    if price_change >= self.profit_target:
                        profit = buy_amount * price_change
                        logger.info(f"💰 Profit target hit: {symbol} - {price_change:.2%} profit")
                        self.stats["total_profit"] += profit
                        break

                    # Check stop loss
                    if price_change <= self.stop_loss:
                        loss = buy_amount * abs(price_change)
                        logger.info(f"🛑 Stop loss hit: {symbol} - {price_change:.2%} loss")
                        self.stats["total_profit"] -= loss
                        break

                await asyncio.sleep(30)  # Check every 30 seconds

        except Exception as e:
            logger.error(f"Position monitoring error: {e}")

    async def _monitor_sniper_position(self, token: Dict[str, Any], buy_amount: float):
        """Enhanced monitoring specifically for sniped positions with aggressive selling"""
        try:
            symbol = token.get("symbol", "UNKNOWN")
            mint = token.get("mint", "")
            entry_time = time.time()

            logger.info(f"🎯 Starting sniper position monitoring: {symbol}")

            # Sniper-specific settings (more aggressive)
            sniper_profit_target = 0.15  # 15% profit target
            sniper_stop_loss = -0.08     # 8% stop loss
            quick_profit_target = 0.05   # 5% quick profit in first 5 minutes
            max_hold_minutes = 30        # Maximum 30 minutes hold time

            while time.time() - entry_time < (max_hold_minutes * 60):
                if not self.active:
                    break

                age_minutes = (time.time() - entry_time) / 60

                # Check if position still exists in trade handler
                if self.trade_handler and mint not in self.trade_handler.open_positions:
                    logger.info(f"🔍 Sniper position {symbol} no longer in open positions")
                    break

                # Get current position data from trade handler
                if self.trade_handler and mint in self.trade_handler.open_positions:
                    position = self.trade_handler.open_positions[mint]
                    current_pnl_percent = position.get("current_pnl_percent", 0)

                    # Quick profit exit (first 5 minutes)
                    if age_minutes <= 5 and current_pnl_percent >= (quick_profit_target * 100):
                        logger.info(f"⚡ Sniper quick profit exit: {symbol} - {current_pnl_percent:.2f}% in {age_minutes:.1f}m")
                        await self.trade_handler.sell_token(mint, "sniper_quick_profit")
                        break

                    # Main profit target
                    if current_pnl_percent >= (sniper_profit_target * 100):
                        logger.info(f"🎯 Sniper profit target hit: {symbol} - {current_pnl_percent:.2f}%")
                        await self.trade_handler.sell_token(mint, "sniper_profit_target")
                        break

                    # Stop loss
                    if current_pnl_percent <= (sniper_stop_loss * 100):
                        logger.info(f"🛑 Sniper stop loss triggered: {symbol} - {current_pnl_percent:.2f}%")
                        await self.trade_handler.sell_token(mint, "sniper_stop_loss")
                        break

                    # Force exit after max hold time
                    if age_minutes >= max_hold_minutes:
                        logger.info(f"⏰ Sniper max hold time reached: {symbol} - Force selling")
                        await self.trade_handler.sell_token(mint, "sniper_timeout")
                        break

                    # Smart exit on declining momentum (after 10 minutes)
                    if (age_minutes > 10 and 
                        current_pnl_percent > 2 and  # Small profit
                        hasattr(position, 'highest_value') and
                        position.get('current_value', 0) < position.get('highest_value', 0) * 0.85):  # Down 15% from peak
                        logger.info(f"📉 Sniper smart exit on declining momentum: {symbol}")
                        await self.trade_handler.sell_token(mint, "sniper_momentum_decline")
                        break

                # Check every 10 seconds for sniper positions (more frequent monitoring)
                await asyncio.sleep(10)

            logger.info(f"🏁 Sniper position monitoring ended for {symbol}")

        except Exception as e:
            logger.error(f"Sniper position monitoring error for {symbol}: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get sniper statistics"""
        uptime = time.time() - self.stats["start_time"] if self.stats["start_time"] else 0

        return {
            "active": self.active,
            "uptime_seconds": uptime,
            "tokens_scanned": self.stats["tokens_scanned"],
            "trades_executed": self.stats["trades_executed"],
            "successful_trades": self.stats["successful_trades"],
            "success_rate": (self.stats["successful_trades"] / max(self.stats["trades_executed"], 1)) * 100,
            "total_profit": self.stats["total_profit"],
            "avg_profit_per_trade": self.stats["total_profit"] / max(self.stats["trades_executed"], 1)
        }

    async def close(self):
        """Clean up resources"""
        self.active = False
        await self.discovery.close()
        await self.jupiter_executor.close()

# Global trader instance
trader = AuracleTrader()

# Compatibility functions for existing code
async def start_sniper(amount_sol: float = 0.01, duration_minutes: int = 60):
    """Start the AI trader"""
    return await trader.start_sniping(amount_sol, duration_minutes)

async def stop_sniper():
    """Stop the AI trader"""
    return await trader.stop_sniping()

async def manual_snipe(amount_sol: float = 0.01):
    """Execute AI trade"""
    return await trader.manual_snipe(amount_sol)

def get_sniper_stats():
    """Get AI trader statistics"""
    return trader.get_stats()
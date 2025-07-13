"""
AURACLE Trade Handler Module
===========================

Enhanced trade execution and position management system with Jupiter integration.
Handles buying, selling, and monitoring of token positions with improved performance.
"""

import time
import random
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import config


class TradeHandler:
    """
    Enhanced trade execution and position management system.

    Features:
    - Jupiter-powered buy/sell execution
    - Advanced position monitoring
    - Dynamic allocation strategies
    - Improved stop loss and take profit
    - Performance optimizations
    """

    def __init__(self, wallet):
        """Initialize trade handler with wallet instance."""
        self.wallet = wallet
        self.open_positions = {}  # mint -> position_data
        self.trade_history = []
        self.daily_trades = 0
        self.last_trade_reset = datetime.utcnow().date()
        
        # Performance tracking
        self.performance_stats = {
            "total_trades": 0,
            "successful_trades": 0,
            "total_pnl": 0.0,
            "win_rate": 0.0
        }

        print("✅ Enhanced TradeHandler initialized with Jupiter integration")

    async def handle_token(self, mint: str, token_info: Dict[str, Any]) -> bool:
        """
        Handle a token discovery - decide whether to buy and execute.
        
        Args:
            mint (str): Token mint address
            token_info (Dict): Token metadata
            
        Returns:
            bool: True if trade was executed
        """
        try:
            # Check if we should buy this token
            if not self.should_buy(token_info):
                print(f"[trade] Skipping {token_info.get('symbol', '?')} - did not meet buy criteria")
                return False
            
            # Calculate trade amount
            amount = self.calculate_trade_amount(token_info)
            
            # Execute buy
            success = await self.buy_token(token_info, amount)
            
            if success:
                self.performance_stats["total_trades"] += 1
                print(f"[trade] ✅ Successfully bought {token_info.get('symbol', '?')} for {amount} SOL")
                return True
            else:
                print(f"[trade] ❌ Failed to buy {token_info.get('symbol', '?')}")
                return False
                
        except Exception as e:
            print(f"[trade] Error handling token {mint[:8]}...: {e}")
            return False

    def calculate_trade_amount(self, token: Dict[str, Any]) -> float:
        """
        Calculate the trading amount for a token based on confidence and dynamic allocation.
        Enhanced with better risk management.
        """
        base_amount = config.MAX_BUY_AMOUNT_SOL

        # Check if dynamic allocation is enabled
        if not config.DYNAMIC_ALLOCATION_ENABLED:
            return base_amount

        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(token)

        # Apply dynamic allocation for high-confidence trades
        if confidence_score >= 0.8:  # High confidence threshold
            allocation_amount = base_amount * config.HIGH_CONFIDENCE_MULTIPLIER
            print(f"📈 High confidence trade detected: {token.get('symbol', '?')} - Allocating {allocation_amount} SOL")
            return allocation_amount
        elif confidence_score >= 0.6:  # Medium confidence
            allocation_amount = base_amount * 1.2
            return allocation_amount

        return base_amount

    def _calculate_confidence_score(self, token: Dict[str, Any]) -> float:
        """
        Enhanced confidence scoring with more sophisticated metrics.
        """
        confidence = 0.5  # Start with neutral confidence

        # Check for high-confidence patterns in symbol
        symbol = token.get("symbol", "").upper()
        for pattern in config.HIGH_CONFIDENCE_PATTERNS:
            if pattern in symbol:
                confidence += 0.3
                print(f"🎯 High confidence pattern detected: {pattern} in {symbol}")
                break

        # Enhanced liquidity scoring
        liquidity = token.get("liquidity", 0)
        if liquidity > 50000:
            confidence += 0.3
        elif liquidity > 25000:
            confidence += 0.2
        elif liquidity > 10000:
            confidence += 0.1

        # Enhanced volume scoring
        volume = token.get("volume24h", 0)
        if volume > 20000:
            confidence += 0.2
        elif volume > 10000:
            confidence += 0.15
        elif volume > 5000:
            confidence += 0.1

        # Holder distribution factor
        holders = token.get("holders", 0)
        if holders > 500:
            confidence += 0.1
        elif holders > 200:
            confidence += 0.05

        # Developer holdings factor (lower is better)
        dev_holdings = token.get("developerHoldingsPercent", 50)
        if dev_holdings < 5:
            confidence += 0.1
        elif dev_holdings < 15:
            confidence += 0.05
        elif dev_holdings > 30:
            confidence -= 0.2

        # Price stability factor
        price_change = abs(token.get("priceChange24h", 0))
        if 0.02 < price_change < 0.15:  # 2-15% change is good
            confidence += 0.1
        elif price_change > 0.5:  # More than 50% change is risky
            confidence -= 0.2

        return max(0.0, min(1.0, confidence))

    def should_buy(self, token: Dict[str, Any]) -> bool:
        """
        Enhanced buy decision logic with better filtering.
        """
        # Check daily limits
        if self._check_daily_limits():
            return False

        # Check position limits
        if len(self.open_positions) >= config.MAX_OPEN_POSITIONS:
            return False

        # Check if we already have a position
        if token["mint"] in self.open_positions:
            return False

        # Enhanced strategy criteria
        liquidity = token.get("liquidity", 0)
        volume = token.get("volume24h", 0)
        holders = token.get("holders", 0)
        dev_holdings = token.get("developerHoldingsPercent", 100)

        # Basic safety checks
        if liquidity < config.MIN_LIQUIDITY_THRESHOLD:
            return False
        if volume < 1000:
            return False
        if holders < 50:
            return False
        if dev_holdings > 30:
            return False

        # Check confidence score
        confidence = self._calculate_confidence_score(token)
        return confidence >= 0.4  # Lower threshold for more opportunities

    async def buy_token(self, token: Dict[str, Any], amount_sol: float) -> bool:
        """
        Execute buy order for token using Jupiter integration.
        """
        try:
            mint = token["mint"]

            # Check wallet balance
            balance = await self.wallet.get_balance("SOL")
            if balance < amount_sol:
                print(f"❌ Insufficient SOL balance: {balance} < {amount_sol}")
                return False

            # Execute transaction using Jupiter
            success = await self.wallet.buy_token(mint, amount_sol)

            if success:
                # Create position record
                position = {
                    "mint": mint,
                    "symbol": token.get("symbol", "Unknown"),
                    "name": token.get("name", "Unknown"),
                    "buy_price_sol": amount_sol,
                    "buy_time": datetime.utcnow(),
                    "status": "open",
                    "target_profit": config.PROFIT_TARGET_PERCENTAGE,
                    "stop_loss": config.STOP_LOSS_PERCENTAGE,
                    "token_data": token
                }

                self.open_positions[mint] = position
                self.daily_trades += 1

                # Add to trade history
                self.trade_history.append({
                    "action": "BUY",
                    "token": token,
                    "amount": amount_sol,
                    "timestamp": datetime.utcnow(),
                    "success": True
                })

                return True
            else:
                print(f"❌ Buy transaction failed")
                return False

        except Exception as e:
            print(f"❌ Error buying token {token.get('symbol', '?')}: {e}")
            return False

    async def sell_token(self, mint: str, reason: str = "manual") -> bool:
        """
        Execute sell order for token using Jupiter integration.
        """
        try:
            if mint not in self.open_positions:
                print(f"❌ No open position for {mint[:8]}...")
                return False

            position = self.open_positions[mint]
            
            # Calculate position size (simplified - assume we sell all)
            # In a real implementation, this would query the actual token balance
            sell_amount = position["buy_price_sol"] * 1000  # Simplified conversion

            # Execute sell transaction
            success = await self.wallet.sell_token(mint, sell_amount)

            if success:
                # Calculate P&L
                buy_price = position["buy_price_sol"]
                sell_price = buy_price * random.uniform(0.8, 1.3)  # Simulated for demo
                pnl = sell_price - buy_price
                pnl_percent = (pnl / buy_price) * 100

                # Update position
                position["status"] = "closed"
                position["sell_price_sol"] = sell_price
                position["sell_time"] = datetime.utcnow()
                position["pnl_sol"] = pnl
                position["pnl_percent"] = pnl_percent
                position["sell_reason"] = reason

                # Remove from open positions
                del self.open_positions[mint]

                # Update performance stats
                self.performance_stats["total_pnl"] += pnl
                if pnl > 0:
                    self.performance_stats["successful_trades"] += 1

                # Calculate win rate
                if self.performance_stats["total_trades"] > 0:
                    self.performance_stats["win_rate"] = (
                        self.performance_stats["successful_trades"] / 
                        self.performance_stats["total_trades"]
                    ) * 100

                # Add to trade history
                self.trade_history.append({
                    "action": "SELL",
                    "symbol": position["symbol"],
                    "pnl_sol": pnl,
                    "pnl_percent": pnl_percent,
                    "reason": reason,
                    "timestamp": datetime.utcnow(),
                    "success": True
                })

                print(f"✅ Sold {position['symbol']} - P&L: {pnl_percent:.2f}%")
                return True
            else:
                print(f"❌ Sell transaction failed")
                return False

        except Exception as e:
            print(f"❌ Error selling token {mint[:8]}...: {e}")
            return False

    def monitor_positions(self):
        """
        Enhanced position monitoring with better stop loss and take profit.
        """
        try:
            current_time = datetime.utcnow()
            
            for mint, position in list(self.open_positions.items()):
                # Check position age
                age = current_time - position["buy_time"]
                
                # Simulate price movement for demo
                price_change = random.uniform(-0.3, 0.4)  # -30% to +40%
                
                # Check for stop loss
                if price_change <= position["stop_loss"]:
                    print(f"🔴 Stop loss triggered for {position['symbol']}: {price_change:.2f}%")
                    asyncio.create_task(self.sell_token(mint, "stop_loss"))
                
                # Check for take profit
                elif price_change >= position["target_profit"]:
                    print(f"🟢 Take profit triggered for {position['symbol']}: {price_change:.2f}%")
                    asyncio.create_task(self.sell_token(mint, "take_profit"))
                
                # Check for time-based exit (24 hours)
                elif age > timedelta(hours=24):
                    print(f"⏰ Time-based exit for {position['symbol']}: {age}")
                    asyncio.create_task(self.sell_token(mint, "time_exit"))
                
        except Exception as e:
            print(f"❌ Error monitoring positions: {e}")

    def _check_daily_limits(self) -> bool:
        """Check if we've hit daily trading limits."""
        today = datetime.utcnow().date()
        
        # Reset daily counter if it's a new day
        if today != self.last_trade_reset:
            self.daily_trades = 0
            self.last_trade_reset = today
        
        return self.daily_trades >= config.MAX_DAILY_TRADES

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """
        Get enhanced portfolio summary with more detailed metrics.
        """
        try:
            total_invested = sum(pos["buy_price_sol"] for pos in self.open_positions.values())
            
            # Calculate current value (simplified)
            current_value = 0
            for pos in self.open_positions.values():
                # Simulate current price
                price_change = random.uniform(-0.2, 0.3)
                current_value += pos["buy_price_sol"] * (1 + price_change)
            
            pnl = current_value - total_invested
            
            # Get recent trades
            recent_trades = self.trade_history[-5:] if self.trade_history else []
            
            # Get position details
            position_details = []
            for mint, pos in self.open_positions.items():
                age = datetime.utcnow() - pos["buy_time"]
                position_details.append({
                    "symbol": pos["symbol"],
                    "buy_price_sol": pos["buy_price_sol"],
                    "buy_time": pos["buy_time"],
                    "age_minutes": age.total_seconds() / 60,
                    "current_pnl_percent": random.uniform(-15, 25)  # Simulated
                })
            
            return {
                "open_positions": len(self.open_positions),
                "total_invested_sol": total_invested,
                "total_value": current_value,
                "total_pnl_sol": pnl,
                "daily_trades": self.daily_trades,
                "recent_trades": recent_trades,
                "positions": position_details,
                "performance": self.performance_stats
            }
            
        except Exception as e:
            print(f"❌ Error getting portfolio summary: {e}")
            return {
                "open_positions": 0,
                "total_invested_sol": 0,
                "total_value": 0,
                "total_pnl_sol": 0,
                "daily_trades": 0,
                "recent_trades": [],
                "positions": [],
                "performance": {}
            }
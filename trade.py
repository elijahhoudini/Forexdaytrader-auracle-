"""
AURACLE Trade Handler Module
===========================

Trade execution and position management system.
Handles buying, selling, and monitoring of token positions.
"""

import time
import random
from typing import Dict, Any, Optional, List
from datetime import datetime
import config


# This duplicate class definition was removed to fix conflicts

class TradeHandler:
    """
    Trade execution and position management system.

    Handles all trading operations including:
    - Buy/sell order execution
    - Position monitoring and management
    - Stop loss and take profit orders
    - Portfolio tracking
    """

    def __init__(self, wallet):
        """Initialize trade handler with wallet instance."""
        self.wallet = wallet
        self.open_positions = {}  # mint -> position_data
        self.trade_history = []
        self.daily_trades = 0
        self.last_trade_reset = datetime.utcnow().date()

        print("✅ TradeHandler initialized")

    def calculate_trade_amount(self, token: Dict[str, Any]) -> float:
        """
        Calculate the trading amount for a token based on confidence and dynamic allocation.

        Args:
            token (Dict): Token data

        Returns:
            float: Amount of SOL to invest
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

        return base_amount

    def _calculate_confidence_score(self, token: Dict[str, Any]) -> float:
        """
        Calculate confidence score for a token based on various factors.

        Args:
            token (Dict): Token data

        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        confidence = 0.5  # Start with neutral confidence

        # Check for high-confidence patterns in symbol
        symbol = token.get("symbol", "").upper()
        for pattern in config.HIGH_CONFIDENCE_PATTERNS:
            if pattern in symbol:
                confidence += 0.3
                print(f"🎯 High confidence pattern detected: {pattern} in {symbol}")
                break

        # Factor in liquidity (higher liquidity = more confidence)
        liquidity = token.get("liquidity", 0)
        if liquidity > 10000:
            confidence += 0.2
        elif liquidity > 5000:
            confidence += 0.1

        # Factor in volume (higher volume = more confidence)
        volume = token.get("volume24h", 0)
        if volume > 5000:
            confidence += 0.1
        elif volume > 2000:
            confidence += 0.05

        # Factor in price stability (less volatility = more confidence)
        price_change = abs(token.get("priceChange24h", 0))
        if price_change < 0.1:  # Less than 10% change
            confidence += 0.1
        elif price_change > 0.5:  # More than 50% change
            confidence -= 0.2

        return max(0.0, min(1.0, confidence))

    def should_buy(self, token: Dict[str, Any]) -> bool:
        """
        Determine if we should buy a token based on strategy.

        Args:
            token (Dict): Token data

        Returns:
            bool: True if we should buy
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

        # Simple strategy: buy if liquidity is good
        liquidity = token.get("liquidity", 0)
        volume = token.get("volume24h", 0)

        return liquidity > config.MIN_LIQUIDITY_THRESHOLD and volume > 500

    def buy_token(self, token: Dict[str, Any], amount_sol: float) -> bool:
        """
        Execute buy order for token.

        Args:
            token (Dict): Token data
            amount_sol (float): Amount of SOL to spend

        Returns:
            bool: True if successful
        """
        try:
            mint = token["mint"]

            # Check wallet balance
            balance = self.wallet.get_balance("SOL")
            if balance < amount_sol:
                print(f"❌ Insufficient SOL balance: {balance} < {amount_sol}")
                return False

            # Execute transaction
            if config.get_demo_mode():
                # Demo mode - simulate transaction
                tx_result = {
                    "success": True,
                    "signature": f"demo_buy_{mint[:8]}_{int(time.time())}"
                }
                print(f"🔶 DEMO BUY: {token.get('symbol', '?')} - {amount_sol} SOL")
            else:
                # Real transaction
                tx_data = {
                    "action": "buy",
                    "token_mint": mint,
                    "amount_sol": amount_sol,
                    "timestamp": time.time()
                }
                tx_result = self.wallet.send_transaction(tx_data)

            if tx_result["success"]:
                # Create position record
                position = {
                    "mint": mint,
                    "symbol": token.get("symbol", "Unknown"),
                    "buy_price_sol": amount_sol,
                    "buy_time": datetime.utcnow(),
                    "buy_signature": tx_result["signature"],
                    "status": "open"
                }

                self.open_positions[mint] = position
                self.daily_trades += 1

                # Add to trade history
                self.trade_history.append({
                    "action": "BUY",
                    "token": token,
                    "amount": amount_sol,
                    "timestamp": datetime.utcnow(),
                    "signature": tx_result["signature"]
                })

                return True
            else:
                print(f"❌ Buy transaction failed: {tx_result.get('error', 'Unknown error')}")
                return False

        except Exception as e:
            print(f"❌ Buy error: {str(e)}")
            return False

    def sell_token(self, mint: str, reason: str = "manual") -> bool:
        """
        Execute sell order for token.

        Args:
            mint (str): Token mint address
            reason (str): Reason for selling

        Returns:
            bool: True if successful
        """
        try:
            if mint not in self.open_positions:
                print(f"❌ No open position for {mint}")
                return False

            position = self.open_positions[mint]

            # Execute sell transaction
            if config.get_demo_mode():
                # Demo mode - simulate profit/loss
                profit_multiplier = random.uniform(0.8, 1.5)  # Random P&L for demo
                tx_result = {
                    "success": True,
                    "signature": f"demo_sell_{mint[:8]}_{int(time.time())}",
                    "amount_received": position["buy_price_sol"] * profit_multiplier
                }
                print(f"🔶 DEMO SELL: {position['symbol']} - Reason: {reason}")
            else:
                # Real transaction
                tx_data = {
                    "action": "sell",
                    "token_mint": mint,
                    "reason": reason,
                    "timestamp": time.time()
                }
                tx_result = self.wallet.send_transaction(tx_data)

            if tx_result["success"]:
                # Calculate P&L
                amount_received = tx_result.get("amount_received", position["buy_price_sol"])
                pnl = amount_received - position["buy_price_sol"]
                pnl_percent = (pnl / position["buy_price_sol"]) * 100

                # Update position
                position["sell_price_sol"] = amount_received
                position["sell_time"] = datetime.utcnow()
                position["sell_signature"] = tx_result["signature"]
                position["pnl_sol"] = pnl
                position["pnl_percent"] = pnl_percent
                position["status"] = "closed"
                position["sell_reason"] = reason

                # Remove from open positions
                del self.open_positions[mint]

                # Add to trade history
                self.trade_history.append({
                    "action": "SELL",
                    "mint": mint,
                    "symbol": position["symbol"],
                    "amount": amount_received,
                    "pnl": pnl,
                    "pnl_percent": pnl_percent,
                    "reason": reason,
                    "timestamp": datetime.utcnow(),
                    "signature": tx_result["signature"]
                })

                print(f"✅ Sold {position['symbol']} - P&L: {pnl_percent:.2f}%")
                return True
            else:
                print(f"❌ Sell transaction failed: {tx_result.get('error', 'Unknown error')}")
                return False

        except Exception as e:
            print(f"❌ Sell error: {str(e)}")
            return False

    def monitor_positions(self):
        """Monitor open positions for stop loss and take profit."""
        if not self.open_positions:
            return
            
        for mint, position in list(self.open_positions.items()):
            try:
                # Calculate position age
                age_minutes = (datetime.utcnow() - position["buy_time"]).total_seconds() / 60
                
                # Simulate current price for demo
                if config.get_demo_mode():
                    # More realistic price movement for demo
                    # Base on position age - older positions more likely to move
                    age_factor = min(age_minutes / 60, 4)  # Max 4 hours for full volatility
                    volatility = 0.05 + (age_factor * 0.05)  # 5% to 25% volatility
                    
                    # Random walk with slight positive bias
                    price_change = random.uniform(-volatility, volatility * 1.2)
                    current_value = position["buy_price_sol"] * (1 + price_change)
                    pnl_percent = price_change * 100
                else:
                    # In real mode, you would fetch actual token price here
                    current_value = position["buy_price_sol"]
                    pnl_percent = 0
                
                # Update position with current value (for display purposes)
                position["current_value"] = current_value
                position["current_pnl_percent"] = pnl_percent
                
                # Check stop loss
                if pnl_percent <= (config.STOP_LOSS_PERCENTAGE * 100):
                    print(f"🛑 Stop loss triggered for {position['symbol']}: {pnl_percent:.2f}%")
                    self.sell_token(mint, "stop_loss")
                    continue
                
                # Check take profit
                if pnl_percent >= (config.PROFIT_TARGET_PERCENTAGE * 100):
                    print(f"🎯 Take profit triggered for {position['symbol']}: {pnl_percent:.2f}%")
                    self.sell_token(mint, "take_profit")
                    continue
                
                # Check position age (close old positions)
                if age_minutes > 1440:  # 24 hours
                    print(f"⏰ Closing aged position for {position['symbol']}")
                    self.sell_token(mint, "aged_position")
                    continue
                
                # Occasionally show position status
                if random.random() < 0.1:  # 10% chance per monitoring cycle
                    print(f"📊 {position['symbol']}: {pnl_percent:+.2f}% (Age: {age_minutes:.0f}m)")
                    
            except Exception as e:
                print(f"❌ Error monitoring position {mint}: {str(e)}")

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """
        Get portfolio summary with current positions and performance.

        Returns:
            Dict: Portfolio summary
        """
        total_invested = sum(pos["buy_price_sol"] for pos in self.open_positions.values())

        # Calculate total P&L from closed positions
        closed_trades = [t for t in self.trade_history if t["action"] == "SELL"]
        total_pnl = sum(t.get("pnl", 0) for t in closed_trades)

        return {
            "open_positions": len(self.open_positions),
            "total_invested_sol": total_invested,
            "total_pnl_sol": total_pnl,
            "total_value": total_invested + total_pnl,  # Fix: Add total_value key
            "daily_trades": self.daily_trades,
            "positions": list(self.open_positions.values()),
            "recent_trades": self.trade_history[-5:] if self.trade_history else []
        }

    async def handle_token(self, mint: str, token_info: Dict[str, Any]) -> bool:
        """
        Handle a token detected by the scanner.

        Args:
            mint (str): Token mint address
            token_info (Dict): Token information from scanner

        Returns:
            bool: True if action was taken
        """
        try:
            symbol = token_info.get("symbol", "Unknown")

            # Check if we should buy this token
            if not self.should_buy(token_info):
                print(f"[trade] Skipping {symbol} - did not meet buy criteria")
                return False

            # Calculate trade amount
            amount_sol = self.calculate_trade_amount(token_info)

            # Execute buy order
            success = self.buy_token(token_info, amount_sol)

            if success:
                print(f"[trade] ✅ Successfully bought {symbol} for {amount_sol} SOL")
                return True
            else:
                print(f"[trade] ❌ Failed to buy {symbol}")
                return False

        except Exception as e:
            print(f"[trade] Error handling token {mint}: {str(e)}")
            return False

    def _check_daily_limits(self) -> bool:
        """Check if daily trading limits are reached."""
        today = datetime.utcnow().date()

        # Reset daily counter if new day
        if today != self.last_trade_reset:
            self.daily_trades = 0
            self.last_trade_reset = today

        return self.daily_trades >= config.MAX_DAILY_TRADES
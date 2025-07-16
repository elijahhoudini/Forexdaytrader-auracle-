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

    def __init__(self, wallet, auracle_instance=None):
        """Initialize trade handler with wallet instance and optional auracle reference."""
        self.wallet = wallet
        self.auracle_instance = auracle_instance  # Reference to main Auracle instance
        self.open_positions = {}  # mint -> position_data
        self.trade_history = []
        self.daily_trades = 0
        self.last_trade_reset = datetime.utcnow().date()
        
        # Sniper integration
        self.sniper_active = False
        self.sniper_trades = {}  # Track sniper-originated trades
        self.position_monitoring_active = True

        print("✅ TradeHandler initialized with sniper integration")

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
        Enhanced confidence score calculation with balanced criteria.

        Args:
            token (Dict): Token data

        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        confidence = 0.4  # Start with slightly optimistic baseline

        # Check for high-confidence patterns in symbol
        symbol = token.get("symbol", "").upper()
        for pattern in config.HIGH_CONFIDENCE_PATTERNS:
            if pattern in symbol:
                confidence += 0.25
                print(f"🎯 High confidence pattern detected: {pattern} in {symbol}")
                break

        # Factor in liquidity with more realistic thresholds
        liquidity = token.get("liquidity", 0)
        if liquidity > 20000:
            confidence += 0.15
        elif liquidity > 10000:
            confidence += 0.12
        elif liquidity > 5000:
            confidence += 0.08
        elif liquidity > 1000:
            confidence += 0.05

        # Factor in volume with realistic expectations
        volume = token.get("volume24h", 0)
        if volume > 10000:
            confidence += 0.12
        elif volume > 5000:
            confidence += 0.08
        elif volume > 2000:
            confidence += 0.05
        elif volume > 500:
            confidence += 0.03

        # Factor in holders (more holders = more confidence)
        holders = token.get("holders", 0)
        if holders > 100:
            confidence += 0.08
        elif holders > 50:
            confidence += 0.05
        elif holders > 20:
            confidence += 0.03

        # Factor in price movement (moderate positive movement is good)
        price_change = token.get("priceChange24h", 0)
        if 0.02 <= price_change <= 0.15:  # 2-15% positive change is ideal
            confidence += 0.08
        elif 0 <= price_change < 0.02:  # Small positive change
            confidence += 0.03
        elif -0.05 <= price_change < 0:  # Small negative change is acceptable
            confidence += 0.01
        elif price_change < -0.3 or price_change > 0.5:  # Extreme movements are risky
            confidence -= 0.15

        # Bonus for demo tokens (they're safe for testing)
        if token.get("source") == "Demo":
            confidence += 0.1

        return max(0.0, min(1.0, confidence))

    def should_buy(self, token: Dict[str, Any]) -> bool:
        """
        Enhanced AI-powered buy decision with realistic and debuggable criteria.

        Args:
            token (Dict): Token data

        Returns:
            bool: True if we should buy
        """
        symbol = token.get("symbol", "Unknown")
        
        # Check daily limits
        if self._check_daily_limits():
            print(f"[trade] ❌ {symbol}: Daily trade limit reached ({self.daily_trades}/{config.MAX_DAILY_TRADES})")
            return False

        # Check position limits
        if len(self.open_positions) >= config.MAX_OPEN_POSITIONS:
            print(f"[trade] ❌ {symbol}: Max positions reached ({len(self.open_positions)}/{config.MAX_OPEN_POSITIONS})")
            return False

        # Check if we already have a position
        if token["mint"] in self.open_positions:
            print(f"[trade] ❌ {symbol}: Already have position")
            return False

        # Get token metrics
        liquidity = token.get("liquidity", 0)
        volume = token.get("volume24h", 0)
        price_change = token.get("priceChange24h", 0)
        holders = token.get("holders", 0)
        
        # Calculate AI confidence score
        confidence = self._calculate_confidence_score(token)
        
        # Adjust criteria based on mode
        if config.get_demo_mode() and hasattr(config, 'DEMO_MODE_RELAXED_CRITERIA') and config.DEMO_MODE_RELAXED_CRITERIA:
            # Relaxed criteria for demo mode
            min_liquidity = config.MIN_LIQUIDITY_THRESHOLD * 0.5  # 50% of normal requirement
            min_volume = config.MIN_LIQUIDITY_THRESHOLD * 0.3     # 30% of normal requirement
            min_holders = 15                                       # Reduced from 25
            min_confidence = max(0.5, config.AI_CONFIDENCE_THRESHOLD - 0.15)  # Reduced confidence
        else:
            # Normal criteria for live trading
            min_liquidity = config.MIN_LIQUIDITY_THRESHOLD * config.LIQUIDITY_SAFETY_MULTIPLIER
            min_volume = config.MIN_LIQUIDITY_THRESHOLD * config.VOLUME_MOMENTUM_FACTOR
            min_holders = 25
            min_confidence = config.AI_CONFIDENCE_THRESHOLD
        
        # Detailed criteria checking with debugging
        criteria_results = {
            "liquidity_check": liquidity > min_liquidity,
            "volume_check": volume > min_volume,
            "holder_check": holders >= min_holders,
            "confidence_check": confidence >= min_confidence,
            "price_stability": price_change > -0.20,  # Not falling more than 20%
            "volatility_check": abs(price_change) < 1.0 if config.get_demo_mode() else abs(price_change) < 0.6  # More lenient for demo
        }
        
        # Count passed criteria
        passed_criteria = sum(criteria_results.values())
        total_criteria = len(criteria_results)
        
        # Decision logic - require most criteria to pass
        all_critical_passed = (
            criteria_results["liquidity_check"] and
            criteria_results["confidence_check"] and
            criteria_results["price_stability"]
        )
        
        # More lenient decision for demo mode
        if config.get_demo_mode():
            decision = passed_criteria >= 4  # At least 4 out of 6 criteria
        else:
            decision = all_critical_passed and passed_criteria >= 5  # Stricter for live
        
        # Debug output
        mode_str = "🔶 DEMO" if config.get_demo_mode() else "🔥 LIVE"
        status_emoji = "✅" if decision else "❌"
        
        print(f"[trade] {status_emoji} {mode_str} {symbol} Analysis:")
        print(f"   💧 Liquidity: ${liquidity:,.0f} (need ${min_liquidity:,.0f}) {'✅' if criteria_results['liquidity_check'] else '❌'}")
        print(f"   📊 Volume: ${volume:,.0f} (need ${min_volume:,.0f}) {'✅' if criteria_results['volume_check'] else '❌'}")
        print(f"   👥 Holders: {holders} (need {min_holders}) {'✅' if criteria_results['holder_check'] else '❌'}")
        print(f"   🤖 AI Confidence: {confidence:.2f} (need {min_confidence:.2f}) {'✅' if criteria_results['confidence_check'] else '❌'}")
        print(f"   📈 Price Change: {price_change:+.2%} {'✅' if criteria_results['price_stability'] else '❌'}")
        print(f"   🌊 Volatility: {abs(price_change):.2%} {'✅' if criteria_results['volatility_check'] else '❌'}")
        print(f"   📊 Score: {passed_criteria}/{total_criteria} criteria passed")
        
        if decision:
            print(f"🎯 AI BUY Signal: {symbol} - Confidence: {confidence:.2f}")
            
        return decision

    async def buy_token(self, token: Dict[str, Any], amount_sol: float) -> bool:
        """
        Execute buy order for token using Jupiter.

        Args:
            token (Dict): Token data
            amount_sol (float): Amount of SOL to spend

        Returns:
            bool: True if successful
        """
        try:
            mint = token["mint"]

            # Check wallet balance
            balance = await self.wallet.get_balance("SOL")
            if balance < amount_sol:
                print(f"❌ Insufficient SOL balance: {balance} < {amount_sol}")
                return False

            # Execute transaction via Jupiter
            tx_result = await self.wallet.buy_token(mint, amount_sol)

            if tx_result["success"]:
                # Create position record
                position = {
                    "mint": mint,
                    "symbol": token.get("symbol", "Unknown"),
                    "buy_price_sol": amount_sol,
                    "buy_time": datetime.utcnow(),
                    "buy_signature": tx_result["signature"],
                    "tokens_received": tx_result.get("output_amount", 0),
                    "status": "open",
                    "demo_mode": tx_result.get("demo_mode", False)
                }

                self.open_positions[mint] = position
                self.daily_trades += 1

                # Add to trade history
                self.trade_history.append({
                    "action": "BUY",
                    "token": token,
                    "amount": amount_sol,
                    "timestamp": datetime.utcnow(),
                    "signature": tx_result["signature"],
                    "jupiter_result": tx_result
                })

                mode_str = "🔶 DEMO" if tx_result.get("demo_mode") else "🔥 LIVE"
                print(f"{mode_str} BUY: {token.get('symbol', '?')} - {amount_sol} SOL -> {tx_result.get('output_amount', 0)} tokens")
                return True
            else:
                print(f"❌ Buy transaction failed: {tx_result.get('error', 'Unknown error')}")
                return False

        except Exception as e:
            print(f"❌ Buy error: {e}")
            return False

    async def sell_token(self, mint: str, reason: str = "manual") -> bool:
        """
        Enhanced sell order execution with profit tracking.

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
            token_amount = position.get("tokens_received", 1000)  # Use received tokens or default

            # Get current market value before selling
            current_value = position.get("current_value", position["buy_price_sol"])
            current_pnl_percent = position.get("current_pnl_percent", 0)

            # Execute sell transaction via Jupiter
            tx_result = await self.wallet.sell_token(mint, token_amount)

            if tx_result["success"]:
                # Enhanced P&L calculation
                if config.get_demo_mode():
                    # Use simulated current value for demo mode
                    amount_received = current_value
                else:
                    # Use actual received amount for live trading
                    amount_received = tx_result.get("output_amount", 0) / 1e9  # Convert lamports to SOL
                    if amount_received == 0:  # Fallback
                        amount_received = tx_result.get("amount_received", current_value)
                    
                pnl = amount_received - position["buy_price_sol"]
                pnl_percent = (pnl / position["buy_price_sol"]) * 100
                
                # Calculate profit efficiency metrics
                age_minutes = (datetime.utcnow() - position["buy_time"]).total_seconds() / 60
                profit_per_hour = (pnl_percent / max(age_minutes / 60, 0.01))  # Profit per hour
                
                # Update position with enhanced data
                position.update({
                    "sell_price_sol": amount_received,
                    "sell_time": datetime.utcnow(),
                    "sell_signature": tx_result["signature"],
                    "pnl_sol": pnl,
                    "pnl_percent": pnl_percent,
                    "status": "closed",
                    "sell_reason": reason,
                    "hold_time_minutes": age_minutes,
                    "profit_per_hour": profit_per_hour,
                    "was_profitable": pnl > 0
                })

                # Remove from open positions
                del self.open_positions[mint]

                # Enhanced trade history record
                self.trade_history.append({
                    "action": "SELL",
                    "mint": mint,
                    "symbol": position["symbol"],
                    "buy_price": position["buy_price_sol"],
                    "sell_price": amount_received,
                    "pnl_sol": pnl,
                    "pnl_percent": pnl_percent,
                    "hold_time_minutes": age_minutes,
                    "profit_per_hour": profit_per_hour,
                    "reason": reason,
                    "timestamp": datetime.utcnow(),
                    "signature": tx_result["signature"],
                    "jupiter_result": tx_result,
                    "was_profitable": pnl > 0
                })

                # Enhanced profit/loss reporting
                mode_str = "🔶 DEMO" if tx_result.get("demo_mode") else "🔥 LIVE"
                profit_emoji = "💰" if pnl > 0 else "📉" if pnl < 0 else "⚖️"
                
                # Show detailed profit metrics
                print(f"{mode_str} {profit_emoji} SELL: {position['symbol']}")
                print(f"   💵 P&L: {pnl:+.4f} SOL ({pnl_percent:+.2f}%)")
                print(f"   ⏱️  Hold: {age_minutes:.1f}m | Efficiency: {profit_per_hour:+.1f}%/hr")
                print(f"   🎯 Reason: {reason}")
                
                # Update global profit tracking
                self._update_profit_statistics(pnl, pnl_percent, reason)
                
                return True
            else:
                print(f"❌ Sell transaction failed: {tx_result.get('error', 'Unknown error')}")
                return False

        except Exception as e:
            print(f"❌ Sell error: {str(e)}")
            return False

    def _update_profit_statistics(self, pnl_sol: float, pnl_percent: float, reason: str):
        """Update global profit tracking statistics with LLC contribution tracking."""
        if not hasattr(self, 'profit_stats'):
            self.profit_stats = {
                'total_profit_sol': 0,
                'total_trades': 0,
                'profitable_trades': 0,
                'profit_by_reason': {},
                'best_trade_percent': 0,
                'worst_trade_percent': 0
            }
        
        stats = self.profit_stats
        stats['total_profit_sol'] += pnl_sol
        stats['total_trades'] += 1
        
        if pnl_sol > 0:
            stats['profitable_trades'] += 1
            
            # Track LLC contribution for profitable trades
            if self.auracle_instance and hasattr(self.auracle_instance, 'track_llc_contribution'):
                self.auracle_instance.track_llc_contribution(pnl_sol)
        
        # Track by reason
        if reason not in stats['profit_by_reason']:
            stats['profit_by_reason'][reason] = {'count': 0, 'total_profit': 0}
        stats['profit_by_reason'][reason]['count'] += 1
        stats['profit_by_reason'][reason]['total_profit'] += pnl_sol
        
        # Track extremes
        if pnl_percent > stats['best_trade_percent']:
            stats['best_trade_percent'] = pnl_percent
        if pnl_percent < stats['worst_trade_percent']:
            stats['worst_trade_percent'] = pnl_percent
        
        # Show periodic summary
        if stats['total_trades'] % 5 == 0:  # Every 5 trades
            win_rate = (stats['profitable_trades'] / stats['total_trades']) * 100
            print(f"📈 PROFIT SUMMARY: {stats['total_profit_sol']:+.4f} SOL | Win Rate: {win_rate:.1f}% | Trades: {stats['total_trades']}")

    async def monitor_positions(self):
        """Enhanced position monitoring with profit-focused selling strategies and sniper trade handling."""
        if not self.open_positions or not self.position_monitoring_active:
            return
            
        for mint, position in list(self.open_positions.items()):
            try:
                # Calculate position age
                age_minutes = (datetime.utcnow() - position["buy_time"]).total_seconds() / 60
                is_sniper_trade = position.get("sniper_trade", False)
                
                # Enhanced price simulation for demo mode
                if config.get_demo_mode():
                    current_value, pnl_percent = self._simulate_realistic_price_movement(position, age_minutes)
                else:
                    # In real mode, you would fetch actual token price here
                    current_value = position["buy_price_sol"]
                    pnl_percent = 0
                
                # Update position with current value
                position["current_value"] = current_value
                position["current_pnl_percent"] = pnl_percent
                position["age_minutes"] = age_minutes
                
                # Initialize trailing stop if not set
                if "trailing_stop_price" not in position:
                    position["trailing_stop_price"] = position["buy_price_sol"]
                    position["highest_value"] = current_value
                
                # Update trailing stop
                if config.TRAILING_STOP_ENABLED and current_value > position["highest_value"]:
                    position["highest_value"] = current_value
                    new_trailing_stop = current_value * (1 - config.TRAILING_STOP_PERCENTAGE)
                    if new_trailing_stop > position["trailing_stop_price"]:
                        position["trailing_stop_price"] = new_trailing_stop
                
                # PROFIT-FOCUSED SELLING DECISIONS
                
                # 1. Enhanced quick profit for sniper trades
                quick_profit_threshold = config.QUICK_PROFIT_TARGET * 100
                quick_profit_time = config.QUICK_PROFIT_TIME_MINUTES
                
                # Sniper trades get more aggressive quick profit settings
                if is_sniper_trade:
                    quick_profit_threshold *= 0.7  # Lower threshold for sniper trades
                    quick_profit_time *= 1.5  # Longer time window for sniper trades
                
                if (age_minutes <= quick_profit_time and 
                    pnl_percent >= quick_profit_threshold):
                    trade_type = "sniper_quick_profit" if is_sniper_trade else "quick_profit"
                    print(f"⚡ {'Sniper ' if is_sniper_trade else ''}Quick profit exit for {position['symbol']}: {pnl_percent:.2f}% in {age_minutes:.1f}m")
                    await self.sell_token(mint, trade_type)
                    continue
                
                # 2. Main profit target
                if pnl_percent >= (config.PROFIT_TARGET_PERCENTAGE * 100):
                    print(f"🎯 Profit target reached for {position['symbol']}: {pnl_percent:.2f}%")
                    await self.sell_token(mint, "profit_target")
                    continue
                
                # 3. Trailing stop (lock in profits)
                if (config.TRAILING_STOP_ENABLED and 
                    current_value <= position["trailing_stop_price"] and
                    position["trailing_stop_price"] > position["buy_price_sol"]):
                    profit_locked = ((position["trailing_stop_price"] / position["buy_price_sol"]) - 1) * 100
                    print(f"📈 Trailing stop triggered for {position['symbol']}: Locking {profit_locked:.2f}% profit")
                    await self.sell_token(mint, "trailing_stop")
                    continue
                
                # 4. Stop loss (capital preservation)
                if pnl_percent <= (config.STOP_LOSS_PERCENTAGE * 100):
                    print(f"🛑 Stop loss triggered for {position['symbol']}: {pnl_percent:.2f}%")
                    await self.sell_token(mint, "stop_loss")
                    continue
                
                # 5. Minimum hold time check before any exit
                if age_minutes < config.MIN_HOLD_TIME_MINUTES:
                    continue  # Don't exit too early
                
                # 6. Force exit on max hold time (risk management)
                if age_minutes > (config.MAX_HOLD_TIME_HOURS * 60):
                    if config.PROFIT_ONLY_MODE and pnl_percent < 0:
                        # In profit-only mode, extend hold time if losing but still above stop loss
                        if pnl_percent > (config.STOP_LOSS_PERCENTAGE * 100):
                            print(f"⏳ Extending hold time for {position['symbol']} (profit-only mode)")
                            continue
                    
                    print(f"⏰ Max hold time reached for {position['symbol']}: {age_minutes/60:.1f}h")
                    await self.sell_token(mint, "max_hold_time")
                    continue
                
                # 7. Smart exit on declining momentum
                if (age_minutes > 30 and  # After 30 minutes
                    pnl_percent > 2 and   # Small profit
                    pnl_percent < (current_value / position["highest_value"] - 1) * 100 * 0.7):  # Declining from peak
                    print(f"📉 Smart exit on declining momentum for {position['symbol']}: {pnl_percent:.2f}%")
                    await self.sell_token(mint, "momentum_decline")
                    continue
                
                # Periodic status updates
                if random.random() < 0.05:  # 5% chance per cycle
                    trail_info = f" (Trail: {((position['trailing_stop_price']/position['buy_price_sol'])-1)*100:+.1f}%)" if config.TRAILING_STOP_ENABLED else ""
                    print(f"📊 {position['symbol']}: {pnl_percent:+.2f}% | Age: {age_minutes:.0f}m{trail_info}")
                    
            except Exception as e:
                print(f"❌ Error monitoring position {mint}: {str(e)}")

    def _simulate_realistic_price_movement(self, position: Dict[str, Any], age_minutes: float) -> tuple:
        """
        Simulate realistic price movement for demo mode.
        
        Returns:
            tuple: (current_value, pnl_percent)
        """
        # Get symbol for pattern recognition
        symbol = position.get("symbol", "")
        
        # Base volatility
        base_volatility = 0.08  # 8% base volatility
        
        # Time-based volatility (more movement over time)
        time_factor = min(age_minutes / 180, 2.0)  # Max 3 hours for full volatility
        volatility = base_volatility * (1 + time_factor * 0.5)
        
        # Pattern-based behavior
        if any(pattern in symbol for pattern in config.HIGH_CONFIDENCE_PATTERNS):
            # High confidence tokens tend to perform better
            bias = 0.03 + (time_factor * 0.02)  # Positive bias
            volatility *= 0.8  # Less volatile
        else:
            bias = 0.01  # Slight positive bias
        
        # Random walk with momentum
        if not hasattr(position, '_price_momentum'):
            position['_price_momentum'] = 0
        
        # Add momentum to price movement
        momentum_decay = 0.95
        position['_price_momentum'] *= momentum_decay
        
        # New random component
        random_change = random.gauss(bias, volatility)
        position['_price_momentum'] += random_change * 0.3
        
        # Total price change
        total_change = random_change + position['_price_momentum']
        
        # Apply change to get current value
        current_value = position["buy_price_sol"] * (1 + total_change)
        current_value = max(current_value, position["buy_price_sol"] * 0.5)  # Don't go below 50% loss
        
        pnl_percent = ((current_value / position["buy_price_sol"]) - 1) * 100
        
        return current_value, pnl_percent

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """
        Enhanced portfolio summary with profit-focused metrics.

        Returns:
            Dict: Comprehensive portfolio summary
        """
        total_invested = sum(pos["buy_price_sol"] for pos in self.open_positions.values())
        current_total_value = sum(pos.get("current_value", pos["buy_price_sol"]) for pos in self.open_positions.values())

        # Calculate total P&L from closed positions
        closed_trades = [t for t in self.trade_history if t["action"] == "SELL"]
        total_realized_pnl = sum(t.get("pnl_sol", 0) for t in closed_trades)
        
        # Calculate unrealized P&L from open positions
        unrealized_pnl = current_total_value - total_invested
        
        # Total portfolio value
        total_value = current_total_value + total_realized_pnl
        
        # Profit statistics
        profit_stats = getattr(self, 'profit_stats', {
            'total_profit_sol': 0, 'total_trades': 0, 'profitable_trades': 0,
            'profit_by_reason': {}, 'best_trade_percent': 0, 'worst_trade_percent': 0
        })
        
        win_rate = (profit_stats['profitable_trades'] / max(profit_stats['total_trades'], 1)) * 100
        
        # Calculate average profit per trade
        avg_profit_per_trade = total_realized_pnl / max(len(closed_trades), 1)
        
        # Top performing positions
        profitable_positions = [pos for pos in self.open_positions.values() 
                              if pos.get("current_pnl_percent", 0) > 0]
        
        return {
            "open_positions": len(self.open_positions),
            "total_invested_sol": total_invested,
            "current_value_sol": current_total_value,
            "realized_pnl_sol": total_realized_pnl,
            "unrealized_pnl_sol": unrealized_pnl,
            "total_value": total_value,
            "total_return_percent": ((total_value / max(total_invested, 0.001)) - 1) * 100 if total_invested > 0 else 0,
            "daily_trades": self.daily_trades,
            "win_rate_percent": win_rate,
            "avg_profit_per_trade": avg_profit_per_trade,
            "best_trade_percent": profit_stats.get('best_trade_percent', 0),
            "worst_trade_percent": profit_stats.get('worst_trade_percent', 0),
            "profitable_positions_count": len(profitable_positions),
            "positions": list(self.open_positions.values()),
            "recent_trades": self.trade_history[-5:] if self.trade_history else [],
            "profit_by_reason": profit_stats.get('profit_by_reason', {}),
            "last_updated": datetime.utcnow().isoformat()
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
            success = await self.buy_token(token_info, amount_sol)

            if success:
                print(f"[trade] ✅ Successfully bought {symbol} for {amount_sol} SOL")
                return True
            else:
                print(f"[trade] ❌ Failed to buy {symbol}")
                return False

        except Exception as e:
            print(f"[trade] Error handling token {mint}: {str(e)}")
            return False

    async def handle_sniper_token(self, token_info: Dict[str, Any], sniper_source: str = "auto") -> bool:
        """
        Handle a token detected by the sniper with enhanced monitoring.

        Args:
            token_info (Dict): Token information from sniper
            sniper_source (str): Source of sniper signal (auto/manual)

        Returns:
            bool: True if action was taken
        """
        try:
            symbol = token_info.get("symbol", "Unknown")
            mint = token_info.get("mint", "")

            # Enhanced buy criteria for sniper tokens
            if not self.should_buy_sniper_token(token_info):
                print(f"[sniper] Skipping {symbol} - did not meet sniper criteria")
                return False

            # Calculate sniper trade amount (usually smaller for quick trades)
            amount_sol = min(self.calculate_trade_amount(token_info), config.MAX_BUY_AMOUNT_SOL * 0.5)

            # Execute buy order
            success = await self.buy_token(token_info, amount_sol)

            if success:
                # Mark as sniper trade for enhanced monitoring
                if mint in self.open_positions:
                    self.open_positions[mint]["sniper_trade"] = True
                    self.open_positions[mint]["sniper_source"] = sniper_source
                    self.sniper_trades[mint] = {
                        "entry_time": datetime.utcnow(),
                        "source": sniper_source,
                        "symbol": symbol
                    }

                print(f"[sniper] 🎯 Successfully sniped {symbol} for {amount_sol} SOL ({sniper_source})")
                return True
            else:
                print(f"[sniper] ❌ Failed to snipe {symbol}")
                return False

        except Exception as e:
            print(f"[sniper] Error handling sniper token {token_info.get('mint', 'unknown')}: {str(e)}")
            return False

    def should_buy_sniper_token(self, token: Dict[str, Any]) -> bool:
        """
        Enhanced buy decision specifically for sniper-detected tokens.
        More aggressive criteria for quick opportunities.
        """
        symbol = token.get("symbol", "Unknown")
        
        # Check daily limits
        if self._check_daily_limits():
            print(f"[sniper] ❌ {symbol}: Daily trade limit reached")
            return False

        # Check position limits
        if len(self.open_positions) >= config.MAX_OPEN_POSITIONS:
            print(f"[sniper] ❌ {symbol}: Max positions reached")
            return False

        # Check if we already have a position
        if token["mint"] in self.open_positions:
            print(f"[sniper] ❌ {symbol}: Already have position")
            return False

        # Sniper-specific criteria (more lenient for quick opportunities)
        liquidity = token.get("liquidity", 0)
        volume = token.get("volume24h", 0)
        
        # Relaxed criteria for sniper trades
        min_liquidity = config.MIN_LIQUIDITY_THRESHOLD * 0.3  # 30% of normal
        min_volume = 1000  # Lower volume threshold for new tokens
        
        if liquidity < min_liquidity:
            print(f"[sniper] ❌ {symbol}: Insufficient liquidity {liquidity} < {min_liquidity}")
            return False
            
        if volume < min_volume:
            print(f"[sniper] ❌ {symbol}: Insufficient volume {volume} < {min_volume}")
            return False

        print(f"[sniper] ✅ {symbol}: Passed sniper criteria")
        return True

    def _check_daily_limits(self) -> bool:
        """Check if daily trading limits are reached."""
        today = datetime.utcnow().date()

        # Reset daily counter if new day
        if today != self.last_trade_reset:
            self.daily_trades = 0
            self.last_trade_reset = today

        return self.daily_trades >= config.MAX_DAILY_TRADES
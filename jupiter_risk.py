"""
Enhanced Risk Management Module for Jupiter Integration
======================================================

Advanced risk management features for real trading scenarios:
- Transaction validation
- Price impact monitoring
- Slippage protection
- Position size management
- Real-time balance monitoring
"""

import time
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import config
from logger import AuracleLogger


class JupiterRiskManager:
    """
    Advanced risk management for Jupiter swap operations.
    
    Provides comprehensive risk assessment and protection for:
    - Price impact limits
    - Slippage protection
    - Position size validation
    - Balance monitoring
    - Transaction validation
    """
    
    def __init__(self, logger: AuracleLogger):
        self.logger = logger
        self.risk_flags = []
        self.transaction_history = []
        self.price_impact_violations = 0
        self.slippage_violations = 0
        
        # Risk thresholds from configuration
        self.max_price_impact = config.JUPITER_MAX_PRICE_IMPACT
        self.max_slippage_bps = config.JUPITER_MAX_SLIPPAGE_BPS
        self.max_trade_size_sol = config.JUPITER_MAX_TRADE_SIZE_SOL
        self.min_liquidity_usd = config.JUPITER_MIN_LIQUIDITY_USD
        
        print("🛡️ Jupiter Risk Manager initialized")
        print(f"   Max Price Impact: {self.max_price_impact}%")
        print(f"   Max Slippage: {self.max_slippage_bps} BPS")
        print(f"   Max Trade Size: {self.max_trade_size_sol} SOL")
        print(f"   Min Liquidity: ${self.min_liquidity_usd:,.0f}")
    
    def validate_quote(self, quote: Dict[str, Any], trade_amount_sol: float) -> Tuple[bool, str]:
        """
        Validate a Jupiter quote before execution.
        
        Args:
            quote: Quote data from Jupiter API
            trade_amount_sol: Amount of SOL being traded
            
        Returns:
            (is_valid, reason)
        """
        try:
            # Check 1: Price impact validation
            price_impact = abs(quote.get("priceImpactPct", 0))
            if price_impact > self.max_price_impact:
                self.price_impact_violations += 1
                reason = f"Price impact too high: {price_impact}% > {self.max_price_impact}%"
                self.logger.log_flag("PRICE_IMPACT", reason, quote)
                return False, reason
            
            # Check 2: Trade size validation
            if trade_amount_sol > self.max_trade_size_sol:
                reason = f"Trade size too large: {trade_amount_sol} > {self.max_trade_size_sol} SOL"
                self.logger.log_flag("TRADE_SIZE", reason, quote)
                return False, reason
            
            # Check 3: Slippage validation
            slippage_bps = quote.get("slippageBps", 0)
            if slippage_bps > self.max_slippage_bps:
                self.slippage_violations += 1
                reason = f"Slippage too high: {slippage_bps} > {self.max_slippage_bps} BPS"
                self.logger.log_flag("SLIPPAGE", reason, quote)
                return False, reason
            
            # Check 4: Output amount validation
            out_amount = int(quote.get("outAmount", 0))
            if out_amount <= 0:
                reason = "Invalid output amount in quote"
                self.logger.log_flag("INVALID_OUTPUT", reason, quote)
                return False, reason
            
            # Check 5: Route validation
            route_plan = quote.get("routePlan", [])
            if not route_plan:
                reason = "No route plan in quote"
                self.logger.log_flag("NO_ROUTE", reason, quote)
                return False, reason
            
            # Check 6: Fee validation
            total_fees = self._calculate_total_fees(quote)
            if total_fees > trade_amount_sol * 0.1:  # 10% max fees
                reason = f"Fees too high: {total_fees} SOL ({total_fees/trade_amount_sol*100:.1f}%)"
                self.logger.log_flag("HIGH_FEES", reason, quote)
                return False, reason
            
            return True, "Quote validation passed"
            
        except Exception as e:
            reason = f"Quote validation error: {str(e)}"
            self.logger.log_error(reason)
            return False, reason
    
    def validate_token_for_trading(self, token_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate a token for trading eligibility.
        
        Args:
            token_data: Token information
            
        Returns:
            (is_valid, reason)
        """
        try:
            # Check 1: Minimum liquidity
            liquidity = token_data.get("liquidity", 0)
            if liquidity < self.min_liquidity_usd:
                reason = f"Insufficient liquidity: ${liquidity:,.0f} < ${self.min_liquidity_usd:,.0f}"
                return False, reason
            
            # Check 2: Volume validation
            volume_24h = token_data.get("volume24h", 0)
            if volume_24h < 1000:  # Minimum $1000 daily volume
                reason = f"Low volume: ${volume_24h:,.0f} < $1,000"
                return False, reason
            
            # Check 3: Price change validation
            price_change = abs(token_data.get("priceChange24h", 0))
            if price_change > 0.5:  # 50% price change limit
                reason = f"High volatility: {price_change*100:.1f}% > 50%"
                return False, reason
            
            # Check 4: Market cap validation
            market_cap = token_data.get("marketCap", 0)
            if market_cap > 0 and market_cap < 100000:  # Minimum $100k market cap
                reason = f"Low market cap: ${market_cap:,.0f} < $100,000"
                return False, reason
            
            return True, "Token validation passed"
            
        except Exception as e:
            reason = f"Token validation error: {str(e)}"
            self.logger.log_error(reason)
            return False, reason
    
    def validate_balance_for_trade(self, current_balance: float, trade_amount: float) -> Tuple[bool, str]:
        """
        Validate wallet balance for trade execution.
        
        Args:
            current_balance: Current SOL balance
            trade_amount: Amount to trade
            
        Returns:
            (is_valid, reason)
        """
        try:
            # Check 1: Sufficient balance
            if current_balance < trade_amount:
                reason = f"Insufficient balance: {current_balance} < {trade_amount} SOL"
                return False, reason
            
            # Check 2: Reserve balance for fees
            reserve_amount = 0.01  # Reserve 0.01 SOL for transaction fees
            if current_balance - trade_amount < reserve_amount:
                reason = f"Insufficient balance after trade: {current_balance - trade_amount} < {reserve_amount} SOL"
                return False, reason
            
            # Check 3: Maximum position size
            max_position_pct = 0.5  # Maximum 50% of balance per trade
            if trade_amount > current_balance * max_position_pct:
                reason = f"Trade too large: {trade_amount} > {current_balance * max_position_pct} SOL (50% max)"
                return False, reason
            
            return True, "Balance validation passed"
            
        except Exception as e:
            reason = f"Balance validation error: {str(e)}"
            self.logger.log_error(reason)
            return False, reason
    
    def assess_swap_risk(self, quote: Dict[str, Any], token_data: Dict[str, Any], 
                        trade_amount_sol: float, current_balance: float) -> Dict[str, Any]:
        """
        Comprehensive risk assessment for a swap operation.
        
        Args:
            quote: Jupiter quote data
            token_data: Token information
            trade_amount_sol: Amount of SOL being traded
            current_balance: Current wallet balance
            
        Returns:
            Risk assessment result
        """
        risk_assessment = {
            "overall_risk": "LOW",
            "risk_score": 0,
            "checks_passed": 0,
            "checks_failed": 0,
            "warnings": [],
            "critical_issues": [],
            "recommendation": "PROCEED"
        }
        
        try:
            # Quote validation
            quote_valid, quote_reason = self.validate_quote(quote, trade_amount_sol)
            if quote_valid:
                risk_assessment["checks_passed"] += 1
            else:
                risk_assessment["checks_failed"] += 1
                risk_assessment["critical_issues"].append(quote_reason)
                risk_assessment["risk_score"] += 30
            
            # Token validation
            token_valid, token_reason = self.validate_token_for_trading(token_data)
            if token_valid:
                risk_assessment["checks_passed"] += 1
            else:
                risk_assessment["checks_failed"] += 1
                risk_assessment["critical_issues"].append(token_reason)
                risk_assessment["risk_score"] += 25
            
            # Balance validation
            balance_valid, balance_reason = self.validate_balance_for_trade(current_balance, trade_amount_sol)
            if balance_valid:
                risk_assessment["checks_passed"] += 1
            else:
                risk_assessment["checks_failed"] += 1
                risk_assessment["critical_issues"].append(balance_reason)
                risk_assessment["risk_score"] += 20
            
            # Additional risk factors
            price_impact = abs(quote.get("priceImpactPct", 0))
            if price_impact > 2.0:  # Warning threshold
                risk_assessment["warnings"].append(f"High price impact: {price_impact}%")
                risk_assessment["risk_score"] += 10
            
            if trade_amount_sol > 0.1:  # Warning for large trades
                risk_assessment["warnings"].append(f"Large trade size: {trade_amount_sol} SOL")
                risk_assessment["risk_score"] += 5
            
            # Determine overall risk level
            if risk_assessment["risk_score"] >= 50:
                risk_assessment["overall_risk"] = "HIGH"
                risk_assessment["recommendation"] = "REJECT"
            elif risk_assessment["risk_score"] >= 25:
                risk_assessment["overall_risk"] = "MEDIUM"
                risk_assessment["recommendation"] = "CAUTION"
            else:
                risk_assessment["overall_risk"] = "LOW"
                risk_assessment["recommendation"] = "PROCEED"
            
            # Log risk assessment
            self.logger.log_system("Risk Assessment", risk_assessment)
            
            return risk_assessment
            
        except Exception as e:
            self.logger.log_error(f"Risk assessment error: {str(e)}")
            return {
                "overall_risk": "HIGH",
                "risk_score": 100,
                "checks_passed": 0,
                "checks_failed": 1,
                "warnings": [],
                "critical_issues": [f"Risk assessment failed: {str(e)}"],
                "recommendation": "REJECT"
            }
    
    def monitor_transaction_performance(self, signature: str, start_time: float) -> Dict[str, Any]:
        """
        Monitor transaction performance and record metrics.
        
        Args:
            signature: Transaction signature
            start_time: Transaction start time
            
        Returns:
            Performance metrics
        """
        try:
            end_time = time.time()
            execution_time = end_time - start_time
            
            performance_metrics = {
                "signature": signature,
                "execution_time": execution_time,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "completed"
            }
            
            # Add to transaction history
            self.transaction_history.append(performance_metrics)
            
            # Keep only last 100 transactions
            if len(self.transaction_history) > 100:
                self.transaction_history = self.transaction_history[-100:]
            
            # Performance warnings
            if execution_time > 30:  # 30 second warning threshold
                performance_metrics["warning"] = "Slow transaction execution"
                self.logger.log_system("Performance Warning", performance_metrics)
            
            return performance_metrics
            
        except Exception as e:
            self.logger.log_error(f"Performance monitoring error: {str(e)}")
            return {"error": str(e)}
    
    def get_risk_statistics(self) -> Dict[str, Any]:
        """
        Get risk management statistics.
        
        Returns:
            Risk statistics
        """
        try:
            return {
                "risk_flags_count": len(self.risk_flags),
                "price_impact_violations": self.price_impact_violations,
                "slippage_violations": self.slippage_violations,
                "transactions_monitored": len(self.transaction_history),
                "average_execution_time": self._calculate_average_execution_time(),
                "risk_thresholds": {
                    "max_price_impact": self.max_price_impact,
                    "max_slippage_bps": self.max_slippage_bps,
                    "max_trade_size_sol": self.max_trade_size_sol,
                    "min_liquidity_usd": self.min_liquidity_usd
                }
            }
        except Exception as e:
            self.logger.log_error(f"Risk statistics error: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_total_fees(self, quote: Dict[str, Any]) -> float:
        """Calculate total fees from a quote."""
        try:
            # Jupiter quotes include fee information in the route plan
            route_plan = quote.get("routePlan", [])
            total_fees = 0
            
            for step in route_plan:
                fee_amount = step.get("feeAmount", 0)
                if fee_amount:
                    total_fees += int(fee_amount) / 1_000_000_000  # Convert to SOL
            
            return total_fees
        except Exception:
            return 0.001  # Default fee estimate
    
    def _calculate_average_execution_time(self) -> float:
        """Calculate average transaction execution time."""
        try:
            if not self.transaction_history:
                return 0.0
            
            execution_times = [tx.get("execution_time", 0) for tx in self.transaction_history]
            return sum(execution_times) / len(execution_times)
        except Exception:
            return 0.0


# Global risk manager instance
risk_manager = None


def get_risk_manager() -> Optional[JupiterRiskManager]:
    """Get the global risk manager instance."""
    global risk_manager
    return risk_manager


def initialize_risk_manager(logger: AuracleLogger) -> JupiterRiskManager:
    """Initialize the global risk manager instance."""
    global risk_manager
    risk_manager = JupiterRiskManager(logger)
    return risk_manager
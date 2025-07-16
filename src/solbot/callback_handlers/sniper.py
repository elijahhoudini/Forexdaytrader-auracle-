
# Contact Author for your project
# Contact Info
# https://t.me/idioRusty

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class AITrader:
    """Autonomous AI trader that buys and sells coins for profit using intelligent logic"""
    
    def __init__(self, jupiter_client, risk_evaluator, discovery, data_manager):
        self.jupiter_client = jupiter_client
        self.risk_evaluator = risk_evaluator
        self.discovery = discovery
        self.data_manager = data_manager
        self.active = False
        self.trading_interval = 30  # seconds between trading cycles
        self.stats = {
            "trades_executed": 0,
            "successful_trades": 0,
            "total_profit": 0,
            "tokens_analyzed": 0,
            "positions_held": 0
        }
        self.positions = {}  # Track current positions
        self.profit_threshold = 0.171  # 17.1% profit target
        self.stop_loss = 0.02  # 2% stop loss
        
    async def start_autonomous_trading(self, user_id: str, amount_sol: float = None):
        """Start autonomous AI trading"""
        if self.active:
            return {"success": False, "error": "AI trader already active"}
        
        # Calculate 10% of wallet balance if amount not specified
        if amount_sol is None:
            wallet_balance = await self._get_wallet_balance(user_id)
            if wallet_balance:
                # Use 10% of balance, but leave 0.005 SOL for gas fees
                available_balance = max(0, wallet_balance - 0.005)
                amount_sol = min(available_balance * 0.1, available_balance - 0.001)
                amount_sol = max(0.001, amount_sol)  # Minimum 0.001 SOL
            else:
                amount_sol = 0.01  # Fallback amount
            
        self.active = True
        logger.info(f"🤖 Starting AI autonomous trading for user {user_id} with {amount_sol} SOL per trade")
        
        # Start trading loop
        asyncio.create_task(self._trading_loop(user_id, amount_sol))
        
        return {
            "success": True,
            "message": "🤖 AI autonomous trading started",
            "amount": amount_sol
        }
    
    async def stop_autonomous_trading(self):
        """Stop autonomous AI trading"""
        self.active = False
        logger.info("🤖 AI autonomous trading stopped")
        return {"success": True, "message": "🤖 AI trading stopped"}
    
    async def _trading_loop(self, user_id: str, amount_sol: float):
        """Main trading loop with AI decision making"""
        while self.active:
            try:
                await self._execute_trading_cycle(user_id, amount_sol)
                await asyncio.sleep(self.trading_interval)
            except Exception as e:
                logger.error(f"Trading loop error: {e}")
                await asyncio.sleep(5)
    
    async def _execute_trading_cycle(self, user_id: str, amount_sol: float):
        """Execute one complete trading cycle"""
        try:
            # 1. Analyze current positions for sell opportunities
            await self._analyze_positions_for_sell(user_id)
            
            # 2. Discover new tokens for potential buys
            tokens = await self.discovery.discover_tokens()
            self.stats["tokens_analyzed"] += len(tokens)
            
            if not tokens:
                logger.debug("No tokens found for analysis")
                return
            
            # 3. Apply AI logic to select best trading opportunities
            best_buy_opportunity = await self._ai_select_buy_opportunity(tokens)
            
            if best_buy_opportunity:
                await self._execute_buy_trade(user_id, best_buy_opportunity, amount_sol)
                
        except Exception as e:
            logger.error(f"Trading cycle error: {e}")
    
    async def _ai_select_buy_opportunity(self, tokens: List[Dict]) -> Optional[Dict]:
        """AI logic to select the best buy opportunity"""
        try:
            scored_tokens = []
            
            for token in tokens[:10]:  # Analyze top 10 tokens
                score = await self._calculate_ai_score(token)
                if score > 0.7:  # Only consider high-scoring tokens
                    scored_tokens.append({
                        "token": token,
                        "ai_score": score
                    })
            
            if not scored_tokens:
                return None
                
            # Sort by AI score and return best opportunity
            scored_tokens.sort(key=lambda x: x["ai_score"], reverse=True)
            return scored_tokens[0]["token"]
            
        except Exception as e:
            logger.error(f"AI selection error: {e}")
            return None
    
    async def _calculate_ai_score(self, token: Dict) -> float:
        """Calculate AI score for a token based on multiple factors"""
        try:
            score = 0.0
            
            # Volume analysis (30% weight)
            volume_24h = token.get('volume_24h', 0)
            if volume_24h > 100000:  # High volume
                score += 0.3
            elif volume_24h > 50000:  # Medium volume
                score += 0.2
            elif volume_24h > 10000:  # Low volume
                score += 0.1
            
            # Price change analysis (25% weight)
            price_change_24h = token.get('price_change_24h', 0)
            if 0.05 <= price_change_24h <= 0.15:  # 5-15% gain (momentum)
                score += 0.25
            elif 0.02 <= price_change_24h <= 0.05:  # 2-5% gain (stable)
                score += 0.15
            
            # Market cap analysis (20% weight)
            market_cap = token.get('market_cap', 0)
            if 1000000 <= market_cap <= 50000000:  # Sweet spot
                score += 0.2
            elif 500000 <= market_cap <= 1000000:  # Smaller cap
                score += 0.15
            
            # Liquidity analysis (15% weight)
            liquidity = token.get('liquidity', 0)
            if liquidity > 100000:  # High liquidity
                score += 0.15
            elif liquidity > 50000:  # Medium liquidity
                score += 0.1
            
            # Risk assessment (10% weight)
            risk_score = await self.risk_evaluator.evaluate_token(token)
            if risk_score < 0.3:  # Low risk
                score += 0.1
            elif risk_score < 0.5:  # Medium risk
                score += 0.05
            
            return min(score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            logger.error(f"AI scoring error: {e}")
            return 0.0
    
    async def _execute_buy_trade(self, user_id: str, token: Dict, amount_sol: float):
        """Execute a buy trade with AI logic"""
        try:
            token_mint = token.get('mint') or token.get('address')
            token_symbol = token.get('symbol', 'Unknown')
            
            # Execute the trade
            result = await self._execute_trade(token_mint, amount_sol, "BUY")
            
            if result["success"]:
                # Store position for tracking
                position_id = f"{user_id}_{token_mint}_{datetime.now().timestamp()}"
                self.positions[position_id] = {
                    "user_id": user_id,
                    "token_mint": token_mint,
                    "token_symbol": token_symbol,
                    "amount_sol": amount_sol,
                    "buy_price": token.get('price', 0),
                    "buy_time": datetime.now().isoformat(),
                    "ai_score": await self._calculate_ai_score(token)
                }
                
                # Log the trade
                self._log_trade(user_id, "ai_buy", token_symbol, token_mint, amount_sol, True)
                self.stats["trades_executed"] += 1
                self.stats["successful_trades"] += 1
                self.stats["positions_held"] += 1
                
                logger.info(f"🤖 AI bought {token_symbol} for user {user_id}")
                
        except Exception as e:
            logger.error(f"Buy trade execution error: {e}")
    
    async def _analyze_positions_for_sell(self, user_id: str):
        """Analyze current positions for sell opportunities"""
        try:
            positions_to_sell = []
            
            for position_id, position in list(self.positions.items()):
                if position["user_id"] != user_id:
                    continue
                
                # Get current token price
                current_price = await self._get_current_price(position["token_mint"])
                if not current_price:
                    continue
                
                buy_price = position["buy_price"]
                price_change = (current_price - buy_price) / buy_price
                
                # AI sell decision logic
                should_sell = await self._ai_should_sell(position, price_change)
                
                if should_sell:
                    positions_to_sell.append(position_id)
            
            # Execute sell trades
            for position_id in positions_to_sell:
                await self._execute_sell_trade(position_id)
                
        except Exception as e:
            logger.error(f"Position analysis error: {e}")
    
    async def _ai_should_sell(self, position: Dict, price_change: float) -> bool:
        """AI logic to determine if we should sell a position"""
        try:
            # Profit target reached
            if price_change >= self.profit_threshold:
                return True
            
            # Stop loss triggered
            if price_change <= -self.stop_loss:
                return True
            
            # Time-based exit (24 hours)
            buy_time = datetime.fromisoformat(position["buy_time"])
            if datetime.now() - buy_time > timedelta(hours=24):
                return True
            
            # AI score degradation (re-evaluate token)
            token_info = await self._get_token_info(position["token_mint"])
            if token_info:
                current_ai_score = await self._calculate_ai_score(token_info)
                if current_ai_score < 0.4:  # Score dropped significantly
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"AI sell decision error: {e}")
            return False
    
    async def _execute_sell_trade(self, position_id: str):
        """Execute a sell trade"""
        try:
            position = self.positions.get(position_id)
            if not position:
                return
            
            # Execute the trade
            result = await self._execute_trade(
                position["token_mint"], 
                position["amount_sol"], 
                "SELL"
            )
            
            if result["success"]:
                # Calculate profit
                current_price = await self._get_current_price(position["token_mint"])
                if current_price:
                    profit = (current_price - position["buy_price"]) / position["buy_price"] * position["amount_sol"]
                    self.stats["total_profit"] += profit
                
                # Log the trade
                self._log_trade(
                    position["user_id"], 
                    "ai_sell", 
                    position["token_symbol"], 
                    position["token_mint"], 
                    position["amount_sol"], 
                    True
                )
                
                # Remove position
                del self.positions[position_id]
                self.stats["positions_held"] -= 1
                
                logger.info(f"🤖 AI sold {position['token_symbol']} for user {position['user_id']}")
                
        except Exception as e:
            logger.error(f"Sell trade execution error: {e}")
    
    async def _execute_trade(self, token_mint: str, amount_sol: float, trade_type: str) -> Dict:
        """Execute a trade via Jupiter"""
        try:
            # This is a demo implementation
            # In production, this would execute real trades via Jupiter
            return {
                "success": True,
                "signature": f"demo_{int(datetime.now().timestamp())}",
                "trade_type": trade_type
            }
        except Exception as e:
            logger.error(f"Trade execution error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _get_current_price(self, token_mint: str) -> Optional[float]:
        """Get current price of a token"""
        try:
            # Implementation would fetch real price
            return 1.0  # Placeholder
        except Exception as e:
            logger.error(f"Price fetch error: {e}")
            return None
    
    async def _get_token_info(self, token_mint: str) -> Optional[Dict]:
        """Get current token information"""
        try:
            # Implementation would fetch real token data
            return {}  # Placeholder
        except Exception as e:
            logger.error(f"Token info fetch error: {e}")
            return None
    
    def _log_trade(self, user_id: str, action: str, token: str, token_mint: str, amount: float, success: bool):
        """Log trade to data manager"""
        try:
            trade_data = {
                "action": action,
                "token": token,
                "token_mint": token_mint,
                "amount": amount,
                "success": success,
                "signature": f"demo_{int(datetime.now().timestamp())}",
                "demo_mode": True,
                "trade_type": "BUY" if "buy" in action else "SELL",
                "risk_score": 0,
                "timestamp": datetime.now().isoformat()
            }
            
            self.data_manager.log_trade(user_id, trade_data)
            
        except Exception as e:
            logger.error(f"Trade logging error: {e}")
    
    def get_stats(self) -> Dict:
        """Get AI trader statistics"""
        return {
            **self.stats,
            "active": self.active,
            "positions_count": len(self.positions)
        }
    
    def get_positions(self) -> Dict:
        """Get current positions"""
        return self.positions.copy()
    
    async def _get_wallet_balance(self, user_id: str) -> Optional[float]:
        """Get wallet balance for user"""
        try:
            # This would connect to actual wallet/blockchain to get balance
            # For demo, return a mock balance
            return 1.0  # Mock 1 SOL balance
        except Exception as e:
            logger.error(f"Failed to get wallet balance: {e}")
            return None

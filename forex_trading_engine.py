"""
Forex Trading Engine
===================

Core trading engine for Forex markets replacing Solana token trading.
Handles trade execution, position management, and risk control for currency pairs.

Supports:
- MetaTrader 5 integration for live trading
- Demo trading for testing
- Multiple broker webhook integration
- Position sizing and risk management
- Real-time PnL tracking
"""

import asyncio
import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging
import pandas as pd
import aiohttp

# Import our Forex modules
from forex_market_data import ForexMarketData
from forex_technical_indicators import ForexTechnicalIndicators

logger = logging.getLogger(__name__)

class ForexPosition:
    """Represents an open Forex position."""
    
    def __init__(self, pair: str, direction: str, entry_price: float, 
                 size: float, entry_time: datetime = None):
        self.pair = pair
        self.direction = direction  # 'long' or 'short'
        self.entry_price = entry_price
        self.size = size  # Position size in lots
        self.entry_time = entry_time or datetime.now()
        self.current_price = entry_price
        self.unrealized_pnl = 0.0
        self.stop_loss = None
        self.take_profit = None
        self.trailing_stop = None
        
    def update_price(self, current_price: float):
        """Update current price and calculate unrealized PnL."""
        self.current_price = current_price
        
        if self.direction == 'long':
            pips = (current_price - self.entry_price) * 10000  # For most pairs
            if self.pair.endswith('JPY'):
                pips = (current_price - self.entry_price) * 100  # JPY pairs
        else:  # short
            pips = (self.entry_price - current_price) * 10000
            if self.pair.endswith('JPY'):
                pips = (self.entry_price - current_price) * 100
        
        # Calculate PnL (simplified calculation)
        pip_value = 10 if self.pair.endswith('JPY') else 1  # Standard lot pip value
        self.unrealized_pnl = pips * pip_value * self.size
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert position to dictionary."""
        return {
            'pair': self.pair,
            'direction': self.direction,
            'entry_price': self.entry_price,
            'current_price': self.current_price,
            'size': self.size,
            'entry_time': self.entry_time.isoformat(),
            'unrealized_pnl': self.unrealized_pnl,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit
        }

class ForexTradingEngine:
    """
    Main Forex trading engine replacing Solana functionality.
    """
    
    def __init__(self):
        """Initialize Forex trading engine."""
        self.market_data = ForexMarketData()
        self.indicators = ForexTechnicalIndicators()
        
        # Trading configuration - LIVE TRADING ONLY
        self.max_positions = int(os.getenv('MAX_FOREX_POSITIONS', '5'))
        self.max_risk_per_trade = float(os.getenv('MAX_RISK_PER_TRADE', '0.02'))  # 2% risk per trade
        self.account_balance = float(os.getenv('FOREX_ACCOUNT_BALANCE', '10000'))  # Default $10,000
        
        # Position management
        self.positions: Dict[str, ForexPosition] = {}
        self.trade_history: List[Dict[str, Any]] = []
        self.daily_pnl = 0.0
        self.total_pnl = 0.0
        
        # MetaTrader integration
        self.mt5_enabled = os.getenv('MT5_ENABLED', 'false').lower() == 'true'
        self.mt5_login = os.getenv('MT5_LOGIN')
        self.mt5_password = os.getenv('MT5_PASSWORD')
        self.mt5_server = os.getenv('MT5_SERVER')
        
        # Webhook integration
        self.webhook_url = os.getenv('FOREX_WEBHOOK_URL')
        self.webhook_enabled = bool(self.webhook_url)
        
        # Risk management
        self.max_daily_loss = float(os.getenv('MAX_DAILY_LOSS', '500'))  # $500 max daily loss
        self.max_drawdown = float(os.getenv('MAX_DRAWDOWN', '1000'))  # $1000 max drawdown
        
        # Trading hours (24/5 market)
        self.trading_enabled = True
        
        logger.info(f"ForexTradingEngine initialized - LIVE TRADING ONLY")
        logger.info(f"Account balance: ${self.account_balance}")
        logger.info(f"Max positions: {self.max_positions}")
        logger.info(f"Max risk per trade: {self.max_risk_per_trade * 100}%")
    
    async def initialize(self):
        """Initialize trading engine and connections."""
        try:
            # Initialize MT5 if enabled
            if self.mt5_enabled:
                await self._initialize_mt5()
            
            # Test market data connection
            test_price = await self.market_data.get_current_price('EURUSD')
            if test_price:
                logger.info(f"Market data connection successful: EURUSD @ {test_price['mid']:.5f}")
            else:
                logger.warning("Market data connection failed")
            
            # Load existing positions if any
            await self._load_positions()
            
            logger.info("Forex trading engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize trading engine: {e}")
            return False
    
    async def _initialize_mt5(self):
        """Initialize MetaTrader 5 connection for LIVE TRADING ONLY."""
        try:
            if self.mt5_enabled:
                logger.info("🔴 Initializing MT5 for LIVE TRADING")
                # Real MT5 implementation
                try:
                    import MetaTrader5 as mt5
                    
                    # Initialize the MT5 terminal
                    if not mt5.initialize():
                        logger.error("❌ MT5 initialize() failed")
                        return False
                    
                    # Login to the trading account
                    if not mt5.login(int(self.mt5_login), self.mt5_password, self.mt5_server):
                        logger.error(f"❌ MT5 login failed for account {self.mt5_login}")
                        mt5.shutdown()
                        return False
                    
                    # Verify account info
                    account_info = mt5.account_info()
                    if account_info is None:
                        logger.error("❌ Failed to get account info")
                        mt5.shutdown()
                        return False
                    
                    logger.info(f"✅ MT5 Connected - Account: {account_info.login}")
                    logger.info(f"💰 Balance: ${account_info.balance}")
                    logger.info(f"🏦 Server: {account_info.server}")
                    
                    return True
                    
                except ImportError:
                    logger.error("❌ MetaTrader5 package not installed. Install with: pip install MetaTrader5")
                    return False
            else:
                logger.info("ℹ️ MT5 not enabled")
                return True
                
        except Exception as e:
            logger.error(f"❌ MT5 initialization failed: {e}")
            return False
    
    async def _load_positions(self):
        """Load existing positions from storage."""
        try:
            # In a real implementation, load from database or file
            # For now, start with empty positions
            self.positions = {}
            logger.info("Positions loaded")
        except Exception as e:
            logger.error(f"Failed to load positions: {e}")
    
    async def analyze_pair(self, pair: str, timeframe: str = '1hour') -> Dict[str, Any]:
        """
        Analyze a currency pair and generate trading signals.
        
        Args:
            pair: Currency pair (e.g., 'EURUSD')
            timeframe: Analysis timeframe
            
        Returns:
            Analysis results with signals and recommendations
        """
        try:
            # Get current price
            current_price = await self.market_data.get_current_price(pair)
            if not current_price:
                return {'error': f'Could not get current price for {pair}'}
            
            # Get historical data for technical analysis
            historical_data = await self.market_data.get_historical_data(pair, timeframe, 100)
            if historical_data is None or len(historical_data) < 20:
                return {'error': f'Insufficient historical data for {pair}'}
            
            # Generate technical signals
            signals = self.indicators.generate_signals(historical_data)
            
            # Add current price information
            signals['current_price'] = current_price
            signals['pair'] = pair
            signals['timeframe'] = timeframe
            signals['analysis_time'] = datetime.now()
            
            # Calculate position sizing recommendation
            if signals['overall_score'] != 0:
                position_size = self._calculate_position_size(pair, current_price['mid'])
                signals['recommended_size'] = position_size
            
            return signals
            
        except Exception as e:
            logger.error(f"Error analyzing pair {pair}: {e}")
            return {'error': str(e)}
    
    def _calculate_position_size(self, pair: str, price: float) -> float:
        """
        Calculate optimal position size based on risk management.
        
        Args:
            pair: Currency pair
            price: Current price
            
        Returns:
            Position size in lots
        """
        try:
            # Risk amount (e.g., 2% of account balance)
            risk_amount = self.account_balance * self.max_risk_per_trade
            
            # Estimate stop loss distance (simplified - would use ATR in practice)
            stop_loss_pips = 50  # Default 50 pips stop loss
            
            # Calculate pip value for position sizing
            if pair.endswith('JPY'):
                pip_value = 1000 / price  # For JPY pairs
            else:
                pip_value = 10000 / price  # For other pairs
            
            # Calculate position size
            position_size = risk_amount / (stop_loss_pips * pip_value)
            
            # Round to standard lot sizes (0.01 minimum)
            position_size = round(position_size, 2)
            
            # Ensure minimum and maximum limits
            min_size = 0.01
            max_size = 1.0  # Maximum 1 lot per trade
            
            return max(min_size, min(max_size, position_size))
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0.01  # Default minimum size
    
    async def execute_trade(self, pair: str, direction: str, size: float, 
                           stop_loss: float = None, take_profit: float = None) -> Dict[str, Any]:
        """
        Execute a Forex trade.
        
        Args:
            pair: Currency pair
            direction: 'long' or 'short'
            size: Position size in lots
            stop_loss: Stop loss price (optional)
            take_profit: Take profit price (optional)
            
        Returns:
            Trade execution result
        """
        try:
            # Check if we can open new positions
            if len(self.positions) >= self.max_positions:
                return {'error': 'Maximum positions reached'}
            
            # Check daily loss limit
            if self.daily_pnl < -self.max_daily_loss:
                return {'error': 'Daily loss limit reached'}
            
            # Get current price
            current_price = await self.market_data.get_current_price(pair)
            if not current_price:
                return {'error': f'Could not get current price for {pair}'}
            
            # Use bid/ask spread for realistic execution
            execution_price = current_price['ask'] if direction == 'long' else current_price['bid']
            
            if self.mt5_enabled:
                # LIVE MT5 execution
                logger.info("🔴 LIVE TRADING: Executing real MT5 trade")
                result = await self._execute_mt5_trade(pair, direction, size, execution_price,
                                                     stop_loss, take_profit)
            elif self.webhook_enabled:
                # LIVE Webhook execution
                logger.info("🔴 LIVE TRADING: Executing real webhook trade")
                result = await self._execute_webhook_trade(pair, direction, size, execution_price,
                                                         stop_loss, take_profit)
            else:
                return {'error': 'No live trading interface configured. Enable MT5 or webhook for real money trading. No simulation modes available.'}
            
            # Record trade in history
            if result.get('success'):
                trade_record = {
                    'pair': pair,
                    'direction': direction,
                    'size': size,
                    'entry_price': execution_price,
                    'entry_time': datetime.now(),
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'status': 'open'
                }
                self.trade_history.append(trade_record)
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return {'error': str(e)}
    
    async def _execute_mt5_trade(self, pair: str, direction: str, size: float,
                               price: float, stop_loss: float = None,
                               take_profit: float = None) -> Dict[str, Any]:
        """Execute REAL trade via MetaTrader 5 - LIVE TRADING."""
        try:
            import MetaTrader5 as mt5
            
            # Prepare the trade request
            symbol = pair.replace('/', '')  # Convert EUR/USD to EURUSD
            action = mt5.TRADE_ACTION_DEAL
            type_filling = mt5.ORDER_FILLING_IOC
            
            # Determine order type
            if direction.lower() == 'long':
                order_type = mt5.ORDER_TYPE_BUY
            else:
                order_type = mt5.ORDER_TYPE_SELL
            
            # Build the trade request
            request = {
                "action": action,
                "symbol": symbol,
                "volume": size,
                "type": order_type,
                "price": price,
                "type_filling": type_filling,
                "magic": 234000,  # Magic number for identification
                "comment": "AURACLE Forex Bot Live Trade",
            }
            
            # Add stop loss and take profit if specified
            if stop_loss:
                request["sl"] = stop_loss
            if take_profit:
                request["tp"] = take_profit
            
            logger.info(f"🔴 EXECUTING LIVE MT5 TRADE: {direction} {size} lots {pair} @ {price:.5f}")
            
            # Execute the order
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                error_msg = f"MT5 order failed: {result.retcode} - {result.comment}"
                logger.error(error_msg)
                return {'error': error_msg}
            
            # Create position tracking
            position = ForexPosition(pair, direction, result.price, size)
            position.stop_loss = stop_loss
            position.take_profit = take_profit
            position_id = f"MT5_{result.order}"
            self.positions[position_id] = position
            
            logger.info(f"✅ LIVE MT5 TRADE EXECUTED: Order #{result.order}, Price: {result.price:.5f}")
            
            return {
                'success': True,
                'position_id': position_id,
                'order_id': result.order,
                'executed_price': result.price,
                'volume': result.volume,
                'type': 'live_mt5'
            }
            
        except ImportError:
            logger.error("❌ MetaTrader5 package not installed. Install with: pip install MetaTrader5")
            return {'error': 'MetaTrader5 package not installed'}
        except Exception as e:
            logger.error(f"❌ LIVE MT5 trade execution failed: {e}")
            return {'error': str(e)}
    
    async def _execute_webhook_trade(self, pair: str, direction: str, size: float,
                                   price: float, stop_loss: float = None,
                                   take_profit: float = None) -> Dict[str, Any]:
        """Execute REAL trade via webhook to live broker - LIVE TRADING."""
        try:
            trade_data = {
                'pair': pair,
                'direction': direction,
                'size': size,
                'price': price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'timestamp': datetime.now().isoformat(),
                'bot_id': 'AURACLE_FOREX_LIVE',
                'trade_type': 'LIVE'
            }
            
            logger.info(f"🔴 EXECUTING LIVE WEBHOOK TRADE: {direction} {size} lots {pair} @ {price:.5f}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=trade_data, 
                                      headers={'Content-Type': 'application/json'}) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"✅ LIVE WEBHOOK TRADE EXECUTED: {result}")
                        
                        # Create local position tracking
                        position = ForexPosition(pair, direction, price, size)
                        position.stop_loss = stop_loss
                        position.take_profit = take_profit
                        position_id = result.get('position_id', f"WEBHOOK_{pair}_{int(time.time())}")
                        self.positions[position_id] = position
                        
                        return {
                            'success': True,
                            'position_id': position_id,
                            'broker_response': result,
                            'type': 'live_webhook'
                        }
                    else:
                        error_msg = f'Live webhook trade failed with status {response.status}'
                        logger.error(f"❌ {error_msg}")
                        return {'error': error_msg}
            
        except Exception as e:
            logger.error(f"❌ LIVE webhook trade execution failed: {e}")
            return {'error': str(e)}
    
    async def close_position(self, position_id: str, reason: str = 'manual') -> Dict[str, Any]:
        """
        Close an open position.
        
        Args:
            position_id: Position identifier
            reason: Reason for closing (manual, stop_loss, take_profit, etc.)
            
        Returns:
            Close position result
        """
        try:
            if position_id not in self.positions:
                return {'error': 'Position not found'}
            
            position = self.positions[position_id]
            
            # Get current price for closing
            current_price = await self.market_data.get_current_price(position.pair)
            if not current_price:
                return {'error': 'Could not get current price for closing'}
            
            # Use appropriate price for closing (opposite of opening)
            close_price = current_price['bid'] if position.direction == 'long' else current_price['ask']
            
            # Calculate final PnL
            position.update_price(close_price)
            final_pnl = position.unrealized_pnl
            
            # Update account tracking
            self.total_pnl += final_pnl
            self.daily_pnl += final_pnl
            
            # Record closed trade
            close_record = {
                'position_id': position_id,
                'pair': position.pair,
                'direction': position.direction,
                'size': position.size,
                'entry_price': position.entry_price,
                'close_price': close_price,
                'entry_time': position.entry_time,
                'close_time': datetime.now(),
                'pnl': final_pnl,
                'reason': reason
            }
            
            # Remove from open positions
            del self.positions[position_id]
            
            # Add to trade history
            self.trade_history.append(close_record)
            
            logger.info(f"Position closed: {position_id} - PnL: ${final_pnl:.2f}")
            
            return {
                'success': True,
                'position_id': position_id,
                'close_price': close_price,
                'pnl': final_pnl,
                'reason': reason
            }
            
        except Exception as e:
            logger.error(f"Error closing position {position_id}: {e}")
            return {'error': str(e)}
    
    async def update_positions(self):
        """Update all open positions with current prices."""
        try:
            if not self.positions:
                return
            
            # Get current prices for all open pairs
            pairs = list(set(pos.pair for pos in self.positions.values()))
            prices = await self.market_data.get_multiple_prices(pairs)
            
            # Update each position
            for position_id, position in self.positions.items():
                if position.pair in prices and prices[position.pair]:
                    current_price = prices[position.pair]['mid']
                    position.update_price(current_price)
                    
                    # Check for stop loss or take profit triggers
                    await self._check_position_exits(position_id, position)
            
            # Update daily PnL
            self.daily_pnl = sum(pos.unrealized_pnl for pos in self.positions.values())
            
        except Exception as e:
            logger.error(f"Error updating positions: {e}")
    
    async def _check_position_exits(self, position_id: str, position: ForexPosition):
        """Check if position should be closed due to stop loss or take profit."""
        try:
            should_close = False
            close_reason = None
            
            current_price = position.current_price
            
            # Check stop loss
            if position.stop_loss:
                if position.direction == 'long' and current_price <= position.stop_loss:
                    should_close = True
                    close_reason = 'stop_loss'
                elif position.direction == 'short' and current_price >= position.stop_loss:
                    should_close = True
                    close_reason = 'stop_loss'
            
            # Check take profit
            if position.take_profit and not should_close:
                if position.direction == 'long' and current_price >= position.take_profit:
                    should_close = True
                    close_reason = 'take_profit'
                elif position.direction == 'short' and current_price <= position.take_profit:
                    should_close = True
                    close_reason = 'take_profit'
            
            # Close position if triggered
            if should_close:
                result = await self.close_position(position_id, close_reason)
                logger.info(f"Position auto-closed: {position_id} - {close_reason}")
                
        except Exception as e:
            logger.error(f"Error checking position exits: {e}")
    
    async def scan_opportunities(self, pairs: List[str] = None) -> List[Dict[str, Any]]:
        """
        Scan multiple currency pairs for trading opportunities.
        
        Args:
            pairs: List of pairs to scan (defaults to major pairs)
            
        Returns:
            List of trading opportunities
        """
        try:
            if pairs is None:
                pairs = self.market_data.get_supported_pairs()
            
            opportunities = []
            
            for pair in pairs:
                # Skip if we already have a position in this pair
                if any(pos.pair == pair for pos in self.positions.values()):
                    continue
                
                # Analyze the pair
                analysis = await self.analyze_pair(pair)
                
                if 'error' not in analysis:
                    score = analysis.get('overall_score', 0)
                    
                    # Consider it an opportunity if score is strong enough
                    if abs(score) >= 40:  # Strong signal threshold
                        opportunity = {
                            'pair': pair,
                            'direction': 'long' if score > 0 else 'short',
                            'confidence': abs(score),
                            'recommendation': analysis.get('recommendation'),
                            'current_price': analysis.get('current_price'),
                            'signals': {
                                'rsi': analysis.get('rsi_signal'),
                                'macd': analysis.get('macd_signal'),
                                'trend': analysis.get('trend_strength')
                            },
                            'recommended_size': analysis.get('recommended_size', 0.01)
                        }
                        opportunities.append(opportunity)
            
            # Sort by confidence (highest first)
            opportunities.sort(key=lambda x: x['confidence'], reverse=True)
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error scanning opportunities: {e}")
            return []
    
    def get_account_summary(self) -> Dict[str, Any]:
        """Get account summary with positions and PnL."""
        try:
            open_positions = [pos.to_dict() for pos in self.positions.values()]
            unrealized_pnl = sum(pos.unrealized_pnl for pos in self.positions.values())
            
            return {
                'account_balance': self.account_balance,
                'total_pnl': self.total_pnl,
                'daily_pnl': self.daily_pnl,
                'unrealized_pnl': unrealized_pnl,
                'open_positions': len(self.positions),
                'max_positions': self.max_positions,
                'positions': open_positions,
                'live_trading_only': True,
                'last_update': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error getting account summary: {e}")
            return {'error': str(e)}

# Testing function
async def test_forex_trading():
    """Test Forex trading engine functionality."""
    print("🧪 Testing Forex Trading Engine...")
    
    # Initialize trading engine
    engine = ForexTradingEngine()
    await engine.initialize()
    
    # Test market analysis
    print("\n📊 Testing market analysis...")
    analysis = await engine.analyze_pair('EURUSD')
    if 'error' not in analysis:
        print(f"✅ EURUSD Analysis Score: {analysis['overall_score']}")
        print(f"✅ Recommendation: {analysis['recommendation']}")
    else:
        print(f"❌ Analysis failed: {analysis['error']}")
    
    # Test trade execution (live only)
    print("\n💹 Testing trade execution...")
    if analysis.get('overall_score', 0) > 20:
        direction = 'long' if analysis['overall_score'] > 0 else 'short'
        trade_result = await engine.execute_trade('EURUSD', direction, 0.01)
        
        if trade_result.get('success'):
            print(f"✅ Live trade executed: {trade_result}")
            
            # Test position update
            await engine.update_positions()
            print("✅ Positions updated")
            
            # Test position closing
            position_id = trade_result['position_id']
            close_result = await engine.close_position(position_id, 'test')
            if close_result.get('success'):
                print(f"✅ Position closed: PnL ${close_result['pnl']:.2f}")
        else:
            print(f"❌ Trade execution failed: {trade_result}")
    else:
        print("ℹ️ No strong signals for trade execution test")
    
    # Test opportunity scanning
    print("\n🔍 Testing opportunity scanning...")
    opportunities = await engine.scan_opportunities(['EURUSD', 'GBPUSD'])
    print(f"✅ Found {len(opportunities)} opportunities")
    for opp in opportunities[:2]:  # Show top 2
        print(f"  - {opp['pair']}: {opp['direction']} (confidence: {opp['confidence']})")
    
    # Test account summary
    summary = engine.get_account_summary()
    print(f"\n💰 Account Summary:")
    print(f"  Balance: ${summary['account_balance']}")
    print(f"  Total PnL: ${summary['total_pnl']:.2f}")
    print(f"  Open Positions: {summary['open_positions']}")
    
    print("\n✅ Forex trading engine testing completed!")

if __name__ == "__main__":
    asyncio.run(test_forex_trading())
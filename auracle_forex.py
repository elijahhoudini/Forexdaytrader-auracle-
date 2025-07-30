"""
AURACLE Forex Trading Bot
========================

The main AURACLE bot converted for Forex trading.
Replaces all Solana functionality with Forex market operations.

Features:
- Autonomous Forex trading on major currency pairs
- Real-time technical analysis and signal generation
- Risk management and position sizing
- MetaTrader integration or webhook support
- Telegram notifications and control
- PnL tracking and performance analytics
"""

import asyncio
import logging
import os
import signal
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import traceback

# Import Forex modules
from forex_market_data import ForexMarketData
from forex_technical_indicators import ForexTechnicalIndicators
from forex_trading_engine import ForexTradingEngine

# Import existing modules that we'll adapt
from logger import AuracleLogger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AuracleForex:
    """
    AURACLE Forex Trading Bot - Main controller for autonomous Forex trading.
    
    Replaces the original Solana trading functionality with Forex market operations.
    """
    
    def __init__(self):
        """Initialize AURACLE Forex trading bot."""
        print("=" * 70)
        print("🚀 INITIALIZING AURACLE FOREX TRADING BOT")
        print("🌍 Mission: Autonomous Forex Trading for Maximum Profits")
        print("💱 Markets: EUR/USD, GBP/USD, USD/JPY, USD/CHF, AUD/USD, USD/CAD")
        print("=" * 70)
        
        # Core components
        self.market_data = ForexMarketData()
        self.trading_engine = ForexTradingEngine()
        self.indicators = ForexTechnicalIndicators()
        
        # Configuration
        self.demo_mode = os.getenv('FOREX_DEMO_MODE', 'true').lower() == 'true'
        self.autonomous_mode = os.getenv('AUTONOMOUS_TRADING', 'false').lower() == 'true'
        self.scan_interval = int(os.getenv('SCAN_INTERVAL_SECONDS', '300'))  # 5 minutes
        self.max_daily_trades = int(os.getenv('MAX_DAILY_TRADES', '10'))
        
        # Trading pairs to monitor
        self.trading_pairs = os.getenv('TRADING_PAIRS', 'EURUSD,GBPUSD,USDJPY,USDCHF,AUDUSD,USDCAD').split(',')
        
        # Performance tracking
        self.daily_trades = 0
        self.start_time = datetime.now()
        self.last_scan_time = None
        self.performance_stats = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0.0,
            'best_trade': 0.0,
            'worst_trade': 0.0
        }
        
        # Safety controls
        self.emergency_stop = False
        self.max_concurrent_positions = int(os.getenv('MAX_CONCURRENT_POSITIONS', '3'))
        
        # Telegram integration (reuse existing)
        self.telegram_enabled = os.getenv('TELEGRAM_ENABLED', 'false').lower() == 'true'
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        # Risk management
        self.daily_loss_limit = float(os.getenv('DAILY_LOSS_LIMIT', '200'))  # $200 daily loss limit
        self.max_position_size = float(os.getenv('MAX_POSITION_SIZE', '0.10'))  # 0.10 lots max
        
        logger.info(f"AURACLE Forex initialized")
        logger.info(f"Demo mode: {self.demo_mode}")
        logger.info(f"Autonomous mode: {self.autonomous_mode}")
        logger.info(f"Trading pairs: {', '.join(self.trading_pairs)}")
        logger.info(f"Scan interval: {self.scan_interval} seconds")
        
    async def initialize(self) -> bool:
        """Initialize all components."""
        try:
            logger.info("🔄 Initializing AURACLE Forex components...")
            
            # Initialize trading engine
            success = await self.trading_engine.initialize()
            if not success:
                logger.error("❌ Failed to initialize trading engine")
                return False
            
            # Test market data connection
            test_price = await self.market_data.get_current_price('EURUSD')
            if test_price:
                logger.info(f"✅ Market data connected: EURUSD @ {test_price['mid']:.5f}")
            else:
                logger.warning("⚠️ Market data connection issues")
            
            # Initialize Telegram if enabled
            if self.telegram_enabled:
                await self._send_telegram_message("🤖 AURACLE Forex Bot Started\n" +
                                                f"Mode: {'Demo' if self.demo_mode else 'Live'}\n" +
                                                f"Pairs: {', '.join(self.trading_pairs)}")
            
            logger.info("✅ AURACLE Forex initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            traceback.print_exc()
            return False
    
    async def run(self):
        """Main trading loop."""
        try:
            if not await self.initialize():
                logger.error("Failed to initialize - stopping")
                return
            
            logger.info("🚀 Starting AURACLE Forex trading loop")
            
            # Setup signal handlers for graceful shutdown
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            while not self.emergency_stop:
                try:
                    # Check if market is open
                    if not await self.market_data.is_market_open():
                        logger.info("💤 Market closed - waiting...")
                        await asyncio.sleep(300)  # Check again in 5 minutes
                        continue
                    
                    # Main trading cycle
                    await self._trading_cycle()
                    
                    # Update positions
                    await self.trading_engine.update_positions()
                    
                    # Performance reporting
                    await self._update_performance_stats()
                    
                    # Sleep until next scan
                    await asyncio.sleep(self.scan_interval)
                    
                except Exception as e:
                    logger.error(f"Error in trading loop: {e}")
                    await asyncio.sleep(60)  # Wait a minute before retrying
            
            logger.info("🛑 AURACLE Forex stopped")
            
        except KeyboardInterrupt:
            logger.info("🛑 Received shutdown signal")
        except Exception as e:
            logger.error(f"Fatal error in main loop: {e}")
            traceback.print_exc()
        finally:
            await self._shutdown()
    
    async def _trading_cycle(self):
        """Execute one complete trading cycle."""
        try:
            logger.info("🔄 Starting trading cycle...")
            self.last_scan_time = datetime.now()
            
            # Check daily limits
            if self.daily_trades >= self.max_daily_trades:
                logger.info(f"📊 Daily trade limit reached ({self.max_daily_trades})")
                return
            
            account_summary = self.trading_engine.get_account_summary()
            
            # Check daily loss limit
            if account_summary['daily_pnl'] < -self.daily_loss_limit:
                logger.warning(f"⚠️ Daily loss limit reached: ${account_summary['daily_pnl']:.2f}")
                await self._send_telegram_message(f"🚨 Daily loss limit reached: ${account_summary['daily_pnl']:.2f}")
                return
            
            # Check maximum positions
            if len(account_summary['positions']) >= self.max_concurrent_positions:
                logger.info(f"📊 Maximum positions reached ({self.max_concurrent_positions})")
                return
            
            # Scan for opportunities
            opportunities = await self.trading_engine.scan_opportunities(self.trading_pairs)
            
            if opportunities:
                logger.info(f"🔍 Found {len(opportunities)} trading opportunities")
                
                # Process top opportunities in autonomous mode
                if self.autonomous_mode:
                    await self._process_opportunities(opportunities[:3])  # Top 3 opportunities
                else:
                    # Just log opportunities in manual mode
                    for opp in opportunities[:3]:
                        logger.info(f"📈 Opportunity: {opp['pair']} {opp['direction']} " +
                                  f"(confidence: {opp['confidence']})")
            else:
                logger.info("🔍 No trading opportunities found")
            
            # Log current status
            await self._log_status(account_summary, opportunities)
            
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}")
    
    async def _process_opportunities(self, opportunities: List[Dict[str, Any]]):
        """Process trading opportunities in autonomous mode."""
        try:
            for opportunity in opportunities:
                # Skip if confidence is too low
                if opportunity['confidence'] < 60:  # Require 60% confidence
                    continue
                
                pair = opportunity['pair']
                direction = opportunity['direction']
                size = min(opportunity['recommended_size'], self.max_position_size)
                
                logger.info(f"💹 Executing trade: {direction} {size} lots {pair}")
                
                # Calculate stop loss and take profit
                current_price = opportunity['current_price']['mid']
                
                if direction == 'long':
                    stop_loss = current_price * 0.995   # 0.5% stop loss
                    take_profit = current_price * 1.015  # 1.5% take profit
                else:
                    stop_loss = current_price * 1.005   # 0.5% stop loss  
                    take_profit = current_price * 0.985  # 1.5% take profit
                
                # Execute the trade
                trade_result = await self.trading_engine.execute_trade(
                    pair, direction, size, stop_loss, take_profit
                )
                
                if trade_result.get('success'):
                    self.daily_trades += 1
                    self.performance_stats['total_trades'] += 1
                    
                    logger.info(f"✅ Trade executed: {trade_result}")
                    
                    # Send Telegram notification
                    if self.telegram_enabled:
                        message = (f"📈 Trade Executed\n"
                                 f"Pair: {pair}\n"
                                 f"Direction: {direction.upper()}\n"
                                 f"Size: {size} lots\n"
                                 f"Entry: {current_price:.5f}\n"
                                 f"Stop Loss: {stop_loss:.5f}\n"
                                 f"Take Profit: {take_profit:.5f}")
                        await self._send_telegram_message(message)
                    
                    # Limit to one trade per cycle for safety
                    break
                    
                else:
                    logger.warning(f"❌ Trade failed: {trade_result}")
                    
        except Exception as e:
            logger.error(f"Error processing opportunities: {e}")
    
    async def _update_performance_stats(self):
        """Update performance statistics."""
        try:
            account_summary = self.trading_engine.get_account_summary()
            
            # Update daily PnL
            self.performance_stats['total_pnl'] = account_summary['total_pnl']
            
            # Count winning/losing trades from history
            winning_trades = 0
            losing_trades = 0
            best_trade = 0.0
            worst_trade = 0.0
            
            for trade in self.trading_engine.trade_history:
                if 'pnl' in trade:
                    pnl = trade['pnl']
                    if pnl > 0:
                        winning_trades += 1
                        best_trade = max(best_trade, pnl)
                    elif pnl < 0:
                        losing_trades += 1
                        worst_trade = min(worst_trade, pnl)
            
            self.performance_stats.update({
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'best_trade': best_trade,
                'worst_trade': worst_trade
            })
            
        except Exception as e:
            logger.error(f"Error updating performance stats: {e}")
    
    async def _log_status(self, account_summary: Dict[str, Any], opportunities: List[Dict[str, Any]]):
        """Log current bot status."""
        try:
            uptime = datetime.now() - self.start_time
            win_rate = 0
            if self.performance_stats['total_trades'] > 0:
                win_rate = (self.performance_stats['winning_trades'] / 
                           self.performance_stats['total_trades']) * 100
            
            status_msg = (
                f"📊 AURACLE Forex Status\n"
                f"Uptime: {uptime}\n"
                f"Daily PnL: ${account_summary['daily_pnl']:.2f}\n"
                f"Total PnL: ${account_summary['total_pnl']:.2f}\n"
                f"Open Positions: {len(account_summary['positions'])}\n"
                f"Daily Trades: {self.daily_trades}/{self.max_daily_trades}\n"
                f"Win Rate: {win_rate:.1f}%\n"
                f"Opportunities: {len(opportunities)}"
            )
            
            logger.info(status_msg.replace('\n', ' | '))
            
            # Send hourly Telegram updates
            if (self.telegram_enabled and 
                datetime.now().minute == 0 and 
                datetime.now().hour % 4 == 0):  # Every 4 hours
                await self._send_telegram_message(status_msg)
                
        except Exception as e:
            logger.error(f"Error logging status: {e}")
    
    async def _send_telegram_message(self, message: str):
        """Send message via Telegram (placeholder for integration)."""
        try:
            # This would integrate with the existing Telegram bot
            # For now, just log the message
            logger.info(f"📱 Telegram: {message}")
            
            # In real implementation:
            # await telegram_bot.send_message(self.telegram_chat_id, message)
            
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum} - initiating shutdown")
        self.emergency_stop = True
    
    async def _shutdown(self):
        """Graceful shutdown procedure."""
        try:
            logger.info("🔄 Shutting down AURACLE Forex...")
            
            # Close all open positions in demo mode
            if self.demo_mode:
                for position_id in list(self.trading_engine.positions.keys()):
                    await self.trading_engine.close_position(position_id, 'shutdown')
            
            # Final performance report
            final_stats = self.performance_stats
            win_rate = 0
            if final_stats['total_trades'] > 0:
                win_rate = (final_stats['winning_trades'] / final_stats['total_trades']) * 100
            
            final_report = (
                f"📊 AURACLE Forex Final Report\n"
                f"Total Trades: {final_stats['total_trades']}\n"
                f"Win Rate: {win_rate:.1f}%\n"
                f"Total PnL: ${final_stats['total_pnl']:.2f}\n"
                f"Best Trade: ${final_stats['best_trade']:.2f}\n"
                f"Worst Trade: ${final_stats['worst_trade']:.2f}\n"
                f"Runtime: {datetime.now() - self.start_time}"
            )
            
            logger.info(final_report.replace('\n', ' | '))
            
            if self.telegram_enabled:
                await self._send_telegram_message(f"🛑 AURACLE Forex Stopped\n{final_report}")
            
            logger.info("✅ Shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Manual trading interface for testing
class ForexTradingInterface:
    """Simple interface for manual Forex trading testing."""
    
    def __init__(self):
        self.auracle = AuracleForex()
    
    async def run_interactive(self):
        """Run interactive trading session."""
        print("🎮 AURACLE Forex Interactive Mode")
        print("Commands: analyze <pair>, trade <pair> <direction> <size>, status, quit")
        
        await self.auracle.initialize()
        
        while True:
            try:
                command = input("\n> ").strip().split()
                if not command:
                    continue
                
                cmd = command[0].lower()
                
                if cmd == 'quit':
                    break
                elif cmd == 'analyze' and len(command) > 1:
                    pair = command[1].upper()
                    analysis = await self.auracle.trading_engine.analyze_pair(pair)
                    if 'error' not in analysis:
                        print(f"📊 {pair} Analysis:")
                        print(f"  Score: {analysis['overall_score']}")
                        print(f"  Recommendation: {analysis['recommendation']}")
                        print(f"  RSI: {analysis.get('rsi', 'N/A')}")
                        print(f"  Trend: {analysis.get('trend_strength', 'N/A')}")
                    else:
                        print(f"❌ Error: {analysis['error']}")
                
                elif cmd == 'trade' and len(command) >= 4:
                    pair = command[1].upper()
                    direction = command[2].lower()
                    size = float(command[3])
                    
                    result = await self.auracle.trading_engine.execute_trade(pair, direction, size)
                    if result.get('success'):
                        print(f"✅ Trade executed: {result}")
                    else:
                        print(f"❌ Trade failed: {result}")
                
                elif cmd == 'status':
                    summary = self.auracle.trading_engine.get_account_summary()
                    print(f"💰 Account Summary:")
                    print(f"  Balance: ${summary['account_balance']}")
                    print(f"  Total PnL: ${summary['total_pnl']:.2f}")
                    print(f"  Daily PnL: ${summary['daily_pnl']:.2f}")
                    print(f"  Open Positions: {summary['open_positions']}")
                
                else:
                    print("❓ Unknown command. Use: analyze, trade, status, quit")
                    
            except Exception as e:
                print(f"❌ Error: {e}")

# Main entry point
async def main():
    """Main entry point for AURACLE Forex."""
    import argparse
    
    parser = argparse.ArgumentParser(description='AURACLE Forex Trading Bot')
    parser.add_argument('--mode', choices=['auto', 'interactive', 'test'], 
                       default='auto', help='Trading mode')
    
    args = parser.parse_args()
    
    try:
        if args.mode == 'auto':
            # Autonomous trading mode
            auracle = AuracleForex()
            await auracle.run()
            
        elif args.mode == 'interactive':
            # Interactive manual trading
            interface = ForexTradingInterface()
            await interface.run_interactive()
            
        elif args.mode == 'test':
            # Test mode - run basic functionality tests
            print("🧪 Running AURACLE Forex tests...")
            
            # Test market data
            market_data = ForexMarketData()
            price = await market_data.get_current_price('EURUSD')
            print(f"✅ Market data test: EURUSD @ {price['mid']:.5f}" if price else "❌ Market data failed")
            
            # Test trading engine
            engine = ForexTradingEngine()
            await engine.initialize()
            analysis = await engine.analyze_pair('EURUSD')
            print(f"✅ Analysis test: Score {analysis.get('overall_score', 'N/A')}")
            
            print("✅ Tests completed")
        
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
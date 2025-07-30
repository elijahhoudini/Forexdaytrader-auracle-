"""
Backtesting Engine with Visualization
====================================

Comprehensive backtesting system for AURACLE Forex strategies with 
performance visualization using Matplotlib and Plotly.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

try:
    import plotly.graph_objects as go
    import plotly.subplots as sp
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Warning: Plotly not available. Using matplotlib only.")


@dataclass
class BacktestTrade:
    """Represents a completed trade in backtesting."""
    entry_time: datetime
    exit_time: datetime
    pair: str
    direction: str
    entry_price: float
    exit_price: float
    size: float
    pnl: float
    duration: timedelta
    max_profit: float
    max_loss: float
    reason: str  # How the trade was closed


@dataclass
class BacktestResults:
    """Results of a backtest run."""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    gross_profit: float
    gross_loss: float
    profit_factor: float
    max_drawdown: float
    max_drawdown_duration: timedelta
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    average_trade: float
    average_winner: float
    average_loser: float
    largest_winner: float
    largest_loser: float
    equity_curve: pd.DataFrame
    trades: List[BacktestTrade]
    initial_balance: float
    final_balance: float
    roi: float


class BacktestEngine:
    """
    Backtesting engine for Forex trading strategies.
    
    Features:
    - Historical data simulation
    - Realistic spread and slippage modeling
    - Multiple visualization options
    - Comprehensive performance metrics
    - Risk metrics calculation
    """
    
    def __init__(self, initial_balance: float = 10000, spread_pips: float = 1.5):
        """
        Initialize backtest engine.
        
        Args:
            initial_balance: Starting account balance
            spread_pips: Broker spread in pips
        """
        self.initial_balance = initial_balance
        self.spread_pips = spread_pips
        self.results: Optional[BacktestResults] = None
    
    def run_backtest(self, 
                    strategy, 
                    historical_data: pd.DataFrame, 
                    risk_config: Dict,
                    start_date: Optional[str] = None,
                    end_date: Optional[str] = None) -> BacktestResults:
        """
        Run backtest for a strategy on historical data.
        
        Args:
            strategy: Trading strategy instance
            historical_data: Historical OHLCV data
            risk_config: Risk management configuration
            start_date: Start date for backtest (YYYY-MM-DD)
            end_date: End date for backtest (YYYY-MM-DD)
            
        Returns:
            BacktestResults object
        """
        print(f"🔄 Starting backtest: {strategy.get_strategy_name()}")
        
        # Filter data by date range
        data = self._prepare_data(historical_data, start_date, end_date)
        
        if len(data) < 50:
            raise ValueError("Insufficient historical data for backtesting")
        
        # Initialize tracking variables
        balance = self.initial_balance
        equity_curve = []
        trades = []
        open_positions = {}
        max_balance = balance
        max_drawdown = 0.0
        max_dd_duration = timedelta(0)
        drawdown_start = None
        
        # Generate signals
        print(f"📊 Generating signals for {len(data)} candles...")
        signals = strategy.generate_signals(data, "EURUSD")  # Assume EURUSD for backtesting
        print(f"📈 Generated {len(signals)} trading signals")
        
        # Convert signals to DataFrame for easier processing
        signals_df = pd.DataFrame(signals) if signals else pd.DataFrame()
        
        # Simulate trading
        for i, row in data.iterrows():
            current_time = row['timestamp']
            current_price = row['close']
            
            # Update equity curve
            unrealized_pnl = self._calculate_unrealized_pnl(open_positions, current_price)
            current_equity = balance + unrealized_pnl
            equity_curve.append({
                'timestamp': current_time,
                'balance': balance,
                'equity': current_equity,
                'drawdown': max(0, max_balance - current_equity)
            })
            
            # Update max drawdown
            if current_equity > max_balance:
                max_balance = current_equity
                if drawdown_start:
                    dd_duration = current_time - drawdown_start
                    if dd_duration > max_dd_duration:
                        max_dd_duration = dd_duration
                    drawdown_start = None
            else:
                drawdown = max_balance - current_equity
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
                if not drawdown_start and drawdown > 0:
                    drawdown_start = current_time
            
            # Check for signal at current time
            current_signals = signals_df[signals_df['timestamp'] == current_time] if not signals_df.empty else []
            
            # Process new signals
            for _, signal in current_signals.iterrows() if hasattr(current_signals, 'iterrows') else []:
                if len(open_positions) < risk_config.get('max_positions', 3):
                    # Calculate position size
                    position_size = self._calculate_position_size(
                        signal.to_dict(), current_price, balance, risk_config
                    )
                    
                    if position_size > 0:
                        # Apply spread
                        if signal['signal'] == 'BUY':
                            entry_price = current_price + (self.spread_pips * 0.0001)
                        else:
                            entry_price = current_price - (self.spread_pips * 0.0001)
                        
                        # Open position
                        position_id = f"{signal['pair']}_{current_time.strftime('%Y%m%d_%H%M%S')}"
                        open_positions[position_id] = {
                            'entry_time': current_time,
                            'pair': signal['pair'],
                            'direction': signal['signal'],
                            'entry_price': entry_price,
                            'size': position_size,
                            'stop_loss': signal.get('stop_loss', 0),
                            'take_profit': signal.get('take_profit', 0),
                            'max_profit': 0,
                            'max_loss': 0
                        }
            
            # Check stop loss and take profit for open positions
            positions_to_close = []
            for pos_id, position in open_positions.items():
                # Update max profit/loss
                if position['direction'] == 'BUY':
                    unrealized = (current_price - position['entry_price']) * position['size'] * 100000
                else:
                    unrealized = (position['entry_price'] - current_price) * position['size'] * 100000
                
                position['max_profit'] = max(position['max_profit'], unrealized)
                position['max_loss'] = min(position['max_loss'], unrealized)
                
                # Check stop loss and take profit
                should_close, reason, exit_price = self._check_exit_conditions(
                    position, current_price, self.spread_pips
                )
                
                if should_close:
                    positions_to_close.append((pos_id, exit_price, reason))
            
            # Close positions
            for pos_id, exit_price, reason in positions_to_close:
                position = open_positions[pos_id]
                
                # Calculate P&L
                if position['direction'] == 'BUY':
                    pnl = (exit_price - position['entry_price']) * position['size'] * 100000
                else:
                    pnl = (position['entry_price'] - exit_price) * position['size'] * 100000
                
                # Create trade record
                trade = BacktestTrade(
                    entry_time=position['entry_time'],
                    exit_time=current_time,
                    pair=position['pair'],
                    direction=position['direction'],
                    entry_price=position['entry_price'],
                    exit_price=exit_price,
                    size=position['size'],
                    pnl=pnl,
                    duration=current_time - position['entry_time'],
                    max_profit=position['max_profit'],
                    max_loss=position['max_loss'],
                    reason=reason
                )
                trades.append(trade)
                
                # Update balance
                balance += pnl
                
                # Remove position
                del open_positions[pos_id]
        
        # Calculate performance metrics
        equity_df = pd.DataFrame(equity_curve)
        results = self._calculate_performance_metrics(trades, equity_df, self.initial_balance)
        
        self.results = results
        print(f"✅ Backtest completed: {results.total_trades} trades, {results.win_rate:.1f}% win rate, ROI: {results.roi:.1f}%")
        
        return results
    
    def create_performance_report(self, save_path: str = None) -> str:
        """
        Create a comprehensive performance report.
        
        Args:
            save_path: Optional path to save the report
            
        Returns:
            Report as string
        """
        if not self.results:
            return "No backtest results available"
        
        results = self.results
        
        report = f"""
AURACLE Forex Backtest Performance Report
=========================================

📊 TRADE STATISTICS
-------------------
Total Trades: {results.total_trades}
Winning Trades: {results.winning_trades}
Losing Trades: {results.losing_trades}
Win Rate: {results.win_rate:.2f}%

💰 PROFIT & LOSS
----------------
Initial Balance: ${results.initial_balance:,.2f}
Final Balance: ${results.final_balance:,.2f}
Total P&L: ${results.total_pnl:,.2f}
ROI: {results.roi:.2f}%

Gross Profit: ${results.gross_profit:,.2f}
Gross Loss: ${results.gross_loss:,.2f}
Profit Factor: {results.profit_factor:.2f}

📈 PERFORMANCE METRICS
----------------------
Average Trade: ${results.average_trade:.2f}
Average Winner: ${results.average_winner:.2f}
Average Loser: ${results.average_loser:.2f}
Largest Winner: ${results.largest_winner:.2f}
Largest Loser: ${results.largest_loser:.2f}

📉 RISK METRICS
---------------
Maximum Drawdown: ${results.max_drawdown:.2f} ({results.max_drawdown/results.initial_balance*100:.2f}%)
Max DD Duration: {results.max_drawdown_duration}
Sharpe Ratio: {results.sharpe_ratio:.3f}
Sortino Ratio: {results.sortino_ratio:.3f}
Calmar Ratio: {results.calmar_ratio:.3f}

🎯 TRADE ANALYSIS
-----------------
"""
        
        # Add monthly breakdown if available
        if results.trades:
            monthly_pnl = {}
            for trade in results.trades:
                month_key = trade.entry_time.strftime('%Y-%m')
                if month_key not in monthly_pnl:
                    monthly_pnl[month_key] = 0
                monthly_pnl[month_key] += trade.pnl
            
            report += "Monthly P&L:\n"
            for month, pnl in sorted(monthly_pnl.items()):
                report += f"  {month}: ${pnl:,.2f}\n"
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'w') as f:
                f.write(report)
        
        return report
    
    def plot_results(self, save_dir: str = "data/backtests") -> Dict[str, str]:
        """
        Create visualization plots for backtest results.
        
        Args:
            save_dir: Directory to save plots
            
        Returns:
            Dictionary of plot file paths
        """
        if not self.results:
            raise ValueError("No backtest results available")
        
        os.makedirs(save_dir, exist_ok=True)
        plot_paths = {}
        
        # 1. Equity Curve
        plot_paths['equity_curve'] = self._plot_equity_curve(save_dir)
        
        # 2. Drawdown Chart
        plot_paths['drawdown'] = self._plot_drawdown(save_dir)
        
        # 3. Trade Distribution
        plot_paths['trade_distribution'] = self._plot_trade_distribution(save_dir)
        
        # 4. Monthly Returns
        plot_paths['monthly_returns'] = self._plot_monthly_returns(save_dir)
        
        # 5. Interactive dashboard (if Plotly available)
        if PLOTLY_AVAILABLE:
            plot_paths['interactive_dashboard'] = self._create_interactive_dashboard(save_dir)
        
        return plot_paths
    
    def _prepare_data(self, data: pd.DataFrame, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Prepare and filter historical data."""
        df = data.copy()
        
        # Ensure timestamp column is datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Filter by date range
        if start_date:
            df = df[df['timestamp'] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df['timestamp'] <= pd.to_datetime(end_date)]
        
        return df.sort_values('timestamp').reset_index(drop=True)
    
    def _calculate_position_size(self, signal: Dict, current_price: float, balance: float, risk_config: Dict) -> float:
        """Calculate position size based on risk management."""
        max_risk_per_trade = risk_config.get('max_risk_per_trade', 0.02)
        max_position_size = risk_config.get('max_position_size', 1.0)
        
        risk_amount = balance * max_risk_per_trade
        
        # Calculate stop loss distance
        stop_loss = signal.get('stop_loss', 0)
        if stop_loss <= 0:
            stop_loss_distance = 50 * 0.0001  # Default 50 pips
        else:
            stop_loss_distance = abs(current_price - stop_loss)
        
        if stop_loss_distance <= 0:
            return 0.01
        
        # Calculate position size
        pips_at_risk = stop_loss_distance / 0.0001
        value_per_pip = 1.0  # Simplified
        lot_size = risk_amount / (pips_at_risk * value_per_pip)
        
        return max(0.01, min(lot_size, max_position_size))
    
    def _calculate_unrealized_pnl(self, positions: Dict, current_price: float) -> float:
        """Calculate total unrealized P&L for open positions."""
        total_unrealized = 0.0
        for position in positions.values():
            if position['direction'] == 'BUY':
                unrealized = (current_price - position['entry_price']) * position['size'] * 100000
            else:
                unrealized = (position['entry_price'] - current_price) * position['size'] * 100000
            total_unrealized += unrealized
        return total_unrealized
    
    def _check_exit_conditions(self, position: Dict, current_price: float, spread_pips: float) -> Tuple[bool, str, float]:
        """Check if position should be closed."""
        direction = position['direction']
        stop_loss = position['stop_loss']
        take_profit = position['take_profit']
        
        # Apply spread for exit
        if direction == 'BUY':
            exit_price = current_price - (spread_pips * 0.0001)  # Bid price
            
            # Check stop loss
            if stop_loss > 0 and exit_price <= stop_loss:
                return True, "Stop Loss", exit_price
            
            # Check take profit
            if take_profit > 0 and exit_price >= take_profit:
                return True, "Take Profit", exit_price
        
        else:  # SELL
            exit_price = current_price + (spread_pips * 0.0001)  # Ask price
            
            # Check stop loss
            if stop_loss > 0 and exit_price >= stop_loss:
                return True, "Stop Loss", exit_price
            
            # Check take profit
            if take_profit > 0 and exit_price <= take_profit:
                return True, "Take Profit", exit_price
        
        return False, "", 0.0
    
    def _calculate_performance_metrics(self, trades: List[BacktestTrade], equity_df: pd.DataFrame, initial_balance: float) -> BacktestResults:
        """Calculate comprehensive performance metrics."""
        if not trades:
            # Return default results for no trades
            return BacktestResults(
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
                total_pnl=0.0,
                gross_profit=0.0,
                gross_loss=0.0,
                profit_factor=0.0,
                max_drawdown=0.0,
                max_drawdown_duration=timedelta(0),
                sharpe_ratio=0.0,
                sortino_ratio=0.0,
                calmar_ratio=0.0,
                average_trade=0.0,
                average_winner=0.0,
                average_loser=0.0,
                largest_winner=0.0,
                largest_loser=0.0,
                equity_curve=equity_df,
                trades=trades,
                initial_balance=initial_balance,
                final_balance=initial_balance,
                roi=0.0
            )
        
        # Basic trade statistics
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t.pnl > 0])
        losing_trades = len([t for t in trades if t.pnl < 0])
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        # P&L calculations
        total_pnl = sum(t.pnl for t in trades)
        gross_profit = sum(t.pnl for t in trades if t.pnl > 0)
        gross_loss = abs(sum(t.pnl for t in trades if t.pnl < 0))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Trade averages
        average_trade = total_pnl / total_trades
        average_winner = gross_profit / winning_trades if winning_trades > 0 else 0
        average_loser = -gross_loss / losing_trades if losing_trades > 0 else 0
        
        # Largest wins/losses
        largest_winner = max((t.pnl for t in trades), default=0)
        largest_loser = min((t.pnl for t in trades), default=0)
        
        # Final balance and ROI
        final_balance = initial_balance + total_pnl
        roi = (total_pnl / initial_balance) * 100
        
        # Risk metrics
        max_drawdown = equity_df['drawdown'].max() if not equity_df.empty else 0
        
        # Calculate ratios
        if not equity_df.empty and len(equity_df) > 1:
            returns = equity_df['equity'].pct_change().dropna()
            sharpe_ratio = self._calculate_sharpe_ratio(returns)
            sortino_ratio = self._calculate_sortino_ratio(returns)
        else:
            sharpe_ratio = 0.0
            sortino_ratio = 0.0
        
        calmar_ratio = (roi / 100) / (max_drawdown / initial_balance) if max_drawdown > 0 else 0
        
        return BacktestResults(
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            total_pnl=total_pnl,
            gross_profit=gross_profit,
            gross_loss=gross_loss,
            profit_factor=profit_factor,
            max_drawdown=max_drawdown,
            max_drawdown_duration=timedelta(0),  # Would need more complex calculation
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            average_trade=average_trade,
            average_winner=average_winner,
            average_loser=average_loser,
            largest_winner=largest_winner,
            largest_loser=largest_loser,
            equity_curve=equity_df,
            trades=trades,
            initial_balance=initial_balance,
            final_balance=final_balance,
            roi=roi
        )
    
    def _calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio."""
        if len(returns) == 0 or returns.std() == 0:
            return 0.0
        
        annual_returns = returns.mean() * 252  # Assuming daily returns
        annual_vol = returns.std() * np.sqrt(252)
        
        return (annual_returns - risk_free_rate) / annual_vol
    
    def _calculate_sortino_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sortino ratio."""
        if len(returns) == 0:
            return 0.0
        
        downside_returns = returns[returns < 0]
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0.0
        
        annual_returns = returns.mean() * 252
        downside_vol = downside_returns.std() * np.sqrt(252)
        
        return (annual_returns - risk_free_rate) / downside_vol
    
    def _plot_equity_curve(self, save_dir: str) -> str:
        """Plot equity curve."""
        plt.figure(figsize=(12, 6))
        
        equity_df = self.results.equity_curve
        plt.plot(equity_df['timestamp'], equity_df['equity'], label='Equity', linewidth=2)
        plt.plot(equity_df['timestamp'], equity_df['balance'], label='Realized P&L', alpha=0.7)
        
        plt.title('Equity Curve', fontsize=16, fontweight='bold')
        plt.xlabel('Date')
        plt.ylabel('Account Value ($)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Format x-axis
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        plt.xticks(rotation=45)
        
        filename = os.path.join(save_dir, 'equity_curve.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def _plot_drawdown(self, save_dir: str) -> str:
        """Plot drawdown chart."""
        plt.figure(figsize=(12, 4))
        
        equity_df = self.results.equity_curve
        plt.fill_between(equity_df['timestamp'], 0, -equity_df['drawdown'], 
                        alpha=0.7, color='red', label='Drawdown')
        
        plt.title('Drawdown Chart', fontsize=16, fontweight='bold')
        plt.xlabel('Date')
        plt.ylabel('Drawdown ($)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Format x-axis
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        plt.xticks(rotation=45)
        
        filename = os.path.join(save_dir, 'drawdown.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def _plot_trade_distribution(self, save_dir: str) -> str:
        """Plot trade P&L distribution."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        trades = self.results.trades
        pnls = [t.pnl for t in trades]
        
        # Histogram
        ax1.hist(pnls, bins=20, alpha=0.7, edgecolor='black')
        ax1.axvline(0, color='red', linestyle='--', label='Break-even')
        ax1.set_title('Trade P&L Distribution')
        ax1.set_xlabel('P&L ($)')
        ax1.set_ylabel('Frequency')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Cumulative P&L
        cumulative_pnl = np.cumsum(pnls)
        trade_numbers = range(1, len(trades) + 1)
        ax2.plot(trade_numbers, cumulative_pnl, linewidth=2)
        ax2.set_title('Cumulative P&L by Trade')
        ax2.set_xlabel('Trade Number')
        ax2.set_ylabel('Cumulative P&L ($)')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        filename = os.path.join(save_dir, 'trade_distribution.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def _plot_monthly_returns(self, save_dir: str) -> str:
        """Plot monthly returns."""
        trades = self.results.trades
        
        # Calculate monthly returns
        monthly_pnl = {}
        for trade in trades:
            month_key = trade.entry_time.strftime('%Y-%m')
            if month_key not in monthly_pnl:
                monthly_pnl[month_key] = 0
            monthly_pnl[month_key] += trade.pnl
        
        if not monthly_pnl:
            return ""
        
        months = sorted(monthly_pnl.keys())
        returns = [monthly_pnl[month] for month in months]
        
        plt.figure(figsize=(12, 6))
        colors = ['green' if r > 0 else 'red' for r in returns]
        plt.bar(months, returns, color=colors, alpha=0.7)
        plt.axhline(0, color='black', linestyle='-', alpha=0.5)
        
        plt.title('Monthly Returns', fontsize=16, fontweight='bold')
        plt.xlabel('Month')
        plt.ylabel('Returns ($)')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        filename = os.path.join(save_dir, 'monthly_returns.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def _create_interactive_dashboard(self, save_dir: str) -> str:
        """Create interactive Plotly dashboard."""
        if not PLOTLY_AVAILABLE:
            return ""
        
        equity_df = self.results.equity_curve
        trades = self.results.trades
        
        # Create subplots
        fig = sp.make_subplots(
            rows=3, cols=2,
            subplot_titles=('Equity Curve', 'Drawdown', 'Trade P&L Distribution', 
                          'Monthly Returns', 'Trade Timeline', 'Performance Metrics'),
            specs=[[{"colspan": 2}, None],
                   [{"type": "histogram"}, {"type": "bar"}],
                   [{"colspan": 2}, None]]
        )
        
        # Equity curve
        fig.add_trace(
            go.Scatter(x=equity_df['timestamp'], y=equity_df['equity'], 
                      name='Equity', line=dict(width=2)),
            row=1, col=1
        )
        
        # Drawdown
        fig.add_trace(
            go.Scatter(x=equity_df['timestamp'], y=-equity_df['drawdown'],
                      fill='tonexty', name='Drawdown', 
                      line=dict(color='red')),
            row=1, col=1
        )
        
        # Trade P&L distribution
        pnls = [t.pnl for t in trades]
        fig.add_trace(
            go.Histogram(x=pnls, name='Trade P&L', nbinsx=20),
            row=2, col=1
        )
        
        # Monthly returns
        monthly_pnl = {}
        for trade in trades:
            month_key = trade.entry_time.strftime('%Y-%m')
            if month_key not in monthly_pnl:
                monthly_pnl[month_key] = 0
            monthly_pnl[month_key] += trade.pnl
        
        if monthly_pnl:
            months = sorted(monthly_pnl.keys())
            returns = [monthly_pnl[month] for month in months]
            colors = ['green' if r > 0 else 'red' for r in returns]
            
            fig.add_trace(
                go.Bar(x=months, y=returns, name='Monthly Returns',
                      marker_color=colors),
                row=2, col=2
            )
        
        # Trade timeline
        if trades:
            entry_times = [t.entry_time for t in trades]
            cumulative_pnl = np.cumsum([t.pnl for t in trades])
            
            fig.add_trace(
                go.Scatter(x=entry_times, y=cumulative_pnl,
                          name='Cumulative P&L', mode='lines+markers'),
                row=3, col=1
            )
        
        # Update layout
        fig.update_layout(
            height=1200,
            title_text="AURACLE Backtest Dashboard",
            showlegend=True
        )
        
        filename = os.path.join(save_dir, 'interactive_dashboard.html')
        fig.write_html(filename)
        
        return filename
"""
Risk Manager
============

Centralized risk management for AURACLE Forex trading.
Handles position sizing, daily loss limits, and drawdown monitoring.
"""

import os
import json
import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import pandas as pd


@dataclass
class Position:
    """Represents an active trading position."""
    pair: str
    direction: str  # 'BUY' or 'SELL'
    entry_price: float
    current_price: float
    size: float
    stop_loss: float
    take_profit: float
    timestamp: datetime.datetime
    unrealized_pnl: float = 0.0


@dataclass
class RiskMetrics:
    """Risk metrics for monitoring."""
    daily_pnl: float
    total_pnl: float
    max_drawdown: float
    current_drawdown: float
    daily_trades: int
    open_positions: int
    account_balance: float
    equity: float
    margin_used: float
    free_margin: float


class RiskManager:
    """
    Centralized risk management system.
    
    Features:
    - Daily loss limits
    - Position sizing based on account balance and risk per trade
    - Maximum drawdown monitoring
    - Maximum concurrent positions
    - Real-time P&L tracking
    """
    
    def __init__(self, config: Dict):
        """
        Initialize risk manager.
        
        Args:
            config: Risk management configuration
        """
        self.config = config
        self.positions: Dict[str, Position] = {}
        self.daily_trades = 0
        self.daily_pnl = 0.0
        self.total_pnl = 0.0
        self.max_drawdown = 0.0
        self.account_balance = config.get('account_balance', 10000.0)
        self.equity = self.account_balance
        self.peak_equity = self.account_balance
        
        # Risk limits
        self.max_daily_loss = config.get('max_daily_loss', 500.0)
        self.max_drawdown_limit = config.get('max_drawdown_limit', 1000.0)
        self.max_risk_per_trade = config.get('max_risk_per_trade', 0.02)
        self.max_positions = config.get('max_positions', 5)
        self.max_daily_trades = config.get('max_daily_trades', 10)
        
        # Initialize tracking
        self._load_state()
        self._reset_daily_counters_if_new_day()
    
    def can_open_position(self, signal: Dict) -> Tuple[bool, str]:
        """
        Check if a new position can be opened based on risk limits.
        
        Args:
            signal: Trading signal dictionary
            
        Returns:
            Tuple of (can_open, reason)
        """
        # Check daily loss limit
        if self.daily_pnl <= -self.max_daily_loss:
            return False, f"Daily loss limit reached: ${self.daily_pnl:.2f}"
        
        # Check maximum drawdown
        if self.max_drawdown >= self.max_drawdown_limit:
            return False, f"Maximum drawdown limit reached: ${self.max_drawdown:.2f}"
        
        # Check maximum positions
        if len(self.positions) >= self.max_positions:
            return False, f"Maximum positions limit reached: {len(self.positions)}/{self.max_positions}"
        
        # Check daily trades limit
        if self.daily_trades >= self.max_daily_trades:
            return False, f"Daily trades limit reached: {self.daily_trades}/{self.max_daily_trades}"
        
        # Check if position already exists for this pair
        pair = signal['pair']
        if pair in self.positions:
            return False, f"Position already exists for {pair}"
        
        # Check account balance
        required_margin = self._calculate_required_margin(signal)
        if required_margin > self._get_free_margin():
            return False, f"Insufficient margin: required ${required_margin:.2f}, available ${self._get_free_margin():.2f}"
        
        return True, "Position can be opened"
    
    def calculate_position_size(self, signal: Dict, current_price: float) -> float:
        """
        Calculate optimal position size based on risk per trade.
        
        Args:
            signal: Trading signal with stop loss
            current_price: Current market price
            
        Returns:
            Position size in lots
        """
        # Calculate risk amount in currency
        risk_amount = self.account_balance * self.max_risk_per_trade
        
        # Calculate stop loss distance in pips
        stop_loss = signal.get('stop_loss', 0)
        if stop_loss <= 0:
            # Default stop loss: 50 pips
            pip_value = self._get_pip_value(signal['pair'])
            stop_loss_distance = 50 * pip_value
        else:
            stop_loss_distance = abs(current_price - stop_loss)
        
        if stop_loss_distance <= 0:
            return 0.01  # Minimum position size
        
        # Calculate position size
        pip_value = self._get_pip_value(signal['pair'])
        pips_at_risk = stop_loss_distance / pip_value
        
        if pips_at_risk <= 0:
            return 0.01
        
        # Calculate lot size
        value_per_pip = self._get_value_per_pip(signal['pair'])
        lot_size = risk_amount / (pips_at_risk * value_per_pip)
        
        # Apply position size limits
        min_lot_size = 0.01
        max_lot_size = self.config.get('max_position_size', 1.0)
        
        return max(min_lot_size, min(lot_size, max_lot_size))
    
    def add_position(self, signal: Dict, position_size: float, entry_price: float) -> str:
        """
        Add a new position to tracking.
        
        Args:
            signal: Trading signal
            position_size: Position size in lots
            entry_price: Entry price
            
        Returns:
            Position ID
        """
        position_id = f"{signal['pair']}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        position = Position(
            pair=signal['pair'],
            direction=signal['signal'],
            entry_price=entry_price,
            current_price=entry_price,
            size=position_size,
            stop_loss=signal.get('stop_loss', 0),
            take_profit=signal.get('take_profit', 0),
            timestamp=datetime.datetime.now()
        )
        
        self.positions[position_id] = position
        self.daily_trades += 1
        
        self._save_state()
        return position_id
    
    def update_position(self, position_id: str, current_price: float):
        """
        Update position with current price and calculate P&L.
        
        Args:
            position_id: Position identifier
            current_price: Current market price
        """
        if position_id not in self.positions:
            return
        
        position = self.positions[position_id]
        position.current_price = current_price
        
        # Calculate unrealized P&L
        if position.direction == 'BUY':
            price_diff = current_price - position.entry_price
        else:  # SELL
            price_diff = position.entry_price - current_price
        
        position.unrealized_pnl = price_diff * position.size * self._get_contract_size(position.pair)
        
        # Update equity
        self._update_equity()
    
    def close_position(self, position_id: str, exit_price: float, reason: str = "Manual close") -> Dict:
        """
        Close a position and update P&L.
        
        Args:
            position_id: Position identifier
            exit_price: Exit price
            reason: Reason for closing
            
        Returns:
            Position close summary
        """
        if position_id not in self.positions:
            return {}
        
        position = self.positions[position_id]
        
        # Calculate realized P&L
        if position.direction == 'BUY':
            price_diff = exit_price - position.entry_price
        else:  # SELL
            price_diff = position.entry_price - exit_price
        
        realized_pnl = price_diff * position.size * self._get_contract_size(position.pair)
        
        # Update balances
        self.daily_pnl += realized_pnl
        self.total_pnl += realized_pnl
        self.account_balance += realized_pnl
        
        # Track drawdown
        self._update_drawdown()
        
        # Create close summary
        close_summary = {
            'position_id': position_id,
            'pair': position.pair,
            'direction': position.direction,
            'entry_price': position.entry_price,
            'exit_price': exit_price,
            'size': position.size,
            'realized_pnl': realized_pnl,
            'duration': datetime.datetime.now() - position.timestamp,
            'reason': reason
        }
        
        # Remove position
        del self.positions[position_id]
        
        self._save_state()
        return close_summary
    
    def check_stop_loss_take_profit(self) -> List[Dict]:
        """
        Check all positions for stop loss or take profit hits.
        
        Returns:
            List of positions to close
        """
        positions_to_close = []
        
        for position_id, position in self.positions.items():
            current_price = position.current_price
            
            should_close = False
            reason = ""
            
            if position.direction == 'BUY':
                if position.stop_loss > 0 and current_price <= position.stop_loss:
                    should_close = True
                    reason = "Stop loss hit"
                elif position.take_profit > 0 and current_price >= position.take_profit:
                    should_close = True
                    reason = "Take profit hit"
            else:  # SELL
                if position.stop_loss > 0 and current_price >= position.stop_loss:
                    should_close = True
                    reason = "Stop loss hit"
                elif position.take_profit > 0 and current_price <= position.take_profit:
                    should_close = True
                    reason = "Take profit hit"
            
            if should_close:
                positions_to_close.append({
                    'position_id': position_id,
                    'exit_price': current_price,
                    'reason': reason
                })
        
        return positions_to_close
    
    def get_risk_metrics(self) -> RiskMetrics:
        """Get current risk metrics."""
        return RiskMetrics(
            daily_pnl=self.daily_pnl,
            total_pnl=self.total_pnl,
            max_drawdown=self.max_drawdown,
            current_drawdown=self.peak_equity - self.equity,
            daily_trades=self.daily_trades,
            open_positions=len(self.positions),
            account_balance=self.account_balance,
            equity=self.equity,
            margin_used=self._get_margin_used(),
            free_margin=self._get_free_margin()
        )
    
    def is_trading_allowed(self) -> Tuple[bool, str]:
        """
        Check if trading is allowed based on current risk state.
        
        Returns:
            Tuple of (allowed, reason)
        """
        # Check daily loss limit
        if self.daily_pnl <= -self.max_daily_loss:
            return False, "Daily loss limit exceeded"
        
        # Check maximum drawdown
        current_drawdown = self.peak_equity - self.equity
        if current_drawdown >= self.max_drawdown_limit:
            return False, "Maximum drawdown exceeded"
        
        # Check daily trades
        if self.daily_trades >= self.max_daily_trades:
            return False, "Daily trades limit exceeded"
        
        return True, "Trading allowed"
    
    def _get_pip_value(self, pair: str) -> float:
        """Get pip value for currency pair."""
        if 'JPY' in pair:
            return 0.01  # JPY pairs
        return 0.0001  # Standard pairs
    
    def _get_value_per_pip(self, pair: str) -> float:
        """Get value per pip for currency pair."""
        # Simplified calculation - in real implementation,
        # this would depend on account currency and current exchange rates
        return 1.0
    
    def _get_contract_size(self, pair: str) -> float:
        """Get contract size for currency pair."""
        return 100000.0  # Standard lot size
    
    def _calculate_required_margin(self, signal: Dict) -> float:
        """Calculate required margin for position."""
        # Simplified margin calculation
        leverage = self.config.get('leverage', 100)
        position_size = self.calculate_position_size(signal, signal['entry_price'])
        contract_value = position_size * self._get_contract_size(signal['pair']) * signal['entry_price']
        return contract_value / leverage
    
    def _get_margin_used(self) -> float:
        """Calculate total margin used."""
        total_margin = 0.0
        for position in self.positions.values():
            contract_value = position.size * self._get_contract_size(position.pair) * position.entry_price
            leverage = self.config.get('leverage', 100)
            total_margin += contract_value / leverage
        return total_margin
    
    def _get_free_margin(self) -> float:
        """Calculate free margin available."""
        return self.equity - self._get_margin_used()
    
    def _update_equity(self):
        """Update equity based on current unrealized P&L."""
        unrealized_pnl = sum(pos.unrealized_pnl for pos in self.positions.values())
        self.equity = self.account_balance + unrealized_pnl
    
    def _update_drawdown(self):
        """Update maximum drawdown tracking."""
        if self.equity > self.peak_equity:
            self.peak_equity = self.equity
        
        current_drawdown = self.peak_equity - self.equity
        if current_drawdown > self.max_drawdown:
            self.max_drawdown = current_drawdown
    
    def _reset_daily_counters_if_new_day(self):
        """Reset daily counters if it's a new trading day."""
        today = datetime.date.today()
        last_reset = getattr(self, '_last_daily_reset', None)
        
        if last_reset != today:
            self.daily_trades = 0
            self.daily_pnl = 0.0
            self._last_daily_reset = today
            self._save_state()
    
    def _save_state(self):
        """Save risk manager state to file."""
        try:
            state = {
                'account_balance': self.account_balance,
                'total_pnl': self.total_pnl,
                'max_drawdown': self.max_drawdown,
                'peak_equity': self.peak_equity,
                'daily_trades': self.daily_trades,
                'daily_pnl': self.daily_pnl,
                'last_daily_reset': getattr(self, '_last_daily_reset', datetime.date.today()).isoformat(),
                'positions': {
                    pid: {
                        'pair': pos.pair,
                        'direction': pos.direction,
                        'entry_price': pos.entry_price,
                        'current_price': pos.current_price,
                        'size': pos.size,
                        'stop_loss': pos.stop_loss,
                        'take_profit': pos.take_profit,
                        'timestamp': pos.timestamp.isoformat(),
                        'unrealized_pnl': pos.unrealized_pnl
                    }
                    for pid, pos in self.positions.items()
                }
            }
            
            os.makedirs('data', exist_ok=True)
            with open('data/risk_manager_state.json', 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save risk manager state: {e}")
    
    def _load_state(self):
        """Load risk manager state from file."""
        try:
            if os.path.exists('data/risk_manager_state.json'):
                with open('data/risk_manager_state.json', 'r') as f:
                    state = json.load(f)
                
                self.account_balance = state.get('account_balance', self.account_balance)
                self.total_pnl = state.get('total_pnl', 0.0)
                self.max_drawdown = state.get('max_drawdown', 0.0)
                self.peak_equity = state.get('peak_equity', self.account_balance)
                self.daily_trades = state.get('daily_trades', 0)
                self.daily_pnl = state.get('daily_pnl', 0.0)
                
                # Load last reset date
                reset_date_str = state.get('last_daily_reset')
                if reset_date_str:
                    self._last_daily_reset = datetime.date.fromisoformat(reset_date_str)
                
                # Load positions
                for pid, pos_data in state.get('positions', {}).items():
                    position = Position(
                        pair=pos_data['pair'],
                        direction=pos_data['direction'],
                        entry_price=pos_data['entry_price'],
                        current_price=pos_data['current_price'],
                        size=pos_data['size'],
                        stop_loss=pos_data['stop_loss'],
                        take_profit=pos_data['take_profit'],
                        timestamp=datetime.datetime.fromisoformat(pos_data['timestamp']),
                        unrealized_pnl=pos_data.get('unrealized_pnl', 0.0)
                    )
                    self.positions[pid] = position
                
                self._update_equity()
        except Exception as e:
            print(f"Warning: Failed to load risk manager state: {e}")
"""
Base Strategy Interface
======================

All trading strategies must inherit from this base class and implement the required methods.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional
import pandas as pd


class BaseStrategy(ABC):
    """
    Base class for all trading strategies.
    
    All custom strategies must inherit from this class and implement:
    - generate_signals()
    - get_strategy_name()
    - get_strategy_description()
    """
    
    def __init__(self, params: Optional[Dict] = None):
        """
        Initialize the strategy with optional parameters.
        
        Args:
            params: Dictionary of strategy-specific parameters
        """
        self.params = params or {}
        self.name = self.get_strategy_name()
        self.description = self.get_strategy_description()
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame, pair: str) -> List[Dict]:
        """
        Generate trading signals based on market data.
        
        Args:
            data: OHLCV data as pandas DataFrame with columns:
                  ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            pair: Currency pair (e.g., 'EURUSD')
        
        Returns:
            List of signal dictionaries with format:
            {
                'timestamp': pd.Timestamp,
                'pair': str,
                'signal': str,  # 'BUY' or 'SELL' or 'HOLD'
                'confidence': float,  # 0.0 to 1.0
                'entry_price': float,
                'stop_loss': float,
                'take_profit': float,
                'reason': str  # Human-readable explanation
            }
        """
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Return the name of the strategy."""
        pass
    
    @abstractmethod
    def get_strategy_description(self) -> str:
        """Return a description of the strategy."""
        pass
    
    def validate_signal(self, signal: Dict) -> bool:
        """
        Validate a trading signal before execution.
        
        Args:
            signal: Signal dictionary to validate
            
        Returns:
            True if signal is valid, False otherwise
        """
        required_fields = ['timestamp', 'pair', 'signal', 'confidence', 'entry_price']
        
        # Check required fields exist
        for field in required_fields:
            if field not in signal:
                return False
        
        # Validate signal type
        if signal['signal'] not in ['BUY', 'SELL', 'HOLD']:
            return False
        
        # Validate confidence
        if not (0.0 <= signal['confidence'] <= 1.0):
            return False
        
        # Validate prices are positive
        if signal['entry_price'] <= 0:
            return False
        
        return True
    
    def get_required_indicators(self) -> List[str]:
        """
        Return list of technical indicators required by this strategy.
        
        Returns:
            List of indicator names (e.g., ['RSI', 'MACD', 'SMA_20'])
        """
        return []
    
    def get_timeframe_requirements(self) -> Dict[str, int]:
        """
        Return the timeframe requirements for this strategy.
        
        Returns:
            Dictionary with timeframe requirements:
            {
                'primary_timeframe': '1h',
                'secondary_timeframe': '4h',
                'min_candles_required': 100
            }
        """
        return {
            'primary_timeframe': '1h',
            'secondary_timeframe': '4h', 
            'min_candles_required': 50
        }
    
    def optimize_parameters(self, historical_data: pd.DataFrame) -> Dict:
        """
        Optimize strategy parameters based on historical data.
        
        Args:
            historical_data: Historical OHLCV data
            
        Returns:
            Dictionary of optimized parameters
        """
        # Default implementation returns current parameters
        return self.params.copy()
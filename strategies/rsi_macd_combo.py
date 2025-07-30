"""
RSI + MACD Combination Strategy
==============================

A classic technical analysis strategy combining RSI and MACD indicators.

Strategy Logic:
- BUY when RSI is oversold (< 30) AND MACD line crosses above signal line
- SELL when RSI is overbought (> 70) AND MACD line crosses below signal line
- Uses dynamic stop-loss and take-profit levels based on ATR

Example usage in strategies directory.
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from .base_strategy import BaseStrategy


class RSI_MACD_Strategy(BaseStrategy):
    """RSI + MACD combination strategy for Forex trading."""
    
    def __init__(self, params: Dict = None):
        """
        Initialize strategy with parameters.
        
        Default parameters:
        - rsi_period: 14
        - rsi_oversold: 30
        - rsi_overbought: 70
        - macd_fast: 12
        - macd_slow: 26
        - macd_signal: 9
        - atr_period: 14
        - risk_reward_ratio: 2.0
        """
        default_params = {
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'macd_fast': 12,
            'macd_slow': 26, 
            'macd_signal': 9,
            'atr_period': 14,
            'risk_reward_ratio': 2.0,
            'min_confidence': 0.6
        }
        
        if params:
            default_params.update(params)
        
        super().__init__(default_params)
    
    def get_strategy_name(self) -> str:
        """Return strategy name."""
        return "RSI_MACD_Combo"
    
    def get_strategy_description(self) -> str:
        """Return strategy description."""
        return ("RSI + MACD combination strategy. Generates BUY signals when RSI is oversold "
                "and MACD crosses above signal line. Generates SELL signals when RSI is "
                "overbought and MACD crosses below signal line.")
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """Calculate MACD indicator."""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Average True Range (ATR)."""
        high_low = high - low
        high_close_prev = np.abs(high - close.shift())
        low_close_prev = np.abs(low - close.shift())
        
        true_range = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        return atr
    
    def generate_signals(self, data: pd.DataFrame, pair: str) -> List[Dict]:
        """
        Generate trading signals based on RSI and MACD.
        
        Args:
            data: OHLCV data with columns ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            pair: Currency pair
            
        Returns:
            List of signal dictionaries
        """
        if len(data) < max(self.params['macd_slow'], self.params['atr_period']) + 10:
            return []  # Not enough data
        
        signals = []
        
        # Calculate indicators
        rsi = self.calculate_rsi(data['close'], self.params['rsi_period'])
        macd_data = self.calculate_macd(data['close'], 
                                      self.params['macd_fast'],
                                      self.params['macd_slow'],
                                      self.params['macd_signal'])
        atr = self.calculate_atr(data['high'], data['low'], data['close'], self.params['atr_period'])
        
        # Find MACD crossovers
        macd_line = macd_data['macd']
        signal_line = macd_data['signal']
        
        # Detect crossovers
        macd_cross_up = (macd_line > signal_line) & (macd_line.shift() <= signal_line.shift())
        macd_cross_down = (macd_line < signal_line) & (macd_line.shift() >= signal_line.shift())
        
        for i in range(1, len(data)):
            current_time = data.iloc[i]['timestamp']
            current_price = data.iloc[i]['close']
            current_rsi = rsi.iloc[i]
            current_atr = atr.iloc[i]
            
            if pd.isna(current_rsi) or pd.isna(current_atr):
                continue
            
            signal = None
            confidence = 0.0
            reason = ""
            
            # BUY signal: RSI oversold + MACD bullish crossover
            if (current_rsi < self.params['rsi_oversold'] and 
                macd_cross_up.iloc[i]):
                
                signal = 'BUY'
                confidence = self._calculate_buy_confidence(current_rsi, macd_data, i)
                reason = f"RSI oversold ({current_rsi:.1f}) + MACD bullish crossover"
                
                # Calculate stop loss and take profit
                stop_loss = current_price - (2 * current_atr)
                take_profit = current_price + (self.params['risk_reward_ratio'] * 2 * current_atr)
            
            # SELL signal: RSI overbought + MACD bearish crossover  
            elif (current_rsi > self.params['rsi_overbought'] and 
                  macd_cross_down.iloc[i]):
                
                signal = 'SELL'
                confidence = self._calculate_sell_confidence(current_rsi, macd_data, i)
                reason = f"RSI overbought ({current_rsi:.1f}) + MACD bearish crossover"
                
                # Calculate stop loss and take profit
                stop_loss = current_price + (2 * current_atr)
                take_profit = current_price - (self.params['risk_reward_ratio'] * 2 * current_atr)
            
            # Only generate signal if confidence meets minimum threshold
            if signal and confidence >= self.params['min_confidence']:
                signals.append({
                    'timestamp': current_time,
                    'pair': pair,
                    'signal': signal,
                    'confidence': confidence,
                    'entry_price': current_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'reason': reason,
                    'indicators': {
                        'rsi': current_rsi,
                        'macd': macd_line.iloc[i],
                        'macd_signal': signal_line.iloc[i],
                        'atr': current_atr
                    }
                })
        
        return signals
    
    def _calculate_buy_confidence(self, rsi: float, macd_data: Dict, index: int) -> float:
        """Calculate confidence for BUY signals."""
        confidence = 0.5  # Base confidence
        
        # Higher confidence for more oversold RSI
        if rsi < 20:
            confidence += 0.3
        elif rsi < 25:
            confidence += 0.2
        elif rsi < 30:
            confidence += 0.1
        
        # Check MACD histogram strength
        histogram = macd_data['histogram'].iloc[index]
        if histogram > 0:
            confidence += 0.1
        
        # Check trend momentum
        macd_line = macd_data['macd'].iloc[index]
        if macd_line > macd_data['macd'].iloc[index-1]:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _calculate_sell_confidence(self, rsi: float, macd_data: Dict, index: int) -> float:
        """Calculate confidence for SELL signals."""
        confidence = 0.5  # Base confidence
        
        # Higher confidence for more overbought RSI
        if rsi > 80:
            confidence += 0.3
        elif rsi > 75:
            confidence += 0.2
        elif rsi > 70:
            confidence += 0.1
        
        # Check MACD histogram strength
        histogram = macd_data['histogram'].iloc[index]
        if histogram < 0:
            confidence += 0.1
        
        # Check trend momentum
        macd_line = macd_data['macd'].iloc[index]
        if macd_line < macd_data['macd'].iloc[index-1]:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def get_required_indicators(self) -> List[str]:
        """Return required indicators."""
        return ['RSI', 'MACD', 'ATR']
    
    def get_timeframe_requirements(self) -> Dict[str, int]:
        """Return timeframe requirements."""
        return {
            'primary_timeframe': '1h',
            'secondary_timeframe': '4h',
            'min_candles_required': 50
        }
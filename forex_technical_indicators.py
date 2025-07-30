"""
Forex Technical Indicators Module
================================

Implements comprehensive technical analysis indicators for Forex trading:
- Moving Averages (SMA, EMA, WMA)
- Momentum Indicators (RSI, MACD, Stochastic)
- Volatility Indicators (Bollinger Bands, ATR)
- Trend Indicators (ADX, Parabolic SAR)
- Volume/Price Action Analysis

All indicators are optimized for Forex market characteristics.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging

logger = logging.getLogger(__name__)

class ForexTechnicalIndicators:
    """
    Comprehensive technical analysis indicators for Forex trading.
    """
    
    def __init__(self):
        """Initialize technical indicators calculator."""
        self.logger = logging.getLogger(__name__)
    
    # ==================== MOVING AVERAGES ====================
    
    def sma(self, data: pd.Series, period: int) -> pd.Series:
        """Simple Moving Average."""
        return data.rolling(window=period).mean()
    
    def ema(self, data: pd.Series, period: int) -> pd.Series:
        """Exponential Moving Average."""
        return data.ewm(span=period).mean()
    
    def wma(self, data: pd.Series, period: int) -> pd.Series:
        """Weighted Moving Average."""
        weights = np.arange(1, period + 1)
        return data.rolling(window=period).apply(
            lambda x: np.dot(x, weights) / weights.sum(), raw=True
        )
    
    # ==================== MOMENTUM INDICATORS ====================
    
    def rsi(self, data: pd.Series, period: int = 14) -> pd.Series:
        """
        Relative Strength Index (RSI).
        
        Args:
            data: Price series (typically close prices)
            period: RSI period (default: 14)
            
        Returns:
            RSI values (0-100)
        """
        delta = data.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def macd(self, data: pd.Series, fast: int = 12, slow: int = 26, 
             signal: int = 9) -> Dict[str, pd.Series]:
        """
        MACD (Moving Average Convergence Divergence).
        
        Args:
            data: Price series
            fast: Fast EMA period (default: 12)
            slow: Slow EMA period (default: 26)
            signal: Signal line EMA period (default: 9)
            
        Returns:
            Dict with MACD line, signal line, and histogram
        """
        ema_fast = self.ema(data, fast)
        ema_slow = self.ema(data, slow)
        
        macd_line = ema_fast - ema_slow
        signal_line = self.ema(macd_line, signal)
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series,
                   k_period: int = 14, d_period: int = 3) -> Dict[str, pd.Series]:
        """
        Stochastic Oscillator.
        
        Args:
            high: High price series
            low: Low price series  
            close: Close price series
            k_period: %K period (default: 14)
            d_period: %D period (default: 3)
            
        Returns:
            Dict with %K and %D lines
        """
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        
        k_percent = 100 * (close - lowest_low) / (highest_high - lowest_low)
        d_percent = k_percent.rolling(window=d_period).mean()
        
        return {
            'k_percent': k_percent,
            'd_percent': d_percent
        }
    
    # ==================== VOLATILITY INDICATORS ====================
    
    def bollinger_bands(self, data: pd.Series, period: int = 20, 
                       std_dev: float = 2.0) -> Dict[str, pd.Series]:
        """
        Bollinger Bands.
        
        Args:
            data: Price series
            period: Moving average period (default: 20)
            std_dev: Standard deviation multiplier (default: 2.0)
            
        Returns:
            Dict with upper band, middle band (SMA), and lower band
        """
        sma = self.sma(data, period)
        std = data.rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return {
            'upper': upper_band,
            'middle': sma,
            'lower': lower_band
        }
    
    def atr(self, high: pd.Series, low: pd.Series, close: pd.Series,
            period: int = 14) -> pd.Series:
        """
        Average True Range (ATR).
        
        Args:
            high: High price series
            low: Low price series
            close: Close price series
            period: ATR period (default: 14)
            
        Returns:
            ATR values
        """
        high_low = high - low
        high_close_prev = np.abs(high - close.shift(1))
        low_close_prev = np.abs(low - close.shift(1))
        
        true_range = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        
        return atr
    
    # ==================== TREND INDICATORS ====================
    
    def adx(self, high: pd.Series, low: pd.Series, close: pd.Series,
            period: int = 14) -> Dict[str, pd.Series]:
        """
        Average Directional Index (ADX) with +DI and -DI.
        
        Args:
            high: High price series
            low: Low price series
            close: Close price series
            period: ADX period (default: 14)
            
        Returns:
            Dict with ADX, +DI, and -DI
        """
        # Calculate True Range
        tr = self.atr(high, low, close, 1)
        
        # Directional Movement
        up_move = high - high.shift(1)
        down_move = low.shift(1) - low
        
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
        
        plus_dm = pd.Series(plus_dm, index=high.index)
        minus_dm = pd.Series(minus_dm, index=high.index)
        
        # Smooth the values
        atr_smooth = tr.rolling(window=period).mean()
        plus_di_smooth = plus_dm.rolling(window=period).mean()
        minus_di_smooth = minus_dm.rolling(window=period).mean()
        
        # Calculate DI values
        plus_di = 100 * plus_di_smooth / atr_smooth
        minus_di = 100 * minus_di_smooth / atr_smooth
        
        # Calculate ADX
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return {
            'adx': adx,
            'plus_di': plus_di,
            'minus_di': minus_di
        }
    
    def parabolic_sar(self, high: pd.Series, low: pd.Series, close: pd.Series,
                      af_start: float = 0.02, af_max: float = 0.2) -> pd.Series:
        """
        Parabolic SAR.
        
        Args:
            high: High price series
            low: Low price series
            close: Close price series
            af_start: Initial acceleration factor (default: 0.02)
            af_max: Maximum acceleration factor (default: 0.2)
            
        Returns:
            Parabolic SAR values
        """
        length = len(close)
        sar = np.zeros(length)
        trend = np.zeros(length)
        af = np.zeros(length)
        ep = np.zeros(length)
        
        # Initialize
        sar[0] = low.iloc[0]
        trend[0] = 1  # 1 for uptrend, -1 for downtrend
        af[0] = af_start
        ep[0] = high.iloc[0]
        
        for i in range(1, length):
            # Previous values
            prev_sar = sar[i-1]
            prev_trend = trend[i-1]
            prev_af = af[i-1]
            prev_ep = ep[i-1]
            
            # Current prices
            curr_high = high.iloc[i]
            curr_low = low.iloc[i]
            
            if prev_trend == 1:  # Uptrend
                sar[i] = prev_sar + prev_af * (prev_ep - prev_sar)
                
                # Check for trend reversal
                if curr_low <= sar[i]:
                    trend[i] = -1
                    sar[i] = prev_ep
                    af[i] = af_start
                    ep[i] = curr_low
                else:
                    trend[i] = 1
                    if curr_high > prev_ep:
                        ep[i] = curr_high
                        af[i] = min(prev_af + af_start, af_max)
                    else:
                        ep[i] = prev_ep
                        af[i] = prev_af
                        
            else:  # Downtrend
                sar[i] = prev_sar - prev_af * (prev_sar - prev_ep)
                
                # Check for trend reversal
                if curr_high >= sar[i]:
                    trend[i] = 1
                    sar[i] = prev_ep
                    af[i] = af_start
                    ep[i] = curr_high
                else:
                    trend[i] = -1
                    if curr_low < prev_ep:
                        ep[i] = curr_low
                        af[i] = min(prev_af + af_start, af_max)
                    else:
                        ep[i] = prev_ep
                        af[i] = prev_af
        
        return pd.Series(sar, index=close.index)
    
    # ==================== FOREX-SPECIFIC INDICATORS ====================
    
    def pivot_points(self, high: pd.Series, low: pd.Series, close: pd.Series) -> Dict[str, float]:
        """
        Calculate pivot points for daily trading levels.
        
        Args:
            high: Previous day's high
            low: Previous day's low
            close: Previous day's close
            
        Returns:
            Dict with pivot point and support/resistance levels
        """
        # Use the last complete values
        h = high.iloc[-1] if not pd.isna(high.iloc[-1]) else high.dropna().iloc[-1]
        l = low.iloc[-1] if not pd.isna(low.iloc[-1]) else low.dropna().iloc[-1]
        c = close.iloc[-1] if not pd.isna(close.iloc[-1]) else close.dropna().iloc[-1]
        
        pivot = (h + l + c) / 3
        
        r1 = 2 * pivot - l
        r2 = pivot + (h - l)
        r3 = h + 2 * (pivot - l)
        
        s1 = 2 * pivot - h
        s2 = pivot - (h - l)
        s3 = l - 2 * (h - pivot)
        
        return {
            'pivot': pivot,
            'r1': r1, 'r2': r2, 'r3': r3,
            's1': s1, 's2': s2, 's3': s3
        }
    
    def currency_strength(self, pairs_data: Dict[str, pd.Series]) -> Dict[str, float]:
        """
        Calculate currency strength index.
        
        Args:
            pairs_data: Dict mapping pair names to price series
            
        Returns:
            Dict with strength scores for each currency
        """
        currencies = set()
        for pair in pairs_data.keys():
            if len(pair) == 6:  # Standard format like EURUSD
                currencies.add(pair[:3])  # Base currency
                currencies.add(pair[3:])  # Quote currency
        
        strength = {currency: 0.0 for currency in currencies}
        
        for pair, prices in pairs_data.items():
            if len(pair) == 6 and not prices.empty:
                base = pair[:3]
                quote = pair[3:]
                
                # Calculate percentage change
                if len(prices) >= 2:
                    pct_change = (prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0] * 100
                    
                    # Positive change means base currency is stronger
                    strength[base] += pct_change
                    strength[quote] -= pct_change
        
        # Normalize to 0-100 scale
        if strength:
            min_strength = min(strength.values())
            max_strength = max(strength.values())
            
            if max_strength > min_strength:
                for currency in strength:
                    strength[currency] = 50 + (strength[currency] - min_strength) / (max_strength - min_strength) * 50
        
        return strength
    
    # ==================== SIGNAL GENERATION ====================
    
    def generate_signals(self, ohlc_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate comprehensive trading signals from OHLC data.
        
        Args:
            ohlc_data: DataFrame with open, high, low, close columns
            
        Returns:
            Dict with various trading signals and their scores
        """
        try:
            close = ohlc_data['close']
            high = ohlc_data['high']
            low = ohlc_data['low']
            
            signals = {}
            
            # Moving Average signals
            sma_20 = self.sma(close, 20)
            sma_50 = self.sma(close, 50)
            ema_12 = self.ema(close, 12)
            ema_26 = self.ema(close, 26)
            
            signals['ma_trend'] = 'bullish' if sma_20.iloc[-1] > sma_50.iloc[-1] else 'bearish'
            signals['ma_signal'] = 'buy' if close.iloc[-1] > sma_20.iloc[-1] else 'sell'
            
            # RSI signals
            rsi = self.rsi(close, 14)
            signals['rsi'] = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
            signals['rsi_signal'] = ('oversold' if signals['rsi'] < 30 else 
                                   'overbought' if signals['rsi'] > 70 else 'neutral')
            
            # MACD signals
            macd_data = self.macd(close)
            macd_line = macd_data['macd'].iloc[-1]
            signal_line = macd_data['signal'].iloc[-1]
            
            signals['macd_signal'] = 'bullish' if macd_line > signal_line else 'bearish'
            signals['macd_histogram'] = macd_data['histogram'].iloc[-1]
            
            # Bollinger Bands signals
            bb = self.bollinger_bands(close, 20, 2)
            current_price = close.iloc[-1]
            upper_band = bb['upper'].iloc[-1]
            lower_band = bb['lower'].iloc[-1]
            middle_band = bb['middle'].iloc[-1]
            
            if current_price > upper_band:
                signals['bb_signal'] = 'overbought'
            elif current_price < lower_band:
                signals['bb_signal'] = 'oversold'
            else:
                signals['bb_signal'] = 'neutral'
            
            signals['bb_position'] = (current_price - lower_band) / (upper_band - lower_band)
            
            # ADX trend strength
            adx_data = self.adx(high, low, close)
            signals['adx'] = adx_data['adx'].iloc[-1] if not pd.isna(adx_data['adx'].iloc[-1]) else 0
            signals['trend_strength'] = ('strong' if signals['adx'] > 25 else 
                                       'weak' if signals['adx'] < 20 else 'moderate')
            
            # Stochastic signals
            stoch = self.stochastic(high, low, close)
            signals['stochastic_k'] = stoch['k_percent'].iloc[-1] if not pd.isna(stoch['k_percent'].iloc[-1]) else 50
            signals['stochastic_signal'] = ('oversold' if signals['stochastic_k'] < 20 else 
                                          'overbought' if signals['stochastic_k'] > 80 else 'neutral')
            
            # Calculate overall signal score (-100 to +100)
            score = 0
            
            # MA contribution (±20 points)
            if signals['ma_signal'] == 'buy' and signals['ma_trend'] == 'bullish':
                score += 20
            elif signals['ma_signal'] == 'sell' and signals['ma_trend'] == 'bearish':
                score -= 20
            
            # RSI contribution (±15 points)
            if signals['rsi_signal'] == 'oversold':
                score += 15
            elif signals['rsi_signal'] == 'overbought':
                score -= 15
            
            # MACD contribution (±20 points)
            if signals['macd_signal'] == 'bullish':
                score += 20
            elif signals['macd_signal'] == 'bearish':
                score -= 20
            
            # Bollinger Bands contribution (±15 points)
            if signals['bb_signal'] == 'oversold':
                score += 15
            elif signals['bb_signal'] == 'overbought':
                score -= 15
            
            # Stochastic contribution (±10 points)
            if signals['stochastic_signal'] == 'oversold':
                score += 10
            elif signals['stochastic_signal'] == 'overbought':
                score -= 10
            
            # Trend strength modifier (reduce score if weak trend)
            if signals['trend_strength'] == 'weak':
                score = score * 0.5
            elif signals['trend_strength'] == 'strong':
                score = score * 1.2
            
            signals['overall_score'] = max(-100, min(100, score))
            signals['recommendation'] = ('strong_buy' if score > 60 else
                                       'buy' if score > 20 else
                                       'neutral' if score > -20 else
                                       'sell' if score > -60 else
                                       'strong_sell')
            
            # Pivot points for support/resistance
            signals['pivot_points'] = self.pivot_points(high, low, close)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error generating signals: {e}")
            return {
                'error': str(e),
                'overall_score': 0,
                'recommendation': 'neutral'
            }

# Example usage and testing
def test_technical_indicators():
    """Test function to verify technical indicators functionality."""
    print("🧪 Testing Forex Technical Indicators...")
    
    # Create sample OHLC data
    dates = pd.date_range(start='2024-01-01', periods=100, freq='H')
    np.random.seed(42)
    
    # Generate realistic forex price data
    base_price = 1.1000
    returns = np.random.normal(0, 0.001, 100)
    prices = [base_price]
    
    for ret in returns[1:]:
        prices.append(prices[-1] * (1 + ret))
    
    ohlc_data = pd.DataFrame({
        'datetime': dates,
        'open': prices,
        'high': [p * (1 + abs(np.random.normal(0, 0.0005))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, 0.0005))) for p in prices],
        'close': prices
    })
    ohlc_data.set_index('datetime', inplace=True)
    
    indicators = ForexTechnicalIndicators()
    
    # Test individual indicators
    print("\n📊 Testing individual indicators...")
    
    # RSI
    rsi = indicators.rsi(ohlc_data['close'])
    print(f"✅ RSI (last value): {rsi.iloc[-1]:.2f}")
    
    # MACD
    macd_data = indicators.macd(ohlc_data['close'])
    print(f"✅ MACD: {macd_data['macd'].iloc[-1]:.6f}")
    
    # Bollinger Bands
    bb = indicators.bollinger_bands(ohlc_data['close'])
    print(f"✅ Bollinger Bands - Upper: {bb['upper'].iloc[-1]:.5f}, Lower: {bb['lower'].iloc[-1]:.5f}")
    
    # Generate comprehensive signals
    print("\n📊 Testing signal generation...")
    signals = indicators.generate_signals(ohlc_data)
    
    print(f"✅ Overall Score: {signals['overall_score']}")
    print(f"✅ Recommendation: {signals['recommendation']}")
    print(f"✅ RSI Signal: {signals['rsi_signal']} (RSI: {signals['rsi']:.2f})")
    print(f"✅ MACD Signal: {signals['macd_signal']}")
    print(f"✅ Trend Strength: {signals['trend_strength']} (ADX: {signals['adx']:.2f})")
    
    print("\n✅ Technical indicators testing completed!")

if __name__ == "__main__":
    test_technical_indicators()
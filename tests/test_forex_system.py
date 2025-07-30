"""
Test Suite for AURACLE Forex Trading System
===========================================

Comprehensive tests for Forex modules, strategies, risk management, and backtesting.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tempfile
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.base_strategy import BaseStrategy
from strategies.strategy_loader import StrategyLoader
from strategies.rsi_macd_combo import RSI_MACD_Strategy
from risk_manager import RiskManager, Position
from backtest_engine import BacktestEngine
from ml_optimizer import MLSignalOptimizer
from economic_calendar import EconomicCalendar


class TestStrategy(BaseStrategy):
    """Simple test strategy for testing."""
    
    def get_strategy_name(self) -> str:
        return "TestStrategy"
    
    def get_strategy_description(self) -> str:
        return "Simple test strategy"
    
    def generate_signals(self, data: pd.DataFrame, pair: str):
        # Generate a simple test signal
        if len(data) < 10:
            return []
        
        return [{
            'timestamp': data.iloc[-1]['timestamp'],
            'pair': pair,
            'signal': 'BUY',
            'confidence': 0.8,
            'entry_price': data.iloc[-1]['close'],
            'stop_loss': data.iloc[-1]['close'] * 0.99,
            'take_profit': data.iloc[-1]['close'] * 1.02,
            'reason': 'Test signal'
        }]


@pytest.fixture
def sample_ohlcv_data():
    """Generate sample OHLCV data for testing."""
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1h')
    
    # Generate realistic price data
    prices = []
    price = 1.1000  # Starting EUR/USD price
    
    for _ in range(100):
        change = np.random.normal(0, 0.001)  # Small random changes
        price += change
        prices.append(price)
    
    # Create OHLC from close prices
    data = []
    for i, (date, close) in enumerate(zip(dates, prices)):
        high = close + abs(np.random.normal(0, 0.0005))
        low = close - abs(np.random.normal(0, 0.0005))
        open_price = prices[i-1] if i > 0 else close
        volume = np.random.randint(1000, 10000)
        
        data.append({
            'timestamp': date,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        })
    
    return pd.DataFrame(data)


@pytest.fixture
def sample_trade_data():
    """Generate sample trade data for testing."""
    trades = []
    base_time = datetime.now() - timedelta(days=30)
    
    for i in range(20):
        entry_time = base_time + timedelta(hours=i*3)
        exit_time = entry_time + timedelta(hours=2)
        pnl = np.random.normal(10, 50)  # Random P&L
        
        trades.append({
            'entry_time': entry_time.isoformat(),
            'exit_time': exit_time.isoformat(),
            'pair': 'EURUSD',
            'direction': 'BUY' if i % 2 == 0 else 'SELL',
            'entry_price': 1.1000 + np.random.normal(0, 0.01),
            'exit_price': 1.1000 + np.random.normal(0, 0.01),
            'size': 0.1,
            'pnl': pnl,
            'confidence': np.random.uniform(0.5, 1.0),
            'timestamp': entry_time.isoformat()
        })
    
    return trades


class TestBaseStrategy:
    """Test the base strategy interface."""
    
    def test_base_strategy_initialization(self):
        """Test base strategy initialization."""
        strategy = TestStrategy({'param1': 'value1'})
        
        assert strategy.params == {'param1': 'value1'}
        assert strategy.name == "TestStrategy"
        assert strategy.description == "Simple test strategy"
    
    def test_signal_validation(self):
        """Test signal validation."""
        strategy = TestStrategy()
        
        # Valid signal
        valid_signal = {
            'timestamp': datetime.now(),
            'pair': 'EURUSD',
            'signal': 'BUY',
            'confidence': 0.8,
            'entry_price': 1.1000
        }
        assert strategy.validate_signal(valid_signal)
        
        # Invalid signal - missing fields
        invalid_signal = {
            'timestamp': datetime.now(),
            'pair': 'EURUSD'
        }
        assert not strategy.validate_signal(invalid_signal)
        
        # Invalid signal - bad confidence
        invalid_signal2 = {
            'timestamp': datetime.now(),
            'pair': 'EURUSD',
            'signal': 'BUY',
            'confidence': 1.5,  # > 1.0
            'entry_price': 1.1000
        }
        assert not strategy.validate_signal(invalid_signal2)


class TestRSIMACDStrategy:
    """Test the RSI+MACD strategy."""
    
    def test_strategy_initialization(self):
        """Test RSI+MACD strategy initialization."""
        strategy = RSI_MACD_Strategy()
        
        assert strategy.get_strategy_name() == "RSI_MACD_Combo"
        assert "RSI + MACD" in strategy.get_strategy_description()
        assert 'RSI' in strategy.get_required_indicators()
        assert 'MACD' in strategy.get_required_indicators()
    
    def test_rsi_calculation(self, sample_ohlcv_data):
        """Test RSI calculation."""
        strategy = RSI_MACD_Strategy()
        rsi = strategy.calculate_rsi(sample_ohlcv_data['close'], period=14)
        
        assert len(rsi) == len(sample_ohlcv_data)
        assert not rsi.iloc[-10:].isna().any()  # Last 10 values should not be NaN
        assert (rsi >= 0).all()
        assert (rsi <= 100).all()
    
    def test_macd_calculation(self, sample_ohlcv_data):
        """Test MACD calculation."""
        strategy = RSI_MACD_Strategy()
        macd_data = strategy.calculate_macd(sample_ohlcv_data['close'])
        
        assert 'macd' in macd_data
        assert 'signal' in macd_data
        assert 'histogram' in macd_data
        assert len(macd_data['macd']) == len(sample_ohlcv_data)
    
    def test_signal_generation(self, sample_ohlcv_data):
        """Test signal generation."""
        strategy = RSI_MACD_Strategy()
        signals = strategy.generate_signals(sample_ohlcv_data, 'EURUSD')
        
        # Should return a list (might be empty)
        assert isinstance(signals, list)
        
        # If signals exist, validate them
        for signal in signals:
            assert strategy.validate_signal(signal)


class TestStrategyLoader:
    """Test the strategy loader."""
    
    def test_strategy_loader_initialization(self):
        """Test strategy loader initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            loader = StrategyLoader(temp_dir)
            assert loader.strategies_dir == temp_dir
            assert isinstance(loader.loaded_strategies, dict)
    
    def test_load_strategies(self):
        """Test loading strategies from the strategies directory."""
        loader = StrategyLoader('strategies')
        strategies = loader.load_all_strategies()
        
        # Should find the RSI_MACD_Strategy
        assert len(strategies) > 0
        assert 'RSI_MACD_Combo' in strategies
    
    def test_get_strategy_instance(self):
        """Test getting strategy instances."""
        loader = StrategyLoader('strategies')
        loader.load_all_strategies()
        
        # Get RSI_MACD strategy
        strategy = loader.get_strategy('RSI_MACD_Combo')
        assert isinstance(strategy, RSI_MACD_Strategy)
        assert strategy.get_strategy_name() == 'RSI_MACD_Combo'


class TestRiskManager:
    """Test the risk management system."""
    
    def test_risk_manager_initialization(self):
        """Test risk manager initialization."""
        config = {
            'account_balance': 10000,
            'max_daily_loss': 500,
            'max_positions': 3,
            'max_risk_per_trade': 0.02
        }
        
        risk_manager = RiskManager(config)
        
        assert risk_manager.account_balance == 10000
        assert risk_manager.max_daily_loss == 500
        assert risk_manager.max_positions == 3
        assert risk_manager.max_risk_per_trade == 0.02
    
    def test_position_size_calculation(self):
        """Test position size calculation."""
        config = {'account_balance': 10000, 'max_risk_per_trade': 0.02}
        risk_manager = RiskManager(config)
        
        signal = {
            'pair': 'EURUSD',
            'signal': 'BUY',
            'entry_price': 1.1000,
            'stop_loss': 1.0950  # 50 pips stop loss
        }
        
        position_size = risk_manager.calculate_position_size(signal, 1.1000)
        
        assert position_size > 0
        assert position_size <= 1.0  # Should not exceed max position size
    
    def test_can_open_position(self):
        """Test position opening validation."""
        config = {
            'account_balance': 10000,
            'max_daily_loss': 500,
            'max_positions': 2
        }
        risk_manager = RiskManager(config)
        
        signal = {
            'pair': 'EURUSD',
            'signal': 'BUY',
            'entry_price': 1.1000
        }
        
        # Should be able to open first position
        can_open, reason = risk_manager.can_open_position(signal)
        assert can_open
        
        # Add some positions to test limits
        risk_manager.add_position(signal, 0.1, 1.1000)
        risk_manager.add_position({**signal, 'pair': 'GBPUSD'}, 0.1, 1.3000)
        
        # Should not be able to open third position (max_positions = 2)
        can_open, reason = risk_manager.can_open_position({**signal, 'pair': 'USDJPY'})
        assert not can_open
        assert "Maximum positions" in reason


class TestBacktestEngine:
    """Test the backtesting engine."""
    
    def test_backtest_engine_initialization(self):
        """Test backtest engine initialization."""
        engine = BacktestEngine(initial_balance=10000, spread_pips=1.5)
        
        assert engine.initial_balance == 10000
        assert engine.spread_pips == 1.5
    
    def test_backtest_execution(self, sample_ohlcv_data):
        """Test backtesting execution."""
        engine = BacktestEngine(initial_balance=10000)
        strategy = TestStrategy()
        
        risk_config = {
            'max_positions': 3,
            'max_risk_per_trade': 0.02,
            'max_position_size': 1.0
        }
        
        # Run backtest
        results = engine.run_backtest(strategy, sample_ohlcv_data, risk_config)
        
        assert results is not None
        assert results.initial_balance == 10000
        assert results.total_trades >= 0
        assert isinstance(results.equity_curve, pd.DataFrame)
    
    def test_performance_report(self, sample_ohlcv_data):
        """Test performance report generation."""
        engine = BacktestEngine(initial_balance=10000)
        strategy = TestStrategy()
        
        risk_config = {'max_positions': 3, 'max_risk_per_trade': 0.02}
        
        # Run backtest
        results = engine.run_backtest(strategy, sample_ohlcv_data, risk_config)
        
        # Generate report
        report = engine.create_performance_report()
        
        assert isinstance(report, str)
        assert "AURACLE Forex Backtest Performance Report" in report
        assert "TRADE STATISTICS" in report


class TestMLOptimizer:
    """Test the ML signal optimization system."""
    
    def test_ml_optimizer_initialization(self):
        """Test ML optimizer initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {'model_dir': temp_dir, 'min_samples': 20}
            optimizer = MLSignalOptimizer(config)
            
            assert optimizer.model_dir == temp_dir
            assert optimizer.min_samples == 20
    
    def test_feature_preparation(self, sample_trade_data, sample_ohlcv_data):
        """Test feature preparation for ML training."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {'model_dir': temp_dir}
            optimizer = MLSignalOptimizer(config)
            
            # Add some technical indicators to market data
            market_data = sample_ohlcv_data.copy()
            market_data.set_index('timestamp', inplace=True)
            market_data['rsi'] = 50 + np.random.normal(0, 10, len(market_data))
            market_data['macd'] = np.random.normal(0, 0.001, len(market_data))
            market_data['macd_signal'] = np.random.normal(0, 0.001, len(market_data))
            
            features_df = optimizer.prepare_features(sample_trade_data, market_data)
            
            if not features_df.empty:
                assert 'target' in features_df.columns
                assert 'signal_confidence' in features_df.columns
                assert 'rsi' in features_df.columns
    
    def test_signal_optimization(self, sample_ohlcv_data):
        """Test signal optimization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {'model_dir': temp_dir}
            optimizer = MLSignalOptimizer(config)
            
            # Create a test signal
            signal = {
                'timestamp': datetime.now(),
                'pair': 'EURUSD',
                'signal': 'BUY',
                'confidence': 0.6,
                'entry_price': 1.1000,
                'stop_loss': 1.0950,
                'take_profit': 1.1100
            }
            
            # Add indicators to market data
            market_data = sample_ohlcv_data.copy()
            market_data['rsi'] = 50
            market_data['macd'] = 0.001
            market_data['macd_signal'] = 0.0005
            
            # Optimize signal (should return original signal if no models trained)
            optimized_signal = optimizer.optimize_signal(signal, market_data)
            
            assert 'timestamp' in optimized_signal
            assert 'confidence' in optimized_signal
            assert optimized_signal['pair'] == 'EURUSD'


class TestEconomicCalendar:
    """Test the economic calendar integration."""
    
    def test_economic_calendar_initialization(self):
        """Test economic calendar initialization."""
        config = {
            'enabled': True,
            'high_impact_pause_minutes': 30,
            'monitored_currencies': ['USD', 'EUR']
        }
        
        calendar = EconomicCalendar(config)
        
        assert calendar.enabled == True
        assert calendar.high_impact_pause_minutes == 30
        assert 'USD' in calendar.monitored_currencies
        assert 'EUR' in calendar.monitored_currencies
    
    def test_trading_pause_disabled(self):
        """Test trading pause when calendar is disabled."""
        config = {'enabled': False}
        calendar = EconomicCalendar(config)
        
        should_pause, event = calendar.should_pause_trading()
        assert should_pause == False
        assert event is None
    
    def test_calendar_summary(self):
        """Test calendar summary generation."""
        config = {'enabled': False}
        calendar = EconomicCalendar(config)
        
        summary = calendar.get_calendar_summary()
        
        assert isinstance(summary, dict)
        assert 'enabled' in summary
        assert 'total_events' in summary
        assert summary['enabled'] == False


def test_integration_workflow(sample_ohlcv_data):
    """Test integration between different components."""
    # Load strategy
    loader = StrategyLoader('strategies')
    loader.load_all_strategies()
    strategy = loader.get_strategy('RSI_MACD_Combo')
    
    # Initialize risk manager
    risk_config = {
        'account_balance': 10000,
        'max_daily_loss': 500,
        'max_positions': 3,
        'max_risk_per_trade': 0.02
    }
    risk_manager = RiskManager(risk_config)
    
    # Generate signals
    signals = strategy.generate_signals(sample_ohlcv_data, 'EURUSD')
    
    # Test signal processing through risk manager
    for signal in signals:
        can_open, reason = risk_manager.can_open_position(signal)
        if can_open:
            position_size = risk_manager.calculate_position_size(signal, signal['entry_price'])
            assert position_size > 0
    
    # Run backtest
    backtest_engine = BacktestEngine(initial_balance=10000)
    results = backtest_engine.run_backtest(strategy, sample_ohlcv_data, risk_config)
    
    assert results.initial_balance == 10000
    assert isinstance(results.total_trades, int)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
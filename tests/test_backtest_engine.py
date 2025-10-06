"""
Tests for the backtesting engine.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from src.engine.backtest import BacktestEngine
from src.strategies.moving_average import MovingAverageCrossover
from src.strategies.momentum import RSIMomentum


class TestBacktestEngine:
    """Test suite for BacktestEngine."""

    @pytest.fixture
    def engine(self):
        """Create backtest engine instance."""
        return BacktestEngine(initial_capital=100000.0, commission=0.001)

    @pytest.fixture
    def sample_data(self):
        """Create sample market data."""
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        prices = 100 + np.cumsum(np.random.randn(100) * 2)

        df = pd.DataFrame({
            'Open': prices * 0.99,
            'High': prices * 1.01,
            'Low': prices * 0.98,
            'Close': prices,
            'Volume': np.random.randint(1000000, 5000000, 100)
        }, index=dates)

        return df

    def test_initialization(self, engine):
        """Test engine initialization."""
        assert engine.initial_capital == 100000.0
        assert engine.commission == 0.001
        assert engine.strategy is None
        assert len(engine.data) == 0

    def test_invalid_capital(self):
        """Test that invalid initial capital raises error."""
        with pytest.raises(ValueError, match="Initial capital must be > 0"):
            BacktestEngine(initial_capital=-1000)

        with pytest.raises(ValueError, match="Initial capital must be > 0"):
            BacktestEngine(initial_capital=0)

    def test_invalid_commission(self):
        """Test that invalid commission raises error."""
        with pytest.raises(ValueError, match="Commission rate must be >= 0"):
            BacktestEngine(initial_capital=100000, commission=-0.01)

    def test_add_data(self, engine, sample_data):
        """Test adding market data."""
        engine.add_data('AAPL', sample_data)

        assert 'AAPL' in engine.data
        assert len(engine.data['AAPL']) == len(sample_data)
        assert engine.data['AAPL'].equals(sample_data)

    def test_set_strategy(self, engine):
        """Test setting a strategy."""
        strategy = MovingAverageCrossover(
            symbols=['AAPL'],
            fast_period=10,
            slow_period=30
        )

        engine.set_strategy(strategy)

        assert engine.strategy is strategy
        assert strategy.engine is engine

    def test_run_without_strategy(self, engine, sample_data):
        """Test that running without strategy raises error."""
        engine.add_data('AAPL', sample_data)

        with pytest.raises(ValueError, match="Strategy not set"):
            engine.run()

    def test_run_without_data(self, engine):
        """Test that running without data raises error."""
        strategy = MovingAverageCrossover(
            symbols=['AAPL'],
            fast_period=10,
            slow_period=30
        )
        engine.set_strategy(strategy)

        with pytest.raises(ValueError, match="No data loaded"):
            engine.run()

    def test_run_complete_backtest(self, engine, sample_data):
        """Test running a complete backtest."""
        engine.add_data('AAPL', sample_data)

        strategy = MovingAverageCrossover(
            symbols=['AAPL'],
            fast_period=10,
            slow_period=30,
            allocation=0.9
        )
        engine.set_strategy(strategy)

        equity_curve = engine.run()

        # Verify equity curve
        assert isinstance(equity_curve, pd.DataFrame)
        assert not equity_curve.empty
        assert 'total_value' in equity_curve.columns
        assert 'cash' in equity_curve.columns
        assert 'position_value' in equity_curve.columns

        # Portfolio value should be positive
        assert (equity_curve['total_value'] > 0).all()

    def test_multiple_symbols(self, engine):
        """Test backtest with multiple symbols."""
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')

        # Create data for two symbols
        for symbol in ['AAPL', 'MSFT']:
            prices = 100 + np.cumsum(np.random.randn(100) * 2)
            df = pd.DataFrame({
                'Open': prices * 0.99,
                'High': prices * 1.01,
                'Low': prices * 0.98,
                'Close': prices,
                'Volume': np.random.randint(1000000, 5000000, 100)
            }, index=dates)
            engine.add_data(symbol, df)

        strategy = MovingAverageCrossover(
            symbols=['AAPL', 'MSFT'],
            fast_period=10,
            slow_period=30,
            allocation=0.45  # 45% each
        )
        engine.set_strategy(strategy)

        equity_curve = engine.run()

        assert not equity_curve.empty
        assert (equity_curve['total_value'] > 0).all()

    def test_get_current_data(self, engine, sample_data):
        """Test getting current data during backtest."""
        engine.add_data('AAPL', sample_data)
        engine.current_date = sample_data.index[50]

        # Get all data up to current date
        current_data = engine.get_current_data('AAPL')

        assert len(current_data) == 51  # Indices 0-50
        assert current_data.index[-1] == sample_data.index[50]

    def test_get_current_data_with_lookback(self, engine, sample_data):
        """Test getting current data with lookback period."""
        engine.add_data('AAPL', sample_data)
        engine.current_date = sample_data.index[50]

        # Get last 20 periods
        current_data = engine.get_current_data('AAPL', lookback=20)

        assert len(current_data) == 20
        assert current_data.index[-1] == sample_data.index[50]

    def test_backtest_with_rsi_strategy(self, engine, sample_data):
        """Test backtest with RSI strategy."""
        engine.add_data('AAPL', sample_data)

        strategy = RSIMomentum(
            symbols=['AAPL'],
            period=14,
            oversold=30,
            overbought=70,
            allocation=1.0
        )
        engine.set_strategy(strategy)

        equity_curve = engine.run()

        # Should complete without errors
        assert not equity_curve.empty
        assert 'total_value' in equity_curve.columns

    def test_commission_impact(self):
        """Test that commission affects returns."""
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        prices = 100 + np.cumsum(np.random.randn(100) * 2)
        df = pd.DataFrame({
            'Open': prices * 0.99,
            'High': prices * 1.01,
            'Low': prices * 0.98,
            'Close': prices,
            'Volume': np.random.randint(1000000, 5000000, 100)
        }, index=dates)

        # Run with no commission
        engine_no_comm = BacktestEngine(initial_capital=100000, commission=0.0)
        engine_no_comm.add_data('AAPL', df)
        strategy1 = MovingAverageCrossover(symbols=['AAPL'], fast_period=10, slow_period=30)
        engine_no_comm.set_strategy(strategy1)
        equity_no_comm = engine_no_comm.run()

        # Run with commission
        engine_with_comm = BacktestEngine(initial_capital=100000, commission=0.01)
        engine_with_comm.add_data('AAPL', df)
        strategy2 = MovingAverageCrossover(symbols=['AAPL'], fast_period=10, slow_period=30)
        engine_with_comm.set_strategy(strategy2)
        equity_with_comm = engine_with_comm.run()

        # Final value with commission should be less (or equal if no trades)
        final_no_comm = equity_no_comm['total_value'].iloc[-1]
        final_with_comm = equity_with_comm['total_value'].iloc[-1]

        # If trades occurred, commission version should have lower final value
        if len(engine_no_comm.portfolio.trades) > 0:
            assert final_with_comm <= final_no_comm

    def test_equity_curve_length(self, engine, sample_data):
        """Test that equity curve has correct length."""
        engine.add_data('AAPL', sample_data)

        strategy = MovingAverageCrossover(
            symbols=['AAPL'],
            fast_period=10,
            slow_period=30
        )
        engine.set_strategy(strategy)

        equity_curve = engine.run()

        # Equity curve should have entries for dates processed
        assert len(equity_curve) > 0
        assert len(equity_curve) <= len(sample_data)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

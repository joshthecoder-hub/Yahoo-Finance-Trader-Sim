"""
Integration tests to verify the complete system works end-to-end.
"""
import pytest
from src.data.fetchTickerData import fetch_ticker_data
from src.engine.backtest import BacktestEngine
from src.strategies.moving_average import MovingAverageCrossover, ExponentialMovingAverageCrossover
from src.strategies.momentum import RSIMomentum, RateOfChangeMomentum
from src.analysis.metrics import PerformanceMetrics


class TestIntegration:
    """Integration tests for the complete backtesting system."""

    def test_sma_strategy_integration(self):
        """Test complete workflow with SMA strategy."""
        # 1. Fetch real data
        data = fetch_ticker_data(
            symbol="AAPL",
            start_date="2024-01-01",
            end_date="2024-02-01"
        )

        assert not data.empty

        # 2. Create backtest engine
        engine = BacktestEngine(initial_capital=100000, commission=0.001)
        engine.add_data("AAPL", data)

        # 3. Create and set strategy
        strategy = MovingAverageCrossover(
            symbols=["AAPL"],
            fast_period=10,
            slow_period=20,
            allocation=0.9
        )
        engine.set_strategy(strategy)

        # 4. Run backtest
        equity_curve = engine.run()

        # 5. Verify results
        assert not equity_curve.empty
        assert 'total_value' in equity_curve.columns
        assert (equity_curve['total_value'] > 0).all()

        # 6. Calculate metrics
        trades = engine.portfolio.get_trade_history()
        metrics = PerformanceMetrics.calculate_all_metrics(equity_curve, trades)

        # 7. Verify metrics
        assert 'total_return' in metrics
        assert 'sharpe_ratio' in metrics
        assert 'max_drawdown_pct' in metrics

    def test_ema_strategy_integration(self):
        """Test complete workflow with EMA strategy."""
        data = fetch_ticker_data(
            symbol="MSFT",
            start_date="2024-01-01",
            end_date="2024-02-01"
        )

        engine = BacktestEngine(initial_capital=100000, commission=0.001)
        engine.add_data("MSFT", data)

        strategy = ExponentialMovingAverageCrossover(
            symbols=["MSFT"],
            fast_period=12,
            slow_period=26,
            allocation=1.0
        )
        engine.set_strategy(strategy)

        equity_curve = engine.run()

        assert not equity_curve.empty
        assert equity_curve['total_value'].iloc[-1] > 0

    def test_rsi_strategy_integration(self):
        """Test complete workflow with RSI strategy."""
        data = fetch_ticker_data(
            symbol="AAPL",
            start_date="2024-01-01",
            end_date="2024-02-01"
        )

        engine = BacktestEngine(initial_capital=100000, commission=0.001)
        engine.add_data("AAPL", data)

        strategy = RSIMomentum(
            symbols=["AAPL"],
            period=14,
            oversold=30,
            overbought=70,
            allocation=1.0
        )
        engine.set_strategy(strategy)

        equity_curve = engine.run()

        assert not equity_curve.empty
        assert (equity_curve['total_value'] > 0).all()

    def test_multiple_strategies_comparison(self):
        """Test running multiple strategies on the same data."""
        # Fetch data once
        data = fetch_ticker_data(
            symbol="AAPL",
            start_date="2024-01-01",
            end_date="2024-02-01"
        )

        results = {}

        # Test SMA
        engine1 = BacktestEngine(initial_capital=100000, commission=0.001)
        engine1.add_data("AAPL", data)
        strategy1 = MovingAverageCrossover(
            symbols=["AAPL"],
            fast_period=10,
            slow_period=20
        )
        engine1.set_strategy(strategy1)
        equity1 = engine1.run()
        results['SMA'] = equity1['total_value'].iloc[-1]

        # Test EMA
        engine2 = BacktestEngine(initial_capital=100000, commission=0.001)
        engine2.add_data("AAPL", data)
        strategy2 = ExponentialMovingAverageCrossover(
            symbols=["AAPL"],
            fast_period=12,
            slow_period=26
        )
        engine2.set_strategy(strategy2)
        equity2 = engine2.run()
        results['EMA'] = equity2['total_value'].iloc[-1]

        # Both should have positive final values
        assert all(v > 0 for v in results.values())

    def test_no_mcp_dependency(self):
        """Verify system works without MCP fetcher."""
        # This test ensures we don't have any imports of mcp_fetcher
        # If the deleted mcp_fetcher.py was required, this would fail

        from src.data import fetchTickerData
        from src.engine import backtest
        from src.strategies import moving_average, momentum
        from src.portfolio import portfolio
        from src.analysis import metrics

        # All imports should succeed
        assert fetchTickerData is not None
        assert backtest is not None
        assert moving_average is not None
        assert momentum is not None
        assert portfolio is not None
        assert metrics is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

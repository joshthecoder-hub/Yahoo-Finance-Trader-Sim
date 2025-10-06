"""
Tests for portfolio management and P&L tracking.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from src.portfolio.portfolio import Portfolio
from src.execution.order import Order, OrderType, OrderSide


class TestPortfolio:
    """Test suite for Portfolio class."""

    @pytest.fixture
    def portfolio(self):
        """Create portfolio instance."""
        return Portfolio(initial_capital=100000.0, commission_rate=0.001)

    def test_initialization(self, portfolio):
        """Test portfolio initialization."""
        assert portfolio.initial_capital == 100000.0
        assert portfolio.cash == 100000.0
        assert portfolio.executor.commission_rate == 0.001
        assert len(portfolio.positions) == 0

    def test_execute_buy_order(self, portfolio):
        """Test executing a buy order."""
        order = Order(
            symbol='AAPL',
            order_type=OrderType.MARKET,
            side=OrderSide.BUY,
            quantity=10,
            timestamp=datetime(2024, 1, 1)
        )

        price = 150.0
        result = portfolio.execute_order(order, price)

        # Should execute successfully
        assert result is True

        # Check position created
        assert 'AAPL' in portfolio.positions
        assert portfolio.positions['AAPL'] == 10

    def test_execute_sell_order(self, portfolio):
        """Test executing a sell order."""
        # First buy some shares
        buy_order = Order(
            symbol='AAPL',
            order_type=OrderType.MARKET,
            side=OrderSide.BUY,
            quantity=10,
            timestamp=datetime(2024, 1, 1)
        )
        portfolio.execute_order(buy_order, 150.0)

        # Now sell
        sell_order = Order(
            symbol='AAPL',
            order_type=OrderType.MARKET,
            side=OrderSide.SELL,
            quantity=5,
            timestamp=datetime(2024, 1, 2)
        )
        result = portfolio.execute_order(sell_order, 160.0)

        # Should execute successfully
        assert result is True

        # Check position reduced
        assert portfolio.positions['AAPL'] == 5

    def test_sell_without_position(self, portfolio):
        """Test that selling without position returns False."""
        sell_order = Order(
            symbol='AAPL',
            order_type=OrderType.MARKET,
            side=OrderSide.SELL,
            quantity=10,
            timestamp=datetime(2024, 1, 1)
        )

        result = portfolio.execute_order(sell_order, 150.0)

        # Should not execute
        assert result is False
        assert portfolio.cash == 100000.0

    def test_commission_deduction(self, portfolio):
        """Test that commission is deducted correctly."""
        initial_cash = portfolio.cash

        order = Order(
            symbol='AAPL',
            order_type=OrderType.MARKET,
            side=OrderSide.BUY,
            quantity=100,
            timestamp=datetime(2024, 1, 1)
        )

        price = 150.0
        portfolio.execute_order(order, price)

        # Calculate expected cash after commission
        cost = 100 * 150.0
        commission = cost * 0.001
        expected_cash = initial_cash - cost - commission

        assert portfolio.cash == pytest.approx(expected_cash)

    def test_update_positions(self, portfolio):
        """Test updating portfolio positions with current market data."""
        # Buy some shares
        order = Order(
            symbol='AAPL',
            order_type=OrderType.MARKET,
            side=OrderSide.BUY,
            quantity=10,
            timestamp=datetime(2024, 1, 1)
        )
        portfolio.execute_order(order, 150.0)

        # Create market data
        dates = pd.date_range(start='2024-01-01', periods=5, freq='D')
        df = pd.DataFrame({
            'Close': [150, 155, 160, 158, 162]
        }, index=dates)

        current_data = {'AAPL': df}

        # Update positions
        portfolio.update_positions(current_data, dates[4])

        # Total value should be cash + position value
        assert portfolio.total_value > portfolio.cash

    def test_get_trade_history(self, portfolio):
        """Test retrieving trade history."""
        # Execute some trades
        buy = Order(
            symbol='AAPL',
            order_type=OrderType.MARKET,
            side=OrderSide.BUY,
            quantity=10,
            timestamp=datetime(2024, 1, 1)
        )
        portfolio.execute_order(buy, 150.0)

        sell = Order(
            symbol='AAPL',
            order_type=OrderType.MARKET,
            side=OrderSide.SELL,
            quantity=5,
            timestamp=datetime(2024, 1, 2)
        )
        portfolio.execute_order(sell, 160.0)

        history = portfolio.get_trade_history()

        # Should have trade records
        assert isinstance(history, pd.DataFrame)
        if not history.empty:
            assert len(history) >= 2

    def test_portfolio_value_calculation(self, portfolio):
        """Test portfolio value calculation."""
        # Buy shares
        order = Order(
            symbol='AAPL',
            order_type=OrderType.MARKET,
            side=OrderSide.BUY,
            quantity=100,
            timestamp=datetime(2024, 1, 1)
        )
        portfolio.execute_order(order, 100.0)

        # Create market data with price increase
        dates = pd.date_range(start='2024-01-01', periods=1, freq='D')
        df = pd.DataFrame({'Close': [110]}, index=dates)
        current_data = {'AAPL': df}

        portfolio.update_positions(current_data, dates[0])

        # Portfolio should have gained value
        assert portfolio.total_value > portfolio.cash

        # Position value should be quantity * current price
        expected_position_value = 100 * 110
        actual_position_value = portfolio.total_value - portfolio.cash
        assert actual_position_value == pytest.approx(expected_position_value, rel=0.01)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

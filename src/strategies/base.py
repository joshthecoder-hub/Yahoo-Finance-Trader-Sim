"""Base strategy interface for implementing trading strategies."""
from abc import ABC, abstractmethod
from typing import Dict, List
import pandas as pd
from datetime import datetime


class Strategy(ABC):
    """Abstract base class for trading strategies."""

    def __init__(self, name: str):
        """
        Initialize the strategy.

        Args:
            name: Strategy name
        """
        self.name = name
        self.engine = None

    def set_engine(self, engine):
        """
        Set the backtesting engine reference.

        Args:
            engine: BacktestEngine instance
        """
        self.engine = engine

    @abstractmethod
    def generate_signals(
        self,
        data: Dict[str, pd.DataFrame],
        current_date: datetime
    ) -> List[Dict]:
        """
        Generate trading signals based on current market data.

        Args:
            data: Dictionary mapping symbols to their historical data
            current_date: Current timestamp in the backtest

        Returns:
            List of signal dictionaries with keys:
                - symbol: str
                - side: OrderSide (BUY or SELL)
                - quantity: int
                - order_type: OrderType (optional, defaults to MARKET)
        """
        pass

    def calculate_position_size(
        self,
        symbol: str,
        price: float,
        portfolio_value: float,
        allocation: float = 0.1
    ) -> int:
        """
        Calculate position size based on allocation percentage.

        Args:
            symbol: Stock ticker
            price: Current price
            portfolio_value: Total portfolio value
            allocation: Percentage of portfolio to allocate (0.0-1.0)

        Returns:
            Number of shares to trade
        """
        if price <= 0:
            return 0

        dollar_amount = portfolio_value * allocation
        shares = int(dollar_amount / price)

        return shares

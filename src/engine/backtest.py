"""Core backtesting engine with event-driven architecture."""
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime
from ..portfolio.portfolio import Portfolio
from ..execution.order import Order, OrderType, OrderSide
from ..strategies.base import Strategy


class BacktestEngine:
    """Event-driven backtesting engine for systematic trading strategies."""

    def __init__(
        self,
        initial_capital: float = 100000.0,
        commission: float = 0.001  # 0.1% per trade
    ):
        """
        Initialize the backtesting engine.

        Args:
            initial_capital: Starting capital for the portfolio
            commission: Commission rate per trade (must be >= 0)
        """
        if commission < 0:
            raise ValueError(f"Commission rate must be >= 0, got {commission}")
        if initial_capital <= 0:
            raise ValueError(f"Initial capital must be > 0, got {initial_capital}")

        self.initial_capital = initial_capital
        self.commission = commission
        self.portfolio = Portfolio(initial_capital, commission)
        self.strategy: Optional[Strategy] = None
        self.data: Dict[str, pd.DataFrame] = {}
        self.current_date: Optional[datetime] = None

    def add_data(self, symbol: str, data: pd.DataFrame):
        """
        Add market data for a symbol.

        Args:
            symbol: Stock ticker symbol
            data: DataFrame with OHLCV data
        """
        self.data[symbol] = data.copy()

    def set_strategy(self, strategy: Strategy):
        """
        Set the trading strategy.

        Args:
            strategy: Strategy instance to use for trading
        """
        self.strategy = strategy
        strategy.set_engine(self)

    def run(self) -> pd.DataFrame:
        """
        Run the backtest across all data.

        Returns:
            DataFrame with portfolio performance metrics over time
        """
        if self.strategy is None:
            raise ValueError("Strategy not set. Call set_strategy() first.")

        if not self.data:
            raise ValueError("No data loaded. Call add_data() first.")

        # Get all unique dates across all symbols
        all_dates = sorted(set().union(*[set(df.index) for df in self.data.values()]))

        # Event loop: iterate through each timestamp
        for current_date in all_dates:
            self.current_date = current_date

            # Get current market data for all symbols
            current_data = {}
            for symbol, df in self.data.items():
                if current_date in df.index:
                    current_data[symbol] = df.loc[:current_date]

            # Generate signals from strategy
            signals = self.strategy.generate_signals(current_data, current_date)

            # Execute orders based on signals
            for signal in signals:
                self._execute_signal(signal, current_data)

            # Update portfolio value at end of day
            self.portfolio.update_positions(current_data, current_date)

        return self.portfolio.get_performance_history()

    def _execute_signal(self, signal: Dict, current_data: Dict[str, pd.DataFrame]):
        """
        Execute a trading signal.

        Args:
            signal: Dictionary with 'symbol', 'side', 'quantity', 'order_type'
            current_data: Current market data
        """
        symbol = signal['symbol']

        if symbol not in current_data or self.current_date not in current_data[symbol].index:
            return

        current_price = current_data[symbol].loc[self.current_date, 'Close']

        order = Order(
            symbol=symbol,
            order_type=signal.get('order_type', OrderType.MARKET),
            side=signal['side'],
            quantity=signal['quantity'],
            timestamp=self.current_date
        )

        self.portfolio.execute_order(order, current_price)

    def get_current_data(self, symbol: str, lookback: Optional[int] = None) -> pd.DataFrame:
        """
        Get historical data up to current date.

        Args:
            symbol: Stock ticker symbol
            lookback: Number of periods to look back (None = all)

        Returns:
            DataFrame with historical data up to current date
        """
        if symbol not in self.data or self.current_date is None:
            return pd.DataFrame()

        data = self.data[symbol].loc[:self.current_date]

        if lookback is not None:
            data = data.tail(lookback)

        return data

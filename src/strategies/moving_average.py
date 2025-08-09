"""Moving average crossover strategy implementation."""
from typing import Dict, List
import pandas as pd
from datetime import datetime
from .base import Strategy
from ..execution.order import OrderSide


class MovingAverageCrossover(Strategy):
    """
    Simple moving average crossover strategy.

    Generates buy signals when fast MA crosses above slow MA.
    Generates sell signals when fast MA crosses below slow MA.
    """

    def __init__(
        self,
        symbols: List[str],
        fast_period: int = 50,
        slow_period: int = 200,
        allocation: float = 0.1
    ):
        """
        Initialize the moving average crossover strategy.

        Args:
            symbols: List of symbols to trade
            fast_period: Fast moving average period
            slow_period: Slow moving average period
            allocation: Portfolio allocation per position (0.0-1.0)
        """
        super().__init__("Moving Average Crossover")
        self.symbols = symbols
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.allocation = allocation
        self.positions: Dict[str, bool] = {symbol: False for symbol in symbols}

    def generate_signals(
        self,
        data: Dict[str, pd.DataFrame],
        current_date: datetime
    ) -> List[Dict]:
        """
        Generate trading signals based on moving average crossovers.

        Args:
            data: Dictionary mapping symbols to their historical data
            current_date: Current timestamp in the backtest

        Returns:
            List of trading signals
        """
        signals = []

        for symbol in self.symbols:
            if symbol not in data or len(data[symbol]) < self.slow_period:
                continue

            df = data[symbol]

            # Calculate moving averages
            df['SMA_Fast'] = df['Close'].rolling(window=self.fast_period).mean()
            df['SMA_Slow'] = df['Close'].rolling(window=self.slow_period).mean()

            # Get current and previous values
            if len(df) < 2:
                continue

            current_fast = df['SMA_Fast'].iloc[-1]
            current_slow = df['SMA_Slow'].iloc[-1]
            prev_fast = df['SMA_Fast'].iloc[-2]
            prev_slow = df['SMA_Slow'].iloc[-2]

            # Check for NaN values
            if pd.isna(current_fast) or pd.isna(current_slow):
                continue
            if pd.isna(prev_fast) or pd.isna(prev_slow):
                continue

            current_price = df['Close'].iloc[-1]
            portfolio_value = self.engine.portfolio.total_value

            # Bullish crossover: fast MA crosses above slow MA
            if prev_fast <= prev_slow and current_fast > current_slow:
                if not self.positions[symbol]:
                    quantity = self.calculate_position_size(
                        symbol, current_price, portfolio_value, self.allocation
                    )
                    if quantity > 0:
                        signals.append({
                            'symbol': symbol,
                            'side': OrderSide.BUY,
                            'quantity': quantity
                        })
                        self.positions[symbol] = True

            # Bearish crossover: fast MA crosses below slow MA
            elif prev_fast >= prev_slow and current_fast < current_slow:
                if self.positions[symbol]:
                    # Get current position size
                    current_position = self.engine.portfolio.positions.get(symbol, 0)
                    if current_position > 0:
                        signals.append({
                            'symbol': symbol,
                            'side': OrderSide.SELL,
                            'quantity': current_position
                        })
                        self.positions[symbol] = False

        return signals


class ExponentialMovingAverageCrossover(Strategy):
    """
    Exponential moving average crossover strategy.

    Uses EMA instead of SMA for faster response to price changes.
    """

    def __init__(
        self,
        symbols: List[str],
        fast_period: int = 12,
        slow_period: int = 26,
        allocation: float = 0.1
    ):
        """
        Initialize the EMA crossover strategy.

        Args:
            symbols: List of symbols to trade
            fast_period: Fast EMA period
            slow_period: Slow EMA period
            allocation: Portfolio allocation per position (0.0-1.0)
        """
        super().__init__("EMA Crossover")
        self.symbols = symbols
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.allocation = allocation
        self.positions: Dict[str, bool] = {symbol: False for symbol in symbols}

    def generate_signals(
        self,
        data: Dict[str, pd.DataFrame],
        current_date: datetime
    ) -> List[Dict]:
        """Generate trading signals based on EMA crossovers."""
        signals = []

        for symbol in self.symbols:
            if symbol not in data or len(data[symbol]) < self.slow_period:
                continue

            df = data[symbol]

            # Calculate exponential moving averages
            df['EMA_Fast'] = df['Close'].ewm(span=self.fast_period, adjust=False).mean()
            df['EMA_Slow'] = df['Close'].ewm(span=self.slow_period, adjust=False).mean()

            if len(df) < 2:
                continue

            current_fast = df['EMA_Fast'].iloc[-1]
            current_slow = df['EMA_Slow'].iloc[-1]
            prev_fast = df['EMA_Fast'].iloc[-2]
            prev_slow = df['EMA_Slow'].iloc[-2]

            if pd.isna(current_fast) or pd.isna(current_slow):
                continue
            if pd.isna(prev_fast) or pd.isna(prev_slow):
                continue

            current_price = df['Close'].iloc[-1]
            portfolio_value = self.engine.portfolio.total_value

            # Bullish crossover
            if prev_fast <= prev_slow and current_fast > current_slow:
                if not self.positions[symbol]:
                    quantity = self.calculate_position_size(
                        symbol, current_price, portfolio_value, self.allocation
                    )
                    if quantity > 0:
                        signals.append({
                            'symbol': symbol,
                            'side': OrderSide.BUY,
                            'quantity': quantity
                        })
                        self.positions[symbol] = True

            # Bearish crossover
            elif prev_fast >= prev_slow and current_fast < current_slow:
                if self.positions[symbol]:
                    current_position = self.engine.portfolio.positions.get(symbol, 0)
                    if current_position > 0:
                        signals.append({
                            'symbol': symbol,
                            'side': OrderSide.SELL,
                            'quantity': current_position
                        })
                        self.positions[symbol] = False

        return signals

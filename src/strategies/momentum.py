"""Momentum-based trading strategies."""
from typing import Dict, List
import pandas as pd
import numpy as np
from datetime import datetime
from .base import Strategy
from ..execution.order import OrderSide


class RSIMomentum(Strategy):
    """
    RSI (Relative Strength Index) momentum strategy.

    Buys when RSI crosses above oversold threshold.
    Sells when RSI crosses below overbought threshold.
    """

    def __init__(
        self,
        symbols: List[str],
        period: int = 14,
        oversold: float = 30,
        overbought: float = 70,
        allocation: float = 0.1
    ):
        """
        Initialize RSI momentum strategy.

        Args:
            symbols: List of symbols to trade
            period: RSI calculation period
            oversold: Oversold threshold (buy signal, 0-100)
            overbought: Overbought threshold (sell signal, 0-100)
            allocation: Portfolio allocation per position
        """
        # Validate RSI thresholds
        if not (0 <= oversold <= 100):
            raise ValueError(f"Oversold threshold must be between 0 and 100, got {oversold}")
        if not (0 <= overbought <= 100):
            raise ValueError(f"Overbought threshold must be between 0 and 100, got {overbought}")
        if oversold >= overbought:
            raise ValueError(f"Oversold ({oversold}) must be less than overbought ({overbought})")
        if period < 1:
            raise ValueError(f"Period must be >= 1, got {period}")

        super().__init__("RSI Momentum")
        self.symbols = symbols
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
        self.allocation = allocation
        self.positions: Dict[str, bool] = {symbol: False for symbol in symbols}

    def _calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate RSI indicator."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        # Prevent division by zero by adding small epsilon
        rs = gain / (loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def generate_signals(
        self,
        data: Dict[str, pd.DataFrame],
        current_date: datetime
    ) -> List[Dict]:
        """Generate trading signals based on RSI."""
        signals = []

        for symbol in self.symbols:
            if symbol not in data or len(data[symbol]) < self.period + 1:
                continue

            df = data[symbol].copy()

            # Calculate RSI
            df['RSI'] = self._calculate_rsi(df['Close'], self.period)

            if len(df) < 2:
                continue

            current_rsi = df['RSI'].iloc[-1]
            prev_rsi = df['RSI'].iloc[-2]

            if pd.isna(current_rsi) or pd.isna(prev_rsi):
                continue

            current_price = df['Close'].iloc[-1]
            portfolio_value = self.engine.portfolio.total_value

            # Buy signal: RSI crosses above oversold
            if prev_rsi <= self.oversold and current_rsi > self.oversold:
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

            # Sell signal: RSI crosses below overbought
            elif prev_rsi >= self.overbought and current_rsi < self.overbought:
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


class RateOfChangeMomentum(Strategy):
    """
    Rate of Change (ROC) momentum strategy.

    Buys when ROC crosses above threshold (positive momentum).
    Sells when ROC crosses below negative threshold.
    """

    def __init__(
        self,
        symbols: List[str],
        period: int = 20,
        buy_threshold: float = 5.0,
        sell_threshold: float = -5.0,
        allocation: float = 0.1
    ):
        """
        Initialize ROC momentum strategy.

        Args:
            symbols: List of symbols to trade
            period: ROC calculation period
            buy_threshold: Positive threshold for buy signals (%)
            sell_threshold: Negative threshold for sell signals (%)
            allocation: Portfolio allocation per position
        """
        super().__init__("Rate of Change Momentum")
        self.symbols = symbols
        self.period = period
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.allocation = allocation
        self.positions: Dict[str, bool] = {symbol: False for symbol in symbols}

    def _calculate_roc(self, prices: pd.Series, period: int) -> pd.Series:
        """
        Calculate Rate of Change indicator.

        ROC = ((Current Price - Price N periods ago) / Price N periods ago) * 100
        """
        roc = ((prices - prices.shift(period)) / prices.shift(period)) * 100
        return roc

    def generate_signals(
        self,
        data: Dict[str, pd.DataFrame],
        current_date: datetime
    ) -> List[Dict]:
        """Generate trading signals based on ROC."""
        signals = []

        for symbol in self.symbols:
            if symbol not in data or len(data[symbol]) < self.period + 1:
                continue

            df = data[symbol].copy()

            # Calculate ROC
            df['ROC'] = self._calculate_roc(df['Close'], self.period)

            if len(df) < 2:
                continue

            current_roc = df['ROC'].iloc[-1]
            prev_roc = df['ROC'].iloc[-2]

            if pd.isna(current_roc) or pd.isna(prev_roc):
                continue

            current_price = df['Close'].iloc[-1]
            portfolio_value = self.engine.portfolio.total_value

            # Buy signal: ROC crosses above buy threshold
            if prev_roc <= self.buy_threshold and current_roc > self.buy_threshold:
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

            # Sell signal: ROC crosses below sell threshold
            elif prev_roc >= self.sell_threshold and current_roc < self.sell_threshold:
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

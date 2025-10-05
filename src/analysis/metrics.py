"""Performance metrics and analytics for backtesting results."""
import pandas as pd
import numpy as np
from typing import Dict, Optional


class PerformanceMetrics:
    """Calculate performance metrics for backtesting results."""

    @staticmethod
    def calculate_returns(equity_curve: pd.DataFrame) -> pd.Series:
        """
        Calculate returns from equity curve.

        Args:
            equity_curve: DataFrame with 'total_value' column

        Returns:
            Series of returns
        """
        return equity_curve['total_value'].pct_change()

    @staticmethod
    def total_return(equity_curve: pd.DataFrame) -> float:
        """
        Calculate total return.

        Args:
            equity_curve: DataFrame with 'total_value' column

        Returns:
            Total return as decimal (e.g., 0.15 = 15%)
        """
        if len(equity_curve) == 0:
            return 0.0

        initial_value = equity_curve['total_value'].iloc[0]
        final_value = equity_curve['total_value'].iloc[-1]

        return (final_value - initial_value) / initial_value

    @staticmethod
    def annualized_return(equity_curve: pd.DataFrame, periods_per_year: int = 252) -> float:
        """
        Calculate annualized return.

        Args:
            equity_curve: DataFrame with 'total_value' column
            periods_per_year: Trading periods per year (252 for daily)

        Returns:
            Annualized return
        """
        if len(equity_curve) == 0:
            return 0.0

        total_ret = PerformanceMetrics.total_return(equity_curve)
        num_periods = len(equity_curve)

        if num_periods == 0:
            return 0.0

        years = num_periods / periods_per_year
        return (1 + total_ret) ** (1 / years) - 1

    @staticmethod
    def sharpe_ratio(
        equity_curve: pd.DataFrame,
        risk_free_rate: float = 0.02,
        periods_per_year: int = 252
    ) -> float:
        """
        Calculate Sharpe ratio.

        Args:
            equity_curve: DataFrame with 'total_value' column
            risk_free_rate: Annual risk-free rate
            periods_per_year: Trading periods per year

        Returns:
            Sharpe ratio
        """
        returns = PerformanceMetrics.calculate_returns(equity_curve)

        if len(returns) < 2:
            return 0.0

        excess_returns = returns - (risk_free_rate / periods_per_year)
        std_dev = excess_returns.std()

        # Use threshold to handle floating-point precision issues
        if np.isclose(std_dev, 0.0, atol=1e-10) or std_dev < 1e-10:
            return 0.0

        return np.sqrt(periods_per_year) * (excess_returns.mean() / std_dev)

    @staticmethod
    def max_drawdown(equity_curve: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate maximum drawdown.

        Args:
            equity_curve: DataFrame with 'total_value' column

        Returns:
            Dictionary with max_drawdown, max_drawdown_pct, and duration
        """
        if len(equity_curve) == 0:
            return {'max_drawdown': 0.0, 'max_drawdown_pct': 0.0, 'duration': 0}

        values = equity_curve['total_value']
        cummax = values.cummax()
        drawdown = values - cummax
        drawdown_pct = drawdown / cummax

        max_dd = drawdown.min()
        max_dd_pct = drawdown_pct.min()

        # Calculate drawdown duration
        is_drawdown = drawdown < 0
        drawdown_periods = is_drawdown.astype(int)

        # Find longest consecutive drawdown
        max_duration = 0
        current_duration = 0

        for is_dd in drawdown_periods:
            if is_dd:
                current_duration += 1
                max_duration = max(max_duration, current_duration)
            else:
                current_duration = 0

        return {
            'max_drawdown': abs(max_dd),
            'max_drawdown_pct': abs(max_dd_pct),
            'duration': max_duration
        }

    @staticmethod
    def volatility(
        equity_curve: pd.DataFrame,
        periods_per_year: int = 252
    ) -> float:
        """
        Calculate annualized volatility.

        Args:
            equity_curve: DataFrame with 'total_value' column
            periods_per_year: Trading periods per year

        Returns:
            Annualized volatility
        """
        returns = PerformanceMetrics.calculate_returns(equity_curve)

        if len(returns) < 2:
            return 0.0

        return returns.std() * np.sqrt(periods_per_year)

    @staticmethod
    def win_rate(trades: pd.DataFrame) -> float:
        """
        Calculate win rate from trades by matching buy/sell pairs.

        Args:
            trades: DataFrame with trade history (must have 'side', 'symbol', 'price', 'quantity')

        Returns:
            Win rate (0.0-1.0) - percentage of profitable round-trip trades
        """
        if len(trades) == 0:
            return 0.0

        # Match buy/sell pairs to calculate P&L per round-trip trade
        symbols = trades['symbol'].unique()
        winning_trades = 0
        total_roundtrips = 0

        for symbol in symbols:
            symbol_trades = trades[trades['symbol'] == symbol].copy()
            symbol_trades = symbol_trades.sort_index()  # Sort by timestamp

            # Stack to track open positions (FIFO matching)
            buy_stack = []

            for idx, trade in symbol_trades.iterrows():
                if trade['side'] == 'buy':
                    # Add buy to stack
                    buy_stack.append({
                        'price': trade['price'],
                        'quantity': trade['quantity']
                    })
                elif trade['side'] == 'sell':
                    # Match sell with buys from stack
                    remaining_sell_qty = trade['quantity']
                    sell_price = trade['price']

                    while remaining_sell_qty > 0 and len(buy_stack) > 0:
                        buy = buy_stack[0]
                        matched_qty = min(buy['quantity'], remaining_sell_qty)

                        # Calculate P&L for this matched trade
                        pnl = (sell_price - buy['price']) * matched_qty

                        if pnl > 0:
                            winning_trades += 1
                        total_roundtrips += 1

                        # Update quantities
                        buy['quantity'] -= matched_qty
                        remaining_sell_qty -= matched_qty

                        if buy['quantity'] == 0:
                            buy_stack.pop(0)

        if total_roundtrips == 0:
            return 0.0

        return winning_trades / total_roundtrips

    @staticmethod
    def profit_factor(trades: pd.DataFrame) -> float:
        """
        Calculate profit factor (gross profit / gross loss) from matched buy/sell pairs.

        Args:
            trades: DataFrame with trade history (must have 'side', 'symbol', 'price', 'quantity')

        Returns:
            Profit factor - ratio of gross profits to gross losses
        """
        if len(trades) == 0:
            return 0.0

        # Match buy/sell pairs to calculate P&L
        symbols = trades['symbol'].unique()
        gross_profit = 0.0
        gross_loss = 0.0

        for symbol in symbols:
            symbol_trades = trades[trades['symbol'] == symbol].copy()
            symbol_trades = symbol_trades.sort_index()  # Sort by timestamp

            # Stack to track open positions (FIFO matching)
            buy_stack = []

            for idx, trade in symbol_trades.iterrows():
                if trade['side'] == 'buy':
                    # Add buy to stack
                    buy_stack.append({
                        'price': trade['price'],
                        'quantity': trade['quantity']
                    })
                elif trade['side'] == 'sell':
                    # Match sell with buys from stack
                    remaining_sell_qty = trade['quantity']
                    sell_price = trade['price']

                    while remaining_sell_qty > 0 and len(buy_stack) > 0:
                        buy = buy_stack[0]
                        matched_qty = min(buy['quantity'], remaining_sell_qty)

                        # Calculate P&L for this matched trade
                        pnl = (sell_price - buy['price']) * matched_qty

                        if pnl > 0:
                            gross_profit += pnl
                        else:
                            gross_loss += abs(pnl)

                        # Update quantities
                        buy['quantity'] -= matched_qty
                        remaining_sell_qty -= matched_qty

                        if buy['quantity'] == 0:
                            buy_stack.pop(0)

        if gross_loss == 0:
            # All trades profitable or no trades
            return gross_profit if gross_profit > 0 else 0.0

        return gross_profit / gross_loss

    @staticmethod
    def calculate_all_metrics(
        equity_curve: pd.DataFrame,
        trades: pd.DataFrame,
        risk_free_rate: float = 0.02,
        periods_per_year: int = 252
    ) -> Dict[str, float]:
        """
        Calculate all performance metrics.

        Args:
            equity_curve: Portfolio equity curve
            trades: Trade history
            risk_free_rate: Annual risk-free rate
            periods_per_year: Trading periods per year

        Returns:
            Dictionary of all metrics
        """
        metrics = {}

        # Return metrics
        metrics['total_return'] = PerformanceMetrics.total_return(equity_curve)
        metrics['annualized_return'] = PerformanceMetrics.annualized_return(
            equity_curve, periods_per_year
        )

        # Risk metrics
        metrics['volatility'] = PerformanceMetrics.volatility(equity_curve, periods_per_year)
        metrics['sharpe_ratio'] = PerformanceMetrics.sharpe_ratio(
            equity_curve, risk_free_rate, periods_per_year
        )

        # Drawdown metrics
        dd_metrics = PerformanceMetrics.max_drawdown(equity_curve)
        metrics.update(dd_metrics)

        # Trade metrics
        metrics['total_trades'] = len(trades)
        metrics['win_rate'] = PerformanceMetrics.win_rate(trades)
        metrics['profit_factor'] = PerformanceMetrics.profit_factor(trades)

        # Final values
        if len(equity_curve) > 0:
            metrics['initial_capital'] = equity_curve['total_value'].iloc[0]
            metrics['final_value'] = equity_curve['total_value'].iloc[-1]
            metrics['final_cash'] = equity_curve['cash'].iloc[-1]

        return metrics

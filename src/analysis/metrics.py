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

        if excess_returns.std() == 0:
            return 0.0

        return np.sqrt(periods_per_year) * (excess_returns.mean() / excess_returns.std())

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
        Calculate win rate from trades.

        Args:
            trades: DataFrame with trade history

        Returns:
            Win rate (0.0-1.0)
        """
        if len(trades) == 0:
            return 0.0

        # Group by symbol to calculate P&L per trade
        # This is simplified - assumes alternating buys/sells
        sell_trades = trades[trades['side'] == 'sell']

        if len(sell_trades) == 0:
            return 0.0

        # This is a simplification - proper implementation would match buys to sells
        wins = len(sell_trades[sell_trades['price'] > 0])  # Placeholder logic

        return wins / len(sell_trades)

    @staticmethod
    def profit_factor(trades: pd.DataFrame) -> float:
        """
        Calculate profit factor (gross profit / gross loss).

        Args:
            trades: DataFrame with trade history

        Returns:
            Profit factor
        """
        if len(trades) == 0:
            return 0.0

        # Simplified - would need matched buy/sell pairs
        sell_trades = trades[trades['side'] == 'sell']

        if len(sell_trades) == 0:
            return 0.0

        # Placeholder - would calculate actual profits/losses
        return 1.0

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

"""Visualization tools for backtesting results."""
import pandas as pd
import matplotlib.pyplot as plt
from typing import Optional, Tuple
import numpy as np


class BacktestVisualizer:
    """Create visualizations for backtest results."""

    @staticmethod
    def plot_equity_curve(
        equity_curve: pd.DataFrame,
        title: str = "Portfolio Equity Curve",
        figsize: Tuple[int, int] = (12, 6)
    ):
        """
        Plot the equity curve.

        Args:
            equity_curve: DataFrame with 'total_value' column
            title: Plot title
            figsize: Figure size
        """
        fig, ax = plt.subplots(figsize=figsize)

        ax.plot(equity_curve.index, equity_curve['total_value'], label='Portfolio Value', linewidth=2)
        ax.axhline(y=equity_curve['total_value'].iloc[0], color='r', linestyle='--',
                   label='Initial Capital', alpha=0.7)

        ax.set_xlabel('Date')
        ax.set_ylabel('Portfolio Value ($)')
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    @staticmethod
    def plot_drawdown(
        equity_curve: pd.DataFrame,
        title: str = "Drawdown",
        figsize: Tuple[int, int] = (12, 4)
    ):
        """
        Plot drawdown over time.

        Args:
            equity_curve: DataFrame with 'total_value' column
            title: Plot title
            figsize: Figure size
        """
        values = equity_curve['total_value']
        cummax = values.cummax()
        drawdown = (values - cummax) / cummax * 100  # As percentage

        fig, ax = plt.subplots(figsize=figsize)

        ax.fill_between(drawdown.index, drawdown, 0, alpha=0.3, color='red')
        ax.plot(drawdown.index, drawdown, color='red', linewidth=1)

        ax.set_xlabel('Date')
        ax.set_ylabel('Drawdown (%)')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    @staticmethod
    def plot_returns_distribution(
        equity_curve: pd.DataFrame,
        title: str = "Returns Distribution",
        figsize: Tuple[int, int] = (10, 6),
        bins: int = 50
    ):
        """
        Plot distribution of returns.

        Args:
            equity_curve: DataFrame with 'total_value' column
            title: Plot title
            figsize: Figure size
            bins: Number of histogram bins
        """
        returns = equity_curve['total_value'].pct_change().dropna() * 100  # As percentage

        fig, ax = plt.subplots(figsize=figsize)

        ax.hist(returns, bins=bins, alpha=0.7, edgecolor='black')
        ax.axvline(x=returns.mean(), color='r', linestyle='--',
                   label=f'Mean: {returns.mean():.2f}%', linewidth=2)
        ax.axvline(x=returns.median(), color='g', linestyle='--',
                   label=f'Median: {returns.median():.2f}%', linewidth=2)

        ax.set_xlabel('Return (%)')
        ax.set_ylabel('Frequency')
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    @staticmethod
    def plot_position_composition(
        equity_curve: pd.DataFrame,
        title: str = "Portfolio Composition",
        figsize: Tuple[int, int] = (12, 6)
    ):
        """
        Plot cash vs position value over time.

        Args:
            equity_curve: DataFrame with 'cash' and 'position_value' columns
            title: Plot title
            figsize: Figure size
        """
        fig, ax = plt.subplots(figsize=figsize)

        ax.fill_between(equity_curve.index, 0, equity_curve['cash'],
                        alpha=0.5, label='Cash', color='green')
        ax.fill_between(equity_curve.index, equity_curve['cash'],
                        equity_curve['total_value'],
                        alpha=0.5, label='Positions', color='blue')

        ax.set_xlabel('Date')
        ax.set_ylabel('Value ($)')
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    @staticmethod
    def plot_monthly_returns(
        equity_curve: pd.DataFrame,
        title: str = "Monthly Returns",
        figsize: Tuple[int, int] = (12, 6)
    ):
        """
        Plot monthly returns as a bar chart.

        Args:
            equity_curve: DataFrame with 'total_value' column
            title: Plot title
            figsize: Figure size
        """
        # Resample to monthly and calculate returns
        monthly_values = equity_curve['total_value'].resample('M').last()
        monthly_returns = monthly_values.pct_change().dropna() * 100  # As percentage

        fig, ax = plt.subplots(figsize=figsize)

        colors = ['g' if x > 0 else 'r' for x in monthly_returns]
        ax.bar(monthly_returns.index, monthly_returns, color=colors, alpha=0.7, edgecolor='black')

        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax.set_xlabel('Month')
        ax.set_ylabel('Return (%)')
        ax.set_title(title)
        ax.grid(True, alpha=0.3, axis='y')

        plt.xticks(rotation=45)
        plt.tight_layout()
        return fig

    @staticmethod
    def create_summary_dashboard(
        equity_curve: pd.DataFrame,
        metrics: dict,
        figsize: Tuple[int, int] = (16, 10)
    ):
        """
        Create a comprehensive dashboard with multiple plots.

        Args:
            equity_curve: Portfolio equity curve
            metrics: Performance metrics dictionary
            figsize: Figure size
        """
        fig = plt.figure(figsize=figsize)
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

        # Equity curve
        ax1 = fig.add_subplot(gs[0, :])
        ax1.plot(equity_curve.index, equity_curve['total_value'], linewidth=2)
        ax1.set_title('Portfolio Equity Curve', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Value ($)')
        ax1.grid(True, alpha=0.3)

        # Drawdown
        ax2 = fig.add_subplot(gs[1, :])
        values = equity_curve['total_value']
        cummax = values.cummax()
        drawdown = (values - cummax) / cummax * 100
        ax2.fill_between(drawdown.index, drawdown, 0, alpha=0.3, color='red')
        ax2.set_title('Drawdown', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Drawdown (%)')
        ax2.grid(True, alpha=0.3)

        # Returns distribution
        ax3 = fig.add_subplot(gs[2, 0])
        returns = equity_curve['total_value'].pct_change().dropna() * 100
        ax3.hist(returns, bins=30, alpha=0.7, edgecolor='black')
        ax3.set_title('Returns Distribution', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Return (%)')
        ax3.set_ylabel('Frequency')
        ax3.grid(True, alpha=0.3)

        # Metrics table
        ax4 = fig.add_subplot(gs[2, 1])
        ax4.axis('off')

        metrics_text = f"""
        Performance Metrics
        {'='*30}
        Total Return: {metrics.get('total_return', 0)*100:.2f}%
        Annual Return: {metrics.get('annualized_return', 0)*100:.2f}%
        Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}
        Volatility: {metrics.get('volatility', 0)*100:.2f}%
        Max Drawdown: {metrics.get('max_drawdown_pct', 0)*100:.2f}%
        Total Trades: {metrics.get('total_trades', 0)}
        Win Rate: {metrics.get('win_rate', 0)*100:.2f}%
        """

        ax4.text(0.1, 0.5, metrics_text, fontsize=10, family='monospace',
                verticalalignment='center')

        return fig

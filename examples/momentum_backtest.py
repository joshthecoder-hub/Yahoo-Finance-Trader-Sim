"""
Example backtest using RSI momentum strategy.

This demonstrates:
- Fetching real market data from Yahoo Finance
- Using the RSI momentum strategy
- Comparing multiple strategies
- More detailed analysis
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine.backtest import BacktestEngine
from src.strategies.momentum import RSIMomentum, RateOfChangeMomentum
from src.analysis.metrics import PerformanceMetrics
from src.analysis.visualize import BacktestVisualizer
from src.data.fetchTickerData import fetch_ticker_data


def run_rsi_backtest():
    """Run backtest with RSI momentum strategy."""
    print("\n" + "=" * 60)
    print("RSI Momentum Strategy Backtest")
    print("=" * 60)

    # Fetch real data from Yahoo Finance
    symbol = "AAPL"  # Apple stock - good for RSI due to volatility
    start_date = "2020-01-01"
    end_date = "2023-12-31"

    print(f"\nFetching market data from Yahoo Finance for {symbol}...")
    try:
        data = fetch_ticker_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            interval="1d"
        )
    except ValueError as e:
        print(f"Error: {e}")
        return None, None, None, None, None, None

    # Validate sufficient data for RSI strategy
    rsi_period = 14
    days_fetched = len(data)
    min_required = rsi_period + 30  # RSI period + buffer for signal generation

    if days_fetched < min_required:
        print(f"   ⚠️  WARNING: Limited data ({days_fetched} days)")
        print(f"   Recommended minimum: {min_required} days (RSI period + buffer)")
        print(f"   Continuing, but expect limited signals...\n")

    # Create engine
    engine = BacktestEngine(initial_capital=100000.0, commission=0.001)
    engine.add_data(symbol, data)

    # Create RSI strategy
    strategy = RSIMomentum(
        symbols=[symbol],
        period=rsi_period,
        oversold=30,
        overbought=70,
        allocation=0.8
    )
    engine.set_strategy(strategy)

    # Run
    print("Running backtest...")
    equity_curve = engine.run()

    # Analyze
    trades = engine.portfolio.get_trade_history()
    metrics = PerformanceMetrics.calculate_all_metrics(equity_curve, trades)

    # Print results
    print("\nRSI Strategy Results:")
    print(f"  Total Return:      {metrics['total_return']*100:.2f}%")
    print(f"  Annualized Return: {metrics['annualized_return']*100:.2f}%")
    print(f"  Sharpe Ratio:      {metrics['sharpe_ratio']:.2f}")
    print(f"  Max Drawdown:      {metrics['max_drawdown_pct']*100:.2f}%")
    print(f"  Total Trades:      {metrics['total_trades']}")

    return equity_curve, metrics, symbol, strategy, start_date, end_date


def run_roc_backtest():
    """Run backtest with Rate of Change momentum strategy."""
    print("\n" + "=" * 60)
    print("Rate of Change Momentum Strategy Backtest")
    print("=" * 60)

    # Fetch real data from Yahoo Finance
    symbol = "MSFT"  # Microsoft stock - good for momentum strategies
    start_date = "2020-01-01"
    end_date = "2023-12-31"

    print(f"\nFetching market data from Yahoo Finance for {symbol}...")
    try:
        data = fetch_ticker_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            interval="1d"
        )
    except ValueError as e:
        print(f"Error: {e}")
        return None, None, None, None, None, None

    # Validate sufficient data for ROC strategy
    roc_period = 20
    days_fetched = len(data)
    min_required = roc_period + 30  # ROC period + buffer for signal generation

    if days_fetched < min_required:
        print(f"   ⚠️  WARNING: Limited data ({days_fetched} days)")
        print(f"   Recommended minimum: {min_required} days (ROC period + buffer)")
        print(f"   Continuing, but expect limited signals...\n")

    # Create engine
    engine = BacktestEngine(initial_capital=100000.0, commission=0.001)
    engine.add_data(symbol, data)

    # Create ROC strategy
    strategy = RateOfChangeMomentum(
        symbols=[symbol],
        period=roc_period,
        buy_threshold=3.0,
        sell_threshold=-3.0,
        allocation=0.8
    )
    engine.set_strategy(strategy)

    # Run
    print("Running backtest...")
    equity_curve = engine.run()

    # Analyze
    trades = engine.portfolio.get_trade_history()
    metrics = PerformanceMetrics.calculate_all_metrics(equity_curve, trades)

    # Print results
    print("\nROC Strategy Results:")
    print(f"  Total Return:      {metrics['total_return']*100:.2f}%")
    print(f"  Annualized Return: {metrics['annualized_return']*100:.2f}%")
    print(f"  Sharpe Ratio:      {metrics['sharpe_ratio']:.2f}")
    print(f"  Max Drawdown:      {metrics['max_drawdown_pct']*100:.2f}%")
    print(f"  Total Trades:      {metrics['total_trades']}")

    return equity_curve, metrics, symbol, strategy, start_date, end_date


def main():
    """Run multiple momentum strategy backtests."""
    print("=" * 60)
    print("Momentum Strategy Backtesting Examples")
    print("=" * 60)
    print("\nThis script compares two momentum strategies:")
    print("  1. RSI Momentum (AAPL, 2020-01-01 to 2023-12-31)")
    print("  2. Rate of Change Momentum (MSFT, 2020-01-01 to 2023-12-31)")
    print("\nNote: This script uses hardcoded defaults.")
    print("To customize, edit the symbol/dates in run_rsi_backtest() and run_roc_backtest() functions")
    print("or use the simple_ma_backtest.py for command-line customization.")

    # Run both strategies
    rsi_equity, rsi_metrics, rsi_symbol, rsi_strategy, rsi_start, rsi_end = run_rsi_backtest()
    roc_equity, roc_metrics, roc_symbol, roc_strategy, roc_start, roc_end = run_roc_backtest()

    # Check if both backtests succeeded
    if rsi_equity is None or roc_equity is None:
        print("\nOne or more backtests failed. Exiting.")
        return

    # Compare
    print("\n" + "=" * 60)
    print("STRATEGY COMPARISON")
    print("=" * 60)
    print(f"{'Metric':<25} {'RSI':<15} {'ROC':<15}")
    print("-" * 60)
    print(f"{'Total Return':<25} {rsi_metrics['total_return']*100:>6.2f}%       {roc_metrics['total_return']*100:>6.2f}%")
    print(f"{'Annualized Return':<25} {rsi_metrics['annualized_return']*100:>6.2f}%       {roc_metrics['annualized_return']*100:>6.2f}%")
    print(f"{'Sharpe Ratio':<25} {rsi_metrics['sharpe_ratio']:>6.2f}         {roc_metrics['sharpe_ratio']:>6.2f}")
    print(f"{'Max Drawdown':<25} {rsi_metrics['max_drawdown_pct']*100:>6.2f}%       {roc_metrics['max_drawdown_pct']*100:>6.2f}%")
    print(f"{'Total Trades':<25} {rsi_metrics['total_trades']:>6}         {roc_metrics['total_trades']:>6}")
    print("=" * 60)

    # Save visualizations
    print("\nGenerating visualizations...")
    try:
        import matplotlib.pyplot as plt

        # Create results directory
        results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
        os.makedirs(results_dir, exist_ok=True)

        # Save RSI results
        rsi_strategy_name = rsi_strategy.name.lower().replace(' ', '_')
        rsi_time_period = f"{rsi_start.replace('-', '')}_{rsi_end.replace('-', '')}"
        rsi_filename = f"{rsi_symbol}_{rsi_strategy_name}_{rsi_time_period}_results.png"

        fig = BacktestVisualizer.create_summary_dashboard(rsi_equity, rsi_metrics)
        rsi_path = os.path.join(results_dir, rsi_filename)
        plt.savefig(rsi_path, dpi=150, bbox_inches='tight')
        print(f"  Saved {rsi_path}")
        plt.close()

        # Save ROC results
        roc_strategy_name = roc_strategy.name.lower().replace(' ', '_')
        roc_time_period = f"{roc_start.replace('-', '')}_{roc_end.replace('-', '')}"
        roc_filename = f"{roc_symbol}_{roc_strategy_name}_{roc_time_period}_results.png"

        fig = BacktestVisualizer.create_summary_dashboard(roc_equity, roc_metrics)
        roc_path = os.path.join(results_dir, roc_filename)
        plt.savefig(roc_path, dpi=150, bbox_inches='tight')
        print(f"  Saved {roc_path}")
        plt.close()

    except ImportError:
        print("  Matplotlib not available, skipping visualizations")

    print("\nBacktests complete!")


if __name__ == "__main__":
    main()

"""
Example backtest using RSI momentum strategy.

This demonstrates:
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


def generate_trending_data(
    symbol: str,
    start_date: str,
    end_date: str,
    initial_price: float = 100.0,
    volatility: float = 0.02,
    trend: float = 0.001,
    add_cycles: bool = True
) -> pd.DataFrame:
    """Generate synthetic data with trend and optional cycles."""
    dates = pd.date_range(start=start_date, end=end_date, freq='D')

    # Base random walk
    returns = np.random.normal(trend, volatility, len(dates))

    # Add cyclical component if requested
    if add_cycles:
        cycle_period = 60  # 60-day cycle
        cycle_amplitude = volatility * 2
        cycle = cycle_amplitude * np.sin(2 * np.pi * np.arange(len(dates)) / cycle_period)
        returns += cycle

    prices = initial_price * (1 + returns).cumprod()

    # Generate OHLC
    data = []
    for date, close in zip(dates, prices):
        daily_range = close * volatility * np.random.uniform(0.5, 1.5)
        high = close + abs(np.random.normal(0, daily_range / 2))
        low = close - abs(np.random.normal(0, daily_range / 2))
        open_price = low + (high - low) * np.random.random()

        data.append({
            'Date': date,
            'Open': open_price,
            'High': high,
            'Low': low,
            'Close': close,
            'Volume': int(np.random.uniform(1000000, 5000000))
        })

    df = pd.DataFrame(data)
    df.set_index('Date', inplace=True)

    return df


def run_rsi_backtest():
    """Run backtest with RSI momentum strategy."""
    print("\n" + "=" * 60)
    print("RSI Momentum Strategy Backtest")
    print("=" * 60)

    # Generate data with cycles (good for RSI)
    symbol = "CYCLICAL"
    start_date = "2020-01-01"
    end_date = "2023-12-31"
    data = generate_trending_data(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        initial_price=100.0,
        volatility=0.02,
        trend=0.0005,
        add_cycles=True
    )

    # Create engine
    engine = BacktestEngine(initial_capital=100000.0, commission=0.001)
    engine.add_data(symbol, data)

    # Create RSI strategy
    strategy = RSIMomentum(
        symbols=[symbol],
        period=14,
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

    # Generate trending data
    symbol = "TRENDING"
    start_date = "2020-01-01"
    end_date = "2023-12-31"
    data = generate_trending_data(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        initial_price=100.0,
        volatility=0.018,
        trend=0.0008,
        add_cycles=False
    )

    # Create engine
    engine = BacktestEngine(initial_capital=100000.0, commission=0.001)
    engine.add_data(symbol, data)

    # Create ROC strategy
    strategy = RateOfChangeMomentum(
        symbols=[symbol],
        period=20,
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

    # Run both strategies
    rsi_equity, rsi_metrics, rsi_symbol, rsi_strategy, rsi_start, rsi_end = run_rsi_backtest()
    roc_equity, roc_metrics, roc_symbol, roc_strategy, roc_start, roc_end = run_roc_backtest()

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

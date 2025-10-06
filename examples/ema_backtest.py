"""
Simple example of running an EMA crossover backtest.

This example demonstrates:
- Fetching real market data from Yahoo Finance
- Setting up a backtest with the EMA crossover strategy
- Running the backtest
- Analyzing results
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine.backtest import BacktestEngine
from src.strategies.moving_average import ExponentialMovingAverageCrossover
from src.analysis.metrics import PerformanceMetrics
from src.analysis.visualize import BacktestVisualizer
from src.data.fetchTickerData import fetch_ticker_data


def main(symbol=None, start_date=None, end_date=None, fast_period=None, slow_period=None, initial_capital=None):
    """Run an EMA crossover backtest."""
    # Get command line args if available
    import sys
    if '--symbol' in sys.argv:
        import argparse
        parser = argparse.ArgumentParser(description='Run exponential moving average crossover backtest')
        parser.add_argument('--symbol', type=str, default='SPY',
                            help='Stock ticker symbol (default: SPY)')
        parser.add_argument('--start-date', type=str, default='2020-01-01',
                            help='Start date YYYY-MM-DD (default: 2020-01-01)')
        parser.add_argument('--end-date', type=str, default='2023-12-31',
                            help='End date YYYY-MM-DD (default: 2023-12-31)')
        parser.add_argument('--fast-period', type=int, default=12,
                            help='Fast EMA period (default: 12)')
        parser.add_argument('--slow-period', type=int, default=26,
                            help='Slow EMA period (default: 26)')
        parser.add_argument('--capital', type=float, default=100000.0,
                            help='Initial capital (default: 100000.0)')
        args = parser.parse_args()

        symbol = args.symbol
        start_date = args.start_date
        end_date = args.end_date
        fast_period = args.fast_period
        slow_period = args.slow_period
        initial_capital = args.capital

    # Use defaults if not provided
    symbol = symbol or "SPY"
    start_date = start_date or "2020-01-01"
    end_date = end_date or "2023-12-31"
    fast_period = fast_period or 12
    slow_period = slow_period or 26
    initial_capital = initial_capital or 100000.0

    print("=" * 60)
    print("Exponential Moving Average Crossover Backtest Example")
    print("=" * 60)
    print("\nUsing defaults:")
    print(f"  Symbol:         {symbol}")
    print(f"  Date Range:     {start_date} to {end_date}")
    print(f"  Fast EMA:       {fast_period} days")
    print(f"  Slow EMA:       {slow_period} days")
    print(f"  Initial Capital: ${initial_capital:,.0f}")
    print("\nTo use different values, run:")
    print("  python examples/ema_backtest.py --symbol AAPL --start-date 2023-01-01 --end-date 2023-12-31")
    print("  python examples/ema_backtest.py --fast-period 9 --slow-period 21 --capital 50000")
    print("  python examples/ema_backtest.py --help  (for all options)")

    # Fetch real data from Yahoo Finance
    print(f"\n1. Fetching market data from Yahoo Finance for {symbol}...")
    try:
        data = fetch_ticker_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            interval="1d"
        )
    except ValueError as e:
        print(f"   Error: {e}")
        print("   Please check the ticker symbol and date range.")
        return

    # Validate sufficient data for strategy
    days_fetched = len(data)
    min_required = slow_period + 50  # Need slow_period + buffer for meaningful crossovers

    if days_fetched <= min_required:
        print(f"\n   ⚠️  WARNING: Insufficient data for strategy!")
        print(f"   Data fetched: {days_fetched} days")
        print(f"   Minimum recommended: {min_required} days ({slow_period}-day EMA + 50 day buffer)")
        print(f"   First valid {slow_period}-day EMA: ~day {slow_period} of backtest")
        print(f"\n   Recommendations:")
        print(f"   • Extend date range: --start-date 2021-01-01 (or earlier)")
        print(f"   • Use shorter periods: --fast-period 9 --slow-period 21")
        print(f"\n   Continuing anyway, but expect limited/no trading signals...\n")

    # Create backtest engine
    print("\n2. Setting up backtest engine...")
    engine = BacktestEngine(
        initial_capital=initial_capital,
        commission=0.001  # 0.1% commission
    )

    # Add data
    engine.add_data(symbol, data)

    # Create strategy
    print(f"\n3. Creating exponential moving average crossover strategy (fast={fast_period}, slow={slow_period})...")
    strategy = ExponentialMovingAverageCrossover(
        symbols=[symbol],
        fast_period=fast_period,
        slow_period=slow_period,
        allocation=0.9  # Use 90% of capital
    )
    engine.set_strategy(strategy)

    # Run backtest
    print("\n4. Running backtest...")
    equity_curve = engine.run()
    print(f"   Backtest complete! Processed {len(equity_curve)} trading days")

    # Get results
    print("\n5. Analyzing results...")
    trades = engine.portfolio.get_trade_history()
    metrics = PerformanceMetrics.calculate_all_metrics(
        equity_curve=equity_curve,
        trades=trades,
        risk_free_rate=0.02
    )

    # Print results
    print("\n" + "=" * 60)
    print("PERFORMANCE SUMMARY")
    print("=" * 60)
    print(f"Initial Capital:     ${metrics['initial_capital']:,.2f}")
    print(f"Final Value:         ${metrics['final_value']:,.2f}")
    print(f"Total Return:        {metrics['total_return']*100:.2f}%")
    print(f"Annualized Return:   {metrics['annualized_return']*100:.2f}%")
    print(f"Sharpe Ratio:        {metrics['sharpe_ratio']:.2f}")
    print(f"Volatility:          {metrics['volatility']*100:.2f}%")
    print(f"Max Drawdown:        {metrics['max_drawdown_pct']*100:.2f}%")
    print(f"Total Trades:        {metrics['total_trades']}")
    print("=" * 60)

    # Display equity curve
    print("\n6. Generating visualizations...")
    try:
        import matplotlib.pyplot as plt

        # Create results directory if it doesn't exist
        results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
        os.makedirs(results_dir, exist_ok=True)

        # Create filename: ticker_strategy_timeperiod_results.png
        strategy_name = strategy.name.lower().replace(' ', '_')
        time_period = f"{start_date.replace('-', '')}_{end_date.replace('-', '')}"
        filename = f"{symbol}_{strategy_name}_{time_period}_results.png"

        # Create dashboard
        fig = BacktestVisualizer.create_summary_dashboard(equity_curve, metrics)
        output_path = os.path.join(results_dir, filename)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"   Saved {output_path}")

        # Optionally show plot
        # plt.show()

    except ImportError:
        print("   Matplotlib not available, skipping visualizations")

    print("\nBacktest complete!")


if __name__ == "__main__":
    main()

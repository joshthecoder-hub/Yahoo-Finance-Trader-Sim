# Systematic Trading Simulator & Backtester

A modular Python backtesting framework for simulating and analyzing systematic equity trading strategies.

## Features

- Time-series backtesting engine
- Built-in strategies: Moving Average (SMA/EMA), RSI, Rate of Change
- Portfolio management with P&L tracking
- Performance analytics (Sharpe, drawdown, returns)
- Yahoo Finance integration via yfinance

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```bash
# Run example backtests
python examples/simple_ma_backtest.py
python examples/ema_backtest.py
python examples/momentum_backtest.py
```

## Usage

```python
from src.engine.backtest import BacktestEngine
from src.strategies.moving_average import MovingAverageCrossover
from src.analysis.metrics import PerformanceMetrics

# Create engine and strategy
engine = BacktestEngine(initial_capital=100000, commission=0.001)
strategy = MovingAverageCrossover(symbols=["AAPL"], fast_period=50, slow_period=200)
engine.set_strategy(strategy)

# Run and analyze
equity_curve = engine.run()
metrics = PerformanceMetrics.calculate_all_metrics(equity_curve, engine.portfolio.get_trade_history())
```

## Testing

Run the test suite to verify functionality:

```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/test_integration.py -v      # End-to-end integration tests
pytest tests/test_data_fetcher.py -v      # Data fetching tests
pytest tests/test_portfolio.py -v         # Portfolio management tests
pytest tests/test_backtest_engine.py -v   # Backtesting engine tests

# Run example scripts
python examples/simple_ma_backtest.py
python examples/ema_backtest.py
python examples/momentum_backtest.py
```

## License

MIT

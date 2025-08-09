# Systematic Trading Simulator & Backtester

A modular Python backtesting framework for simulating and analyzing systematic equity trading strategies.

## Features

- **Event-driven backtesting engine** - Realistic simulation of time-series trading
- **Modular strategy framework** - Easy to implement custom strategies
- **Multiple built-in strategies**:
  - Moving Average Crossover (SMA/EMA)
  - RSI Momentum
  - Rate of Change Momentum
- **Comprehensive P&L tracking** - Portfolio management with position tracking
- **Performance analytics** - Sharpe ratio, drawdown, returns, and more
- **Visualization tools** - Equity curves, drawdowns, returns distribution
- **Yahoo Finance MCP integration** - Fetch real market data

## Project Structure

```
Yahoo-Finance-Trader-Sim/
├── src/
│   ├── data/          # MCP data fetcher for Yahoo Finance
│   ├── engine/        # Core backtesting engine
│   ├── strategies/    # Trading strategy implementations
│   ├── execution/     # Order management and execution
│   ├── portfolio/     # Portfolio management and P&L tracking
│   └── analysis/      # Performance metrics and visualization
├── tests/             # Unit tests
├── examples/          # Example backtest scripts
└── requirements.txt   # Python dependencies
```

## Installation

```bash
# Clone the repository
git clone https://github.com/joshthecoder-hub/Yahoo-Finance-Trader-Sim.git
cd Yahoo-Finance-Trader-Sim

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Running a Simple Backtest

```python
from src.engine.backtest import BacktestEngine
from src.strategies.moving_average import MovingAverageCrossover

# Create backtest engine
engine = BacktestEngine(
    initial_capital=100000.0,
    commission=0.001  # 0.1% per trade
)

# Add market data (from Yahoo Finance MCP or synthetic)
engine.add_data(symbol, historical_data)

# Create and set strategy
strategy = MovingAverageCrossover(
    symbols=["AAPL"],
    fast_period=50,
    slow_period=200,
    allocation=0.9
)
engine.set_strategy(strategy)

# Run backtest
equity_curve = engine.run()

# Analyze results
from src.analysis.metrics import PerformanceMetrics
trades = engine.portfolio.get_trade_history()
metrics = PerformanceMetrics.calculate_all_metrics(equity_curve, trades)

print(f"Total Return: {metrics['total_return']*100:.2f}%")
print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {metrics['max_drawdown_pct']*100:.2f}%")
```

### Running Example Backtests

```bash
# Simple moving average crossover backtest
python examples/simple_ma_backtest.py

# Momentum strategy comparison
python examples/momentum_backtest.py
```

## Creating Custom Strategies

Extend the `Strategy` base class to implement your own trading logic:

```python
from src.strategies.base import Strategy
from src.execution.order import OrderSide

class MyCustomStrategy(Strategy):
    def __init__(self, symbols, **params):
        super().__init__("My Custom Strategy")
        self.symbols = symbols
        # Initialize your parameters

    def generate_signals(self, data, current_date):
        signals = []

        for symbol in self.symbols:
            # Your signal logic here
            if buy_condition:
                signals.append({
                    'symbol': symbol,
                    'side': OrderSide.BUY,
                    'quantity': quantity
                })
            elif sell_condition:
                signals.append({
                    'symbol': symbol,
                    'side': OrderSide.SELL,
                    'quantity': quantity
                })

        return signals
```

## Performance Metrics

The framework calculates comprehensive performance metrics:

- **Return metrics**: Total return, annualized return
- **Risk metrics**: Volatility, Sharpe ratio
- **Drawdown metrics**: Maximum drawdown, drawdown duration
- **Trade metrics**: Win rate, profit factor, total trades

## Visualization

Generate insightful visualizations:

```python
from src.analysis.visualize import BacktestVisualizer

# Create summary dashboard
fig = BacktestVisualizer.create_summary_dashboard(equity_curve, metrics)
fig.savefig('backtest_results.png')

# Individual plots
BacktestVisualizer.plot_equity_curve(equity_curve)
BacktestVisualizer.plot_drawdown(equity_curve)
BacktestVisualizer.plot_returns_distribution(equity_curve)
```

## Yahoo Finance MCP Integration

The framework integrates with the [Yahoo Finance MCP server](https://github.com/joshthecoder-hub/Yahoo-Finance-MCP) for fetching real market data:

```python
from src.data.mcp_fetcher import MCPDataFetcher

# Initialize with MCP client (requires Yahoo-Finance-MCP server running)
fetcher = MCPDataFetcher(mcp_client)

# Fetch historical data
data = fetcher.fetch_historical_data(
    symbol="AAPL",
    start_date="2020-01-01",
    end_date="2023-12-31",
    interval="1d"
)
```

For setup instructions, see the [Yahoo Finance MCP repository](https://github.com/joshthecoder-hub/Yahoo-Finance-MCP).

## Key Learnings

This project demonstrates:
- **Modular, maintainable Python code** for handling time-series data
- **Event-driven architecture** for realistic backtesting
- **Systematic research workflow** - hypothesis testing, backtesting, and analysis
- **Performance optimization** with efficient pandas operations
- **Professional-grade financial analytics**

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

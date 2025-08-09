"""Portfolio management and P&L tracking."""
from typing import Dict, List
import pandas as pd
from datetime import datetime
from ..execution.order import Order, OrderSide, OrderExecutor, Fill


class Portfolio:
    """Manages portfolio positions, cash, and P&L tracking."""

    def __init__(self, initial_capital: float, commission_rate: float = 0.001):
        """
        Initialize portfolio.

        Args:
            initial_capital: Starting cash amount
            commission_rate: Commission rate per trade
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, int] = {}  # symbol -> quantity
        self.avg_prices: Dict[str, float] = {}  # symbol -> average cost basis
        self.executor = OrderExecutor(commission_rate)

        # Performance tracking
        self.total_value = initial_capital
        self.equity_curve: List[Dict] = []
        self.trades: List[Fill] = []
        self.realized_pnl = 0.0
        self.unrealized_pnl = 0.0

    def execute_order(self, order: Order, current_price: float) -> bool:
        """
        Execute an order and update portfolio state.

        Args:
            order: Order to execute
            current_price: Current market price

        Returns:
            True if order was executed successfully
        """
        # Execute the order
        fill = self.executor.execute_market_order(order, current_price, order.timestamp)

        if fill is None:
            return False

        # Update portfolio based on fill
        if fill.side == OrderSide.BUY:
            return self._process_buy(fill)
        else:
            return self._process_sell(fill)

    def _process_buy(self, fill: Fill) -> bool:
        """Process a buy order fill."""
        total_cost = fill.quantity * fill.price + fill.commission

        # Check if we have enough cash
        if total_cost > self.cash:
            return False

        # Update cash
        self.cash -= total_cost

        # Update position
        if fill.symbol in self.positions:
            # Update average price
            current_qty = self.positions[fill.symbol]
            current_avg = self.avg_prices[fill.symbol]
            total_qty = current_qty + fill.quantity
            self.avg_prices[fill.symbol] = (
                (current_qty * current_avg + fill.quantity * fill.price) / total_qty
            )
            self.positions[fill.symbol] = total_qty
        else:
            self.positions[fill.symbol] = fill.quantity
            self.avg_prices[fill.symbol] = fill.price

        # Record trade
        self.trades.append(fill)

        return True

    def _process_sell(self, fill: Fill) -> bool:
        """Process a sell order fill."""
        # Check if we have the position
        if fill.symbol not in self.positions:
            return False

        if self.positions[fill.symbol] < fill.quantity:
            return False

        # Calculate realized P&L
        avg_cost = self.avg_prices[fill.symbol]
        realized = (fill.price - avg_cost) * fill.quantity - fill.commission
        self.realized_pnl += realized

        # Update cash
        proceeds = fill.quantity * fill.price - fill.commission
        self.cash += proceeds

        # Update position
        self.positions[fill.symbol] -= fill.quantity

        # Remove position if fully closed
        if self.positions[fill.symbol] == 0:
            del self.positions[fill.symbol]
            del self.avg_prices[fill.symbol]

        # Record trade
        self.trades.append(fill)

        return True

    def update_positions(
        self,
        current_data: Dict[str, pd.DataFrame],
        timestamp: datetime
    ):
        """
        Update portfolio value and unrealized P&L.

        Args:
            current_data: Current market data for all symbols
            timestamp: Current timestamp
        """
        # Calculate unrealized P&L
        unrealized = 0.0
        position_value = 0.0

        for symbol, quantity in self.positions.items():
            if symbol in current_data and timestamp in current_data[symbol].index:
                current_price = current_data[symbol].loc[timestamp, 'Close']
                avg_cost = self.avg_prices[symbol]

                position_value += quantity * current_price
                unrealized += (current_price - avg_cost) * quantity

        self.unrealized_pnl = unrealized
        self.total_value = self.cash + position_value

        # Record in equity curve
        self.equity_curve.append({
            'timestamp': timestamp,
            'total_value': self.total_value,
            'cash': self.cash,
            'position_value': position_value,
            'realized_pnl': self.realized_pnl,
            'unrealized_pnl': self.unrealized_pnl
        })

    def get_performance_history(self) -> pd.DataFrame:
        """
        Get portfolio performance history.

        Returns:
            DataFrame with performance metrics over time
        """
        if not self.equity_curve:
            return pd.DataFrame()

        df = pd.DataFrame(self.equity_curve)
        df.set_index('timestamp', inplace=True)

        return df

    def get_current_positions(self) -> Dict[str, Dict]:
        """
        Get current positions with details.

        Returns:
            Dictionary mapping symbols to position details
        """
        positions = {}
        for symbol, quantity in self.positions.items():
            positions[symbol] = {
                'quantity': quantity,
                'avg_price': self.avg_prices[symbol],
                'cost_basis': quantity * self.avg_prices[symbol]
            }
        return positions

    def get_trade_history(self) -> pd.DataFrame:
        """
        Get trade history as DataFrame.

        Returns:
            DataFrame with all executed trades
        """
        if not self.trades:
            return pd.DataFrame()

        trades_data = []
        for fill in self.trades:
            trades_data.append({
                'timestamp': fill.timestamp,
                'symbol': fill.symbol,
                'side': fill.side.value,
                'quantity': fill.quantity,
                'price': fill.price,
                'commission': fill.commission,
                'total': fill.quantity * fill.price
            })

        df = pd.DataFrame(trades_data)
        df.set_index('timestamp', inplace=True)

        return df

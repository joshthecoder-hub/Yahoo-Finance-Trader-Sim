"""Order management and execution logic."""
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


class OrderType(Enum):
    """Order types supported by the execution system."""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderSide(Enum):
    """Order side (buy or sell)."""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    """Order status."""
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class Order:
    """Represents a trading order."""
    symbol: str
    order_type: OrderType
    side: OrderSide
    quantity: int
    timestamp: datetime
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: int = 0
    fill_price: Optional[float] = None
    fill_timestamp: Optional[datetime] = None
    order_id: Optional[str] = None

    def __post_init__(self):
        """Validate order parameters."""
        if self.quantity <= 0:
            raise ValueError("Order quantity must be positive")

        if self.order_type == OrderType.LIMIT and self.limit_price is None:
            raise ValueError("Limit orders require a limit price")

        if self.order_type == OrderType.STOP and self.stop_price is None:
            raise ValueError("Stop orders require a stop price")

        if self.order_type == OrderType.STOP_LIMIT:
            if self.limit_price is None or self.stop_price is None:
                raise ValueError("Stop-limit orders require both limit and stop prices")


@dataclass
class Fill:
    """Represents an order fill."""
    order_id: str
    symbol: str
    side: OrderSide
    quantity: int
    price: float
    timestamp: datetime
    commission: float


class OrderExecutor:
    """Handles order execution logic."""

    def __init__(self, commission_rate: float = 0.001):
        """
        Initialize order executor.

        Args:
            commission_rate: Commission rate per trade (default 0.1%)
        """
        self.commission_rate = commission_rate
        self.next_order_id = 1

    def execute_market_order(
        self,
        order: Order,
        current_price: float,
        timestamp: datetime
    ) -> Fill:
        """
        Execute a market order at current price.

        Args:
            order: Order to execute
            current_price: Current market price
            timestamp: Execution timestamp

        Returns:
            Fill object with execution details
        """
        if order.order_id is None:
            order.order_id = str(self.next_order_id)
            self.next_order_id += 1

        commission = abs(order.quantity * current_price * self.commission_rate)

        fill = Fill(
            order_id=order.order_id,
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=current_price,
            timestamp=timestamp,
            commission=commission
        )

        order.status = OrderStatus.FILLED
        order.filled_quantity = order.quantity
        order.fill_price = current_price
        order.fill_timestamp = timestamp

        return fill

    def execute_limit_order(
        self,
        order: Order,
        current_price: float,
        timestamp: datetime
    ) -> Optional[Fill]:
        """
        Execute a limit order if price conditions are met.

        Args:
            order: Limit order to execute
            current_price: Current market price
            timestamp: Execution timestamp

        Returns:
            Fill object if executed, None otherwise
        """
        if order.limit_price is None:
            return None

        # For buy orders, execute if current price <= limit price
        # For sell orders, execute if current price >= limit price
        should_execute = (
            (order.side == OrderSide.BUY and current_price <= order.limit_price) or
            (order.side == OrderSide.SELL and current_price >= order.limit_price)
        )

        if should_execute:
            return self.execute_market_order(order, order.limit_price, timestamp)

        return None

    def can_execute(self, order: Order, current_price: float) -> bool:
        """
        Check if an order can be executed at current price.

        Args:
            order: Order to check
            current_price: Current market price

        Returns:
            True if order can be executed
        """
        if order.order_type == OrderType.MARKET:
            return True

        if order.order_type == OrderType.LIMIT and order.limit_price is not None:
            if order.side == OrderSide.BUY:
                return current_price <= order.limit_price
            else:
                return current_price >= order.limit_price

        if order.order_type == OrderType.STOP and order.stop_price is not None:
            if order.side == OrderSide.BUY:
                return current_price >= order.stop_price
            else:
                return current_price <= order.stop_price

        return False

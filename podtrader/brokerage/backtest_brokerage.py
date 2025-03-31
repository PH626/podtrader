import numpy as np
import pandas as pd
from ..enums import OrderStatus, RuleType, TradeAction, SizeType
from ..events import SignalEvent
from ..utils import get_logger

logger = get_logger('BacktestBrokerage')

__all__ = ["BacktestBrokerage"]


class Order:
    def __init__(self, create_time, action, size):
        self.create_time = create_time
        self.action = action
        self.size = size

    def __str__(self):
        return f"{self.create_time}: -{self.action}@{self.size}"

    def to_dict(self):
        return {
            "create_time": self.create_time,
            "action": self.action,
            "size": self.size
        }


class BacktestBrokerage:
    def __init__(self, init_cash: float, position: float = 0.0):
        self.cash = init_cash
        self.position = position
        self.status = OrderStatus.EMPTY
        self.orders = []

    def _open_size(self, price: float, size: float, size_type: int = 3) -> int:
        """
        计算开仓数量
        Amount: int = 0         # 数量
        Value: int = 1          # 价值
        Percent: int = 2        # 小数
        Percent100: int = 3     # 百分比

        Args:
            price: 价格
            size: 数量
            size_type: 数量类型

        Returns:
            int: 开仓数量

        Examples:
            >>> self._open_size(100, 100, 3)
            1
            >>> self._open_size(100, 0.01, 2)
            0
        """
        size_type = SizeType(size_type)
        if self.cash <= 0:
            return 0
        max_amount = int(self.cash / price)
        if size_type == SizeType.Value:
            amount = int(size / price)
        elif size_type == SizeType.Percent:
            amount = int(self.cash * size / price)
        elif size_type == SizeType.Percent100:
            amount = int(self.cash * size / 100 / price)
        else:
            amount = int(size)
        return min(max_amount, amount)

    def _close_size(self, price: float, size: float, size_type: int = 3) -> int:
        """
        计算平仓数量

        Args:
            price: 价格
            size: 数量
            size_type: 数量类型

        Returns:
            int: 平仓数量
        """
        size_type = SizeType(size_type)
        if self.position == 0:
            return 0
        max_amount = int(abs(self.position))
        if size_type == SizeType.Value:
            amount = int(size / price)
        elif size_type == SizeType.Percent:
            amount = int(abs(self.position) * size)
        elif size_type == SizeType.Percent100:
            amount = int(abs(self.position) * size / 100)
        else:
            amount = int(size)
        return min(max_amount, amount)

    def place_order(self, event: SignalEvent):
        if event.rule_type == RuleType.Open:
            # 建仓
            # 1. 买涨
            # 1.1 当前没有持仓，买入size，状态为LONG_FILLED
            # 1.2 当前有持仓并且方向为买涨，不操作
            # 1.3 当前有持仓并且方向为买跌，平仓，买入size，状态为LONG_FILLED
            # 2. 买跌
            # 2.1 当前没有持仓，卖出size，状态为SHORT_FILLED
            # 2.2 当前有持仓并且方向为买涨，平仓，卖出size，状态为SHORT_FILLED
            # 2.3 当前有持仓并且方向为买跌，不操作
            if self.status == OrderStatus.EMPTY:
                size = self._open_size(event.price, event.size, event.size_type)
                if size <= 0:
                    return
                if event.action == TradeAction.BUY:
                    self.status = OrderStatus.LONG_FILLED
                    self.position = size
                    self.cash -= size * event.price
                    action = 'long_entry'
                elif event.action == TradeAction.SHORT:
                    self.status = OrderStatus.SHORT_FILLED
                    self.position = -size
                    self.cash += size * event.price
                    action = 'short_entry'
                else:
                    return
                order = Order(
                    event.timestamp,
                    action,
                    size
                )
                self.orders.append(order)
                logger.info(f"Open Position: {order}")
                run_params = {
                    'buy_time': event.timestamp,
                    'buy_price': event.price,
                    'position': size,
                    'cash': self.cash,
                }
                return run_params
        elif event.rule_type == RuleType.Close:
            # 平仓
            # 1. 当前没有持仓，不操作
            # 2. 当前持有多头仓位，平仓方向是买跌平仓，不操作
            # 3. 当前持有多头仓位，平仓方向是买涨平仓，平仓，状态为EMPTY
            # 4. 当前持有空头仓位，平仓方向是买涨平仓，不操作
            # 5. 当前持有空头仓位，平仓方向是买跌平仓，平仓，状态为EMPTY
            if self.status == OrderStatus.EMPTY:
                return
            if self.status.name.startswith("LONG"):
                if event.action == TradeAction.SELL:
                    # 平仓
                    self.cash += self.position * event.price
                    self.status = OrderStatus.EMPTY
                    order = Order(
                        event.timestamp,
                        'long_exit',
                        self.position
                    )
                    self.position = 0
                    self.orders.append(order)
                    logger.info(f"Close Position: {order}")
                    run_params = {
                        'sell_time': event.timestamp,
                        'sell_price': event.price,
                        'position': 0,
                        'cash': self.cash,
                    }
                    return run_params
            elif self.status.name.startswith("SHORT"):
                if event.action == TradeAction.BUY:
                    # 平仓
                    self.cash += self.position * event.price
                    self.status = OrderStatus.EMPTY
                    order = Order(
                        event.timestamp,
                        'short_exit',
                        -self.position
                    )
                    self.position = 0
                    self.orders.append(order)
                    logger.info(f"Close Position: {order}")
                    run_params = {
                        'sell_time': event.timestamp,
                        'sell_price': event.price,
                        'position': 0,
                        'cash': self.cash,
                    }
                    return run_params
        elif event.rule_type == RuleType.StopLoss:
            # 止损
            # 1. 当前没有持仓，不操作
            # 2. 当前持有多头仓位，止损方向是买跌，不操作
            # 3. 当前持有多头仓位，止损方向是买涨，减少size，如果size为0，状态为EMPTY，否则状态为LONG_STOP_LOSS_FILLED
            # 4. 当前持有空头仓位，止损方向是买涨，不操作
            # 5. 当前持有空头仓位，止损方向是买跌，减少size，如果size为0，状态为EMPTY，否则状态为SHORT_STOP_LOSS_FILLED
            if self.status == OrderStatus.EMPTY:
                return
            # 止损
            size = self._close_size(event.size)
            if size == 0:
                return
            if self.status.name.startswith("LONG"):
                if event.action == TradeAction.SELL:
                    self.position -= size
                    if self.position == 0:
                        self.status = OrderStatus.EMPTY
                    else:
                        self.status = OrderStatus.LONG_STOP_LOSS_FILLED
                    order = Order(
                        event.timestamp,
                        'long_exit',
                        size
                    )
                    self.orders.append(order)
                    logger.debug(f"Stop Loss: {order}")
                    run_params = {
                        'sell_time': event.timestamp,
                        'sell_price': event.price,
                        'position': self.position,
                        'cash': self.cash,
                    }
                    return run_params
            elif self.status.name.startswith("SHORT"):
                if event.action == TradeAction.BUY:
                    self.position += size
                    if self.position == 0:
                        self.status = OrderStatus.EMPTY
                    else:
                        self.status = OrderStatus.SHORT_STOP_LOSS_FILLED
                    order = Order(
                        event.timestamp,
                        'short_exit',
                        size
                    )
                    self.orders.append(order)
                    logger.info(f"Stop Loss: {order}")
                    run_params = {
                        'sell_time': event.timestamp,
                        'sell_price': event.price,
                        'position': self.position,
                        'cash': self.cash,
                    }
                    return run_params
        elif event.rule_type == RuleType.TakeProfit:
            # 止盈
            # 1. 当前没有持仓，不操作
            # 2. 当前持有多头仓位，止盈方向是买跌，不操作
            # 3. 当前持有多头仓位，止盈方向是买涨，减少size，如果size为0，状态为EMPTY，否则状态为LONG_TAKE_PROFIT_FILLED
            # 4. 当前持有空头仓位，止盈方向是买涨，不操作
            # 5. 当前持有空头仓位，止盈方向是买跌，减少size，如果size为0，状态为EMPTY，否则状态为SHORT_TAKE_PROFIT_FILLED
            if self.status == OrderStatus.EMPTY:
                return
            # 止盈
            size = self._close_size(event.size)
            if size == 0:
                return
            if self.status.name.startswith("LONG"):
                if event.action == TradeAction.SELL:
                    self.position -= size
                    if self.position == 0:
                        self.status = OrderStatus.EMPTY
                    else:
                        self.status = OrderStatus.LONG_TAKE_PROFIT_FILLED
                    order = Order(
                        event.timestamp,
                        'long_exit',
                        size
                    )
                    self.orders.append(order)
                    logger.debug(f"Take Profit: {order}")
                    run_params = {
                        'sell_time': event.timestamp,
                        'sell_price': event.price,
                        'position': self.position,
                        'cash': self.cash,
                    }
                    return run_params
            elif self.status.name.startswith("SHORT"):
                if event.action == TradeAction.BUY:
                    self.position += size
                    if self.position == 0:
                        self.status = OrderStatus.EMPTY
                    else:
                        self.status = OrderStatus.SHORT_TAKE_PROFIT_FILLED
                    order = Order(
                        event.timestamp,
                        'short_exit',
                        size
                    )
                    self.orders.append(order)
                    logger.debug(f"Take Profit: {order}")
                    run_params = {
                        'sell_time': event.timestamp,
                        'sell_price': event.price,
                        'position': self.position,
                        'cash': self.cash,
                    }
                    return run_params
        else:
            return

    def get_signals(self) -> pd.DataFrame:
        orders = pd.DataFrame([order.to_dict() for order in self.orders])
        if orders.empty:
            return orders
        orders["create_time"] = pd.to_datetime(orders["create_time"])
        orders = orders.set_index("create_time")

        signals = pd.DataFrame(
            np.full(shape=(orders.shape[0], 4), fill_value=False),
            columns=['long_entry', 'long_exit', 'short_entry', 'short_exit'],
            index=orders.index
        )
        signals['size'] = 0
        signals['long_entry'][(orders['action'] == 'long_entry')] = True
        signals['long_exit'][(orders['action'] == 'long_exit')] = True
        signals['short_entry'][(orders['action'] == 'short_entry')] = True
        signals['short_exit'][(orders['action'] == 'short_exit')] = True
        signals['size'] = orders['size']
        signals.index = pd.to_datetime(signals.index)
        return signals

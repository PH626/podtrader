from enum import Enum

__all__ = ["OrderStatus"]


class OrderStatus(Enum):
    # 初始状态
    EMPTY = 0
    # Long开仓
    LONG_SUBMITTED = 11
    # Long开仓成功
    LONG_FILLED = 12
    # Long止损
    LONG_STOP_LOSS = 13
    # Long止损成功
    LONG_STOP_LOSS_FILLED = 14
    # Long止盈
    LONG_TAKE_PROFIT = 15
    # Long止盈成功
    LONG_TAKE_PROFIT_FILLED = 16
    # Long平仓
    LONG_CLOSE = 17
    # Long平仓成功
    LONG_CLOSE_FILLED = 18

    # Short开仓
    SHORT_SUBMITTED = 21
    # Short开仓成功
    SHORT_FILLED = 22
    # Short止损
    SHORT_STOP_LOSS = 23
    # Short止损成功
    SHORT_STOP_LOSS_FILLED = 24
    # Short止盈
    SHORT_TAKE_PROFIT = 25
    # Short止盈成功
    SHORT_TAKE_PROFIT_FILLED = 26
    # Short平仓
    SHORT_CLOSE = 27
    # Short平仓成功
    SHORT_CLOSE_FILLED = 28

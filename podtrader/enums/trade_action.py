from enum import Enum

__all__ = ['TradeAction']


class TradeAction(Enum):
    UNKNOWN = 0
    BUY = 1
    SELL = 2
    SHORT = 3

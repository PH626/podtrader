from .event import Event, EventType
from ..enums import RuleType, TradeAction, SizeType


class SignalEvent(Event):
    def __init__(self) -> None:
        self.event_type = EventType.SIGNAL
        self.rule_type: RuleType = RuleType.Unknown
        self.action: TradeAction = TradeAction.UNKNOWN
        self.symbol = ""
        self.sec_type = ""
        self.exchange = ""
        # 当前价格
        self.price = 0.0
        # 交易量
        self.size: float = 100.0
        self.size_type: int = 3
        # 优先级
        self.priority: int = 0
        self.timestamp = None

    def __str__(self):
        return f"SignalEvent: {self.timestamp} " \
               f"{self.rule_type.name} " \
               f"{self.action.name} " \
               f"{self.symbol} " \
               f"{self.price} " \
               f"{self.size} " \
               f"{self.priority}"

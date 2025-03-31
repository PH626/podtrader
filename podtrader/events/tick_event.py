from datetime import datetime
from enum import Enum
import pandas as pd

from .event import Event, EventType

__all__ = ["TickType", "TickEvent"]


class TickType(Enum):
    """
    Unlike IB, it does not have tick_size, e.g., TickTypeEnum.BID_SIZE
    """

    TRADE = 0
    BID = 1
    ASK = 2
    FULL = 3


class TickEvent(Event):
    """
    Tick event
    """

    def __init__(self) -> None:
        """
        Initialises Tick
        """
        self.event_type: EventType = EventType.TICK
        self.tick_type: TickType = TickType.TRADE
        self.timestamp: pd.Timestamp = pd.Timestamp("1970-01-01", tz="US/Eastern")
        self.full_symbol: str = ""
        self.price: float = 0.0

        self.open: float = 0.0
        self.high: float = 0.0
        self.low: float = 0.0
        self.close: float = 0.0
        self.volume: float = 0.0

    def __str__(self) -> str:
        return "%s,%s,%s,%s,%s" % (
            str(self.timestamp.strftime("%H:%M:%S.%f")),
            str(datetime.now().strftime("%H:%M:%S.%f")),
            str(self.full_symbol),
            self.tick_type,
            str(self.price)
        )

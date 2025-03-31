from enum import Enum


class RuleType(Enum):
    Unknown = 0
    Close = 1
    StopLoss = 2
    TakeProfit = 3
    Open = 4
    RiskControl = 5
    Special = 6

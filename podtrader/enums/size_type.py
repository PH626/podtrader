from enum import Enum


class SizeType(Enum):
    Amount: int = 0         # 数量
    Value: int = 1          # 价值
    Percent: int = 2        # 小数
    Percent100: int = 3     # 百分比

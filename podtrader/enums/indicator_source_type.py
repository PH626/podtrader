from enum import Enum


class IndicatorSourceType(Enum):
    Talib = 'talib'
    Ta = 'ta'
    PandasTa = 'pandas_ta'
    VectorHouse = 'vector-house'

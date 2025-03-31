import threading
from typing import List

from ...enums import TimeSpan
from ...entities.candle import Candle


class QuerySubscription:
    def __init__(self, query_id: int, symbol: str, candle_timespan: TimeSpan) -> None:
        """

        :param query_id:            唯一标识，用于标识查询
        :param symbol:              商品代码
        :param candle_timespan:     K线时间间隔
        """
        self.candle_timespan = candle_timespan
        self.symbol = symbol
        self.query_id = query_id
        self.done_event = threading.Event()
        self.candles: List[Candle] = []
        self.is_error = False

    def push_candles(self, candles: List[Candle]):
        """
        接收K线数据
        :param candles:
        :return:
        """
        self.candles += candles

    def done(self, is_error: bool = False):
        """
        完成查询
        :param is_error:
        :return:
        """
        self.is_error = is_error
        self.done_event.set()

    def result(self) -> List[Candle]:
        self.done_event.wait()

        if self.is_error:
            raise Exception("query failed. see logs.")

        return self.candles

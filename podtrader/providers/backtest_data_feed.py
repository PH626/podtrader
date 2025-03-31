from datetime import datetime
from typing import Iterator, Union

import pandas as pd

from .data_feed_base import DataFeedBase
from ..events import TickEvent


__all__ = ["BacktestDataFeed"]


class BacktestDataFeed(DataFeedBase):
    """
    BacktestDataFeed 使用 PLACEHOLDER 来 stream_next；
    实际数据来自 data_board.get_hist_price
    这是处理多个来源的简便方法
    """

    def __init__(
        self,
        start_date: Union[pd.Timestamp, datetime] = None,
        end_date: Union[pd.Timestamp, datetime] = None,
    ) -> None:
        """
        使用可选的开始和结束日期初始化 BacktestDataFeed。
        """
        if isinstance(start_date, datetime):
            start_date = pd.Timestamp(start_date)
        if isinstance(end_date, datetime):
            end_date = pd.Timestamp(end_date)
        self._end_date: pd.Timestamp = end_date
        self._start_date: pd.Timestamp = start_date
        self._data_stream: pd.DataFrame = None
        self._data_stream_iter: Iterator[pd.Timestamp] = iter([])

    def set_data_source(self, data: pd.DataFrame) -> None:
        """
        设置回测的数据源。数据应为带有日期时间索引的 DataFrame。
        """
        data.index = data.index.tz_localize(None)
        data.index = pd.to_datetime(data.index)
        if self._data_stream is None:
            self._data_stream = data
            self._data_stream_iter = iter(self._data_stream.index)
        else:
            self._data_stream = self._data_stream.join(data, how="outer", sort=True)
            self._data_stream_iter = iter(self._data_stream.index)

    def stream_next(self) -> TickEvent:
        """
        将下一个 TickEvent 放入事件队列。
        """
        index = next(self._data_stream_iter)

        t = TickEvent()
        t.full_symbol = "PLACEHOLDER"  # 符号的占位符
        t.timestamp = index
        t.open = self._data_stream.loc[index, "open"]
        t.high = self._data_stream.loc[index, "high"]
        t.low = self._data_stream.loc[index, "low"]
        t.close = self._data_stream.loc[index, "close"]
        t.volume = self._data_stream.loc[index, "volume"]

        return t

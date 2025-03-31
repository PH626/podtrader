from collections import deque
from datetime import datetime
from typing import Deque, Dict, Any, List, Union

import pandas as pd


class CandleQueue:
    def __init__(self, max_length: int = 300) -> None:
        """
        K线队列
        """
        self.max_length = max_length
        self.queue: Deque[Dict[str, Any]] = deque(maxlen=max_length)
        self.timestamp_index: Dict[datetime, int] = {}

    def put(self, candle: Dict[str, Any], replace: bool = True) -> None:
        """
        添加一个新的K线数据

        - timestamp: 时间戳
        - open: 开盘价
        - close: 收盘价
        - high: 最高价
        - low: 最低价
        - volume: 成交量

        :param candle: K线数据
        :param replace: 是否替换已有数据
        """
        timestamp = candle['dt']
        if timestamp in self.timestamp_index:
            index = self.timestamp_index[timestamp]
            if replace:
                # Replace the old kline data
                self.queue[index] = candle
            else:
                # Aggregate the kline data
                old_candle = self.queue[index]
                old_candle['open'] = candle['open']
                old_candle['close'] = candle['close']
                old_candle['high'] = max(candle['high'], old_candle['high'])
                old_candle['low'] = min(candle['low'], old_candle['low'])
                old_candle['volume'] += candle['volume']
        else:
            # Add new kline data
            if len(self.queue) == self.max_length:
                # Remove the oldest element
                oldest_kline = self.queue.popleft()
                del self.timestamp_index[oldest_kline['dt']]
            self.queue.append(candle)
            self.timestamp_index[timestamp] = len(self.queue) - 1

    def put_list(self, candles: List[Dict[str, Any]]) -> None:
        """
        添加多个K线数据

        :param candles: K线数据列表
        """
        for candle in candles:
            self.put(candle)

    def get_all(self) -> List[Dict[str, Any]]:
        """
        获取所有K线数据
        """
        return list(self.queue)


class SymbolIntervalCandleQueue:
    def __init__(self, symbol) -> None:
        self.symbol = symbol
        self.interval_candle_queues: Dict[str, CandleQueue] = {}

    def put(self, interval: str, candle: Dict[str, Any], replace: bool = True) -> None:
        if interval not in self.interval_candle_queues:
            self.interval_candle_queues[interval] = CandleQueue()
        self.interval_candle_queues[interval].put(candle, replace)

    def put_list(self, interval: str, candles: List[Dict[str, Any]]) -> None:
        if interval not in self.interval_candle_queues:
            self.interval_candle_queues[interval] = CandleQueue()
        self.interval_candle_queues[interval].put_list(candles)

    def get_by_interval(self, interval: str) -> List[Dict[str, Any]]:
        if interval in self.interval_candle_queues:
            return self.interval_candle_queues[interval].get_all()
        return []

    def get_all(self) -> Dict[str, List[Dict[str, Any]]]:
        data = {}
        for k, v in self.interval_candle_queues.items():
            data[k] = v.get_all()
        return data


class CandleManager:
    def __init__(self):
        self.symbol_interval_candle_queues: Dict[str, SymbolIntervalCandleQueue] = {}

    def put(self, symbol: str, interval: str, candle: Dict[str, Any], replace: bool = True) -> None:
        """
        添加一个新的K线数据

        :param symbol: 股票代码
        :param interval: 时间间隔
        :param candle: K线数据
        :param replace: 是否替换已有数据
        """
        if symbol not in self.symbol_interval_candle_queues:
            self.symbol_interval_candle_queues[symbol] = SymbolIntervalCandleQueue(symbol)
        self.symbol_interval_candle_queues[symbol].put(interval, candle, replace)

    def put_list(self, symbol: str, interval: str, candles: List[Dict[str, Any]]) -> None:
        """
        添加多个K线数据

        :param symbol: 股票代码
        :param interval: 时间间隔
        :param candles: K线数据列表
        """
        if symbol not in self.symbol_interval_candle_queues:
            self.symbol_interval_candle_queues[symbol] = SymbolIntervalCandleQueue(symbol)
        self.symbol_interval_candle_queues[symbol].put_list(interval, candles)

    def get_by_symbol_and_interval(self, symbol: str, interval: str, return_type: str = 'list') -> Union[List[Dict[str, Any]], pd.DataFrame]:
        """
        根据股票代码和时间间隔获取K线数据

        :param symbol: 股票代码
        :param interval: 时间间隔
        :param return_type: 返回类型，list或dataframe

        :return: K线数据列表
        """
        if symbol in self.symbol_interval_candle_queues:
            if return_type == 'list':
                return self.symbol_interval_candle_queues[symbol].get_by_interval(interval)
            df = pd.DataFrame(self.symbol_interval_candle_queues[symbol].get_by_interval(interval))
            df = df.set_index('dt')
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            return df
        if return_type == 'list':
            return []
        return pd.DataFrame(columns=['dt', 'open', 'close', 'high', 'low', 'volume'])

    def get_by_symbol(self, symbol: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        根据股票代码获取所有K线数据

        :param symbol: 股票代码
        :return: 所有K线数据的字典
        """
        if symbol in self.symbol_interval_candle_queues:
            return self.symbol_interval_candle_queues[symbol].get_all()
        return {}

    def get_all(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """
        获取所有K线数据

        :return: 所有K线数据的字典
        """
        data = {}
        for symbol, queue in self.symbol_interval_candle_queues.items():
            data[symbol] = queue.get_all()
        return data

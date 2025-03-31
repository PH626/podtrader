import time
from typing import Dict

import pandas as pd
import vectorbt as vbt

from .custom import *
from ..entities import InvestmentT, Investment, Indicator, IndicatorT
from ..enums import IndicatorSourceType

__all__ = ['IndicatorExecutor']


class IndicatorExecutor:
    def __init__(self, pkg: str, func: str, investment: InvestmentT = None, uniqueId: str = None, name: str = None,
                 description: str = None, interval: str = '1d', openStop: bool = False, temporary: bool = False,
                 params: Dict = None):
        """
        指标执行器

        Args:
            pkg: 指标包名
            func: 指标函数名
            investment: 投资设置
            uniqueId: 唯一ID
            name: 名称
            description: 描述
            interval: 周期
            openStop: 是否在开仓后继续执行
            temporary: 是否临时指标
            params: 参数
        """
        if uniqueId is None:
            uniqueId = str(hash(f"{func}{int(time.time() * 1000)}"))
        self.uniqueId = uniqueId
        self.name = name
        self.description = description
        if params is None:
            params = {}
        self.indicator_params = params
        self.apply_func = None
        pkg = IndicatorSourceType(pkg)
        if pkg == IndicatorSourceType.Ta:
            self.F = vbt.ta(func)
        elif pkg == IndicatorSourceType.Talib:
            self.F = vbt.talib(func)
        elif pkg == IndicatorSourceType.PandasTa:
            self.F = vbt.pandas_ta(func)
        else:
            self.F = globals()[func]
        self.interval = interval
        if investment is not None and isinstance(investment, dict):
            investment = Investment.parse_obj(investment)
        self.investment = investment
        self.openStop = openStop
        self.temporary = temporary
        self.input_names = self.F.input_names
        self.param_names = self.F.param_names
        self.output_names = self.F.output_names

    @classmethod
    def from_obj(cls, indicator: IndicatorT):
        """
        从指标实体创建指标执行器
        """
        if isinstance(indicator, dict):
            indicator = Indicator.parse_obj(indicator)
        return cls(
            pkg=indicator.pkg,
            func=indicator.func,
            investment=indicator.investment,
            uniqueId=indicator.uniqueId,
            name=indicator.name,
            description=indicator.description,
            interval=indicator.interval,
            openStop=indicator.openStop,
            temporary=indicator.temporary,
            params=indicator.get_params()
        )

    def _parse_params(self, open=None, high=None, low=None, close=None, volume=None):
        """
        解析参数，将输入参数转换为指标需要的参数，同时将指标参数传递给指标
        :param open:
        :param high:
        :param low:
        :param close:
        :param volume:
        :return:
        """
        params = {}
        # 1. 解析输入参数
        for name in self.input_names:
            if name in ['o', 'open', 'open_', 'Open']:
                params['open'] = open
            elif name in ['h', 'high', 'high_', 'High']:
                params['high'] = high
            elif name in ['l', 'low', 'low_', 'Low']:
                params['low'] = low
            elif name in ['c', 'close', 'close_', 'Close']:
                params['close'] = close
            elif name in ['v', 'volume', 'volume_', 'Volume']:
                params['volume'] = volume
        # 2. 解析指标参数
        for name in self.param_names:
            if name in self.indicator_params:
                params[name] = self.indicator_params[name]
        return params

    def run(self, candles: pd.DataFrame):
        """
        执行指标

        :return:
        """
        params = self._parse_params(
            open=candles['open'],
            high=candles['high'],
            low=candles['low'],
            close=candles['close'],
            volume=candles['volume']
        )
        config = self.F.run(**params)
        results = []
        for name in self.output_names:
            results.append(getattr(config, name))
        results = pd.concat(results, axis=1)
        results.columns = self.output_names
        if self.temporary:
            return results
        return results.iloc[:-1, :]

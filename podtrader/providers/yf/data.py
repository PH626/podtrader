from datetime import timedelta

import numpy as np
import pandas as pd
from vectorbt.data.base import Data
from vectorbt import _typing as tp
import yfinance as yf


class YFData(Data):
    def update_symbol(self, symbol: str, **kwargs):
        download_kwargs = self.select_symbol_kwargs(symbol, self.download_kwargs)
        download_kwargs['start_dt'] = self.data[symbol].index[-1]
        download_kwargs['end_dt'] = download_kwargs['start_dt'] + timedelta(days=2)
        return self.download_symbol(symbol, **kwargs)
    
    @classmethod
    def download_symbol(
            cls,
            symbol: str,
            interval: str = '1d',
            start: tp.Optional[tp.DatetimeLike] = None,
            end: tp.Optional[tp.DatetimeLike] = None,
            **kwargs
    ) -> tp.Frame:
        if end is None:
            end = pd.Timestamp.now()
            end = end.strftime('%Y-%m-%d')
        price = yf.download(symbol, start=start, end=end, interval=interval, ignore_tz=True, progress=False)
        price = price.rename({
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }, axis=1)
        price = price[['open', 'high', 'low', 'close', 'volume']]
        return price

from datetime import datetime
from vectorbt import _typing as tp
import vectorbt as vbt

from .yf import YFData
from .tv import TVData
from .backtest_data_feed import *
from .data_board import CandleManager


def download_historical_data(
        symbol: str,
        sec_type: str = 'stock',
        exchange: str = 'NYSE',
        interval: str = '1d',
        start: tp.Optional[tp.DatetimeLike] = None,
        end: tp.Optional[tp.DatetimeLike] = None,
        datasource: str = 'YF'
):
    import warnings

    warnings.filterwarnings("ignore")
    """Download historical data from the provider."""
    if datasource == 'YF':
        results = YFData.download(
            symbol,
            interval=interval,
            start=start,
            end=end
        )
        price = results.data[symbol]
        price.index = price.index.tz_localize(None)
        return price
    elif datasource == 'TV':
        _interval_mapping = {
            '1d': '1D',
            '4h': '4 hour',
            '1h': '1 hour',
            '15min': '15 minute',
            '5min': '5 minute',
            '1min': '1 minute'
        }
        if start is None:
            start = '2020-01-01'
        start = datetime.strptime(start, '%Y-%m-%d')
        if end is None:
            end = datetime.now()
        else:
            end = datetime.strptime(end, '%Y-%m-%d')
        days = (end - start).days
        if interval == '1d':
            bars = days
        elif interval == '4h':
            bars = days * 6
        elif interval == '1h':
            bars = days * 24
        elif interval == '15min':
            bars = days * 24 * 4
        elif interval == '5min':
            bars = days * 24 * 12
        elif interval == '1min':
            bars = days * 24 * 60
        else:
            raise ValueError('interval must be 1d, 4h, 1h, 15min, 5min')
        data = TVData.download(
            symbol,
            exchange=exchange,
            interval=_interval_mapping[interval],
            limit=bars,
        )
        price = data.data[symbol]
        price = price.rename({
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }, axis=1)
        price.index = price.index.tz_localize(None)
        return price
    else:
        raise ValueError('datasource must be YF or TV')

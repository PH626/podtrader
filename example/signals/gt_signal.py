import numpy as np
import pandas as pd

from podtrader.entities import Investment, Indicator, Signal
from podtrader.indicators import IndicatorExecutor
from podtrader.providers import download_historical_data
from podtrader.signals import SignalExecutor

# Define an investment
investment = Investment(
    symbol='YM1!',
    secType='futures',
    exchange='CBOT',
)

# Download historical data
price = download_historical_data(
    investment.symbol,
    sec_type=investment.secType,
    exchange=investment.exchange,
    interval='1d',
    start='2025-01-01',
    datasource='TV'
)
print(price)

# Define indicators
indicator = Indicator(
    pkg='vector-house',
    func='UUT',
    investment=investment,
)

# Initialize an indicator executor
ind_executor = IndicatorExecutor.from_obj(indicator)
uut = ind_executor.run(
    candles=price,
)

config = {
    'close': price['close'],
    'UUT.C': uut['C'],
    'UUT.T': uut['T'],
    'UUT.R': uut['R'],
    'buy_price': None,
}


# buy signal: close > UUT.T
buy_signal = Signal(
    left='close',
    func='GT',
    right='UUT.T',
)

signal_executor = SignalExecutor.from_obj(buy_signal)
buy = signal_executor.run(config)
print(buy)

buy_price = pd.Series(np.nan, index=price.index)
buy_price[buy] = price['close'][buy]
buy_price = buy_price.ffill()
config['buy_price'] = buy_price

# take profit signal: close > buy_price + 1.8 * UUT.R
take_profit_signal = Signal(
    left='close',
    func='GT',
    right='buy_price + 0.2 * UUT.R',
)

signal_executor = SignalExecutor.from_obj(take_profit_signal)
take_profit = signal_executor.run(config)
print(take_profit[take_profit])

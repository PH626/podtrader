import numpy as np

from podtrader.indicators import IndicatorExecutor
from podtrader.providers import download_historical_data
from podtrader.entities import Investment

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
    interval='1min',
    start='2025-01-01',
    datasource='TV'
)
print(price)

indicator = dict(
    pkg='vector-house',
    func='UUT',
    investment=investment,
)

# Initialize an indicator executor
executor = IndicatorExecutor.from_obj(indicator)
uut = executor.run(
    candles=price,
)
# print(uut)
# 打印不为nan的值
print(uut)


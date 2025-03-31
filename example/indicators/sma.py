from podtrader.indicators import IndicatorExecutor
from podtrader.providers import download_historical_data
from podtrader.entities import Investment

# Define an investment
aapl = Investment(
    symbol='AAPL',
    secType='stock',
    exchange='NASDAQ',
)
# Download historical data
price = download_historical_data(
    aapl.symbol,
    sec_type=aapl.secType,
    exchange=aapl.exchange,
    interval='1d',
    start='2020-01-01',
    datasource='VH'
)
print(price)

indicator = dict(
    pkg='talib',
    func='SMA',
    investment=aapl,
    uniqueId='sma',
    name='SMA',
    description='Simple Moving Average',
    interval='1d',
    params=[
        dict(
            key='timeperiod',
            value=10,
            type='int'
        )
    ]
)

# Initialize an indicator executor
executor = IndicatorExecutor.from_obj(indicator)
sma = executor.run(
    candles=price,
)
print(sma)

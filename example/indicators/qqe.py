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
    datasource='TV'
)
print(price)

indicator = dict(
    pkg='vector-house',
    func='QQE',
    investment=aapl,
    uniqueId='qqe',
    name='QQE',
    description='Quantitative Qualitative Estimation',
    interval='1d',
    params=[
        dict(
            key='rsi_period',
            value=14,
            type='int'
        ),
        dict(
            key='smooth',
            value=5,
            type='int'
        ),
        dict(
            key='factor',
            value=4.238,
            type='float'
        ),
    ]
)

# Initialize an indicator executor
executor = IndicatorExecutor.from_obj(indicator)
res = executor.run(
    candles=price,
)
print(res)

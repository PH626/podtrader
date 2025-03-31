from podtrader.indicators import IndicatorExecutor
from podtrader.providers import download_historical_data
from podtrader.entities import Investment


# Define an investment
investment = Investment(
    symbol='SI1!',
    secType='future',
    exchange='COMEX',
)
# Download historical data
price = download_historical_data(
    investment.symbol,
    sec_type=investment.secType,
    exchange=investment.exchange,
    interval='1d',
    start='2024-01-01',
    datasource='TV'
)
print(price)

indicator = dict(
    pkg='vector-house',
    func='ZIGZAG',
    investment=investment,
)

# Initialize an indicator executor
executor = IndicatorExecutor.from_obj(indicator)
res = executor.run(
    candles=price,
)
print(res)


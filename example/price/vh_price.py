from podtrader.providers import download_historical_data

price = download_historical_data(
    'ES',
    sec_type='stock',
    exchange='NASDAQ',
    interval='1d',
    start='2020-01-01',
    datasource='VH'
)
print(price)

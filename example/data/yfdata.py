from podtrader.providers import download_historical_data


price = download_historical_data(
    'GC1!',
    sec_type='stock',
    exchange='COMEX',
    interval='1d',
    start='2025-01-01',
    datasource='TV'
)
print(price)

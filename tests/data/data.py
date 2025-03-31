from podtrader.providers import download_historical_data

data = download_historical_data(
    'YM1!',
    sec_type='future',
    exchange='CBOT',
    interval='1d',
    start='2025-01-01',
    datasource='TV'
)
print(data)

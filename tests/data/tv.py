from podtrader.providers.tv.data import TVClient


client = TVClient()
df = client.get_hist(
    symbol='AAPL',
    exchange='NASDAQ',
    interval='1D',
    limit=100
)
print(df)

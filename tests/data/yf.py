from podtrader.providers.yf.data import YFData

data = YFData.download(
    'AAPL',
    interval='1d',
    start='2021-01-01',
    end='2021-12-31'
)
print(data.data['AAPL'])

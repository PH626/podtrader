from datetime import datetime

import numpy as np
import pandas as pd
import talib
from dateutil.relativedelta import relativedelta
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

from ..providers import download_historical_data


def create_model(src, degree=2):
    x = np.arange(len(src)).reshape(-1, 1)
    y = src.values
    poly = PolynomialFeatures(degree)
    x_poly = poly.fit_transform(x)
    model = LinearRegression()
    model.fit(x_poly, y)
    return model, poly


def poly_reg(close, benchmark='SPY', interval: str = '1d', degree=1, train_dataset=4, test_dataset=5,
             train_start_time: str = '2015-01-01'):
    """
    Log.diff 和 多项式预测
    :param close:
    :param benchmark:
    :param degree:
    :param train_dataset:
    :param test_dataset:
    :param train_start_time:
    :param interval: 1d, 1h, 15min, 5min, 1min
    :return:
    """
    import warnings

    data_format = '%Y-%m-%d %H:%M:%S'
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    if benchmark is None or benchmark == '':
        log_diff = np.log(close) - np.log(close.shift(1))
    else:
        # 获取benchmark的价格数据
        benchmark_close = download_historical_data(
            symbol=benchmark,
            interval=interval,
            start='2010-01-01',
            datasource='YF'
        )
        benchmark_close = benchmark_close['close']
        combine_close = pd.DataFrame({
            'close': close,
            'benchmark': benchmark_close
        })
        combine_close = combine_close.dropna()
        log_diff = np.log(combine_close['close']) - np.log(combine_close['benchmark'])
    log_diff = log_diff.dropna()
    warnings.filterwarnings("ignore")
    train_data = log_diff[train_start_time:]
    index = train_data.index.tolist()

    model = None
    poly = None
    expired_date = 0
    results = []
    train_start_idx = None
    for idx, dt in enumerate(index):
        dt = datetime(
            year=dt.year,
            month=dt.month,
            day=dt.day,
            hour=dt.hour,
            minute=dt.minute,
            second=dt.second
        )
        test_end_idx = dt.strftime(data_format)
        if expired_date == 0:
            train_start_idx = dt - relativedelta(years=train_dataset)
            test_start_idx = train_start_idx.strftime(data_format)
            y = log_diff.loc[test_start_idx:test_end_idx]
            if y.shape[0] < 100:
                continue
            model, poly = create_model(y.iloc[:-1], degree=degree)
            expired_date = test_dataset
        y = log_diff.loc[train_start_idx:test_end_idx]
        x_poly = poly.fit_transform(np.arange(len(y)).reshape(-1, 1))
        y_pred = model.predict(x_poly)
        dt = dt.strftime(data_format)
        results.append([
            dt,
            y[-1],
            y_pred[-1],
        ])
        expired_date -= 1
    results = pd.DataFrame(results, columns=['dt', 'y', 'y_pred'])
    results['dt'] = pd.to_datetime(results['dt'])
    results = results.set_index('dt')

    combine_result = pd.concat([close, results], axis=1)
    combine_result = combine_result[['y', 'y_pred']]
    return combine_result['y'], combine_result['y_pred']


def zscore(close, benchmark='SPY', interval: str = '1d', degree: int = 1, train_dataset: int = 4,
                 test_dataset: int = 5, cum_days: int = 1, std_days: int = 1, train_start_time: str = '2015-01-01'):
    """
    累计多项式预测 / 标准差
    :param close:
    :param benchmark:
    :param degree:
    :param train_dataset:
    :param test_dataset:
    :param cum_days:
    :param std_days:
    :param train_start_time:
    :param interval: 1d, 1h, 15min, 5min, 1min
    :return:
    """
    y, y_pred = poly_reg(
        close=close,
        benchmark=benchmark,
        degree=degree,
        train_dataset=train_dataset,
        test_dataset=test_dataset,
        train_start_time=train_start_time,
        interval=interval
    )
    results = pd.DataFrame({
        'y': y,
        'y_pred': y_pred
    })
    results['diff'] = results['y'] - results['y_pred']
    if cum_days > 1:
        results['diff'] = talib.SUM(results['diff'].values, cum_days)
    results['std'] = talib.STDDEV(results['diff'].values, std_days)
    results['zscore'] = results['diff'] / results['std']
    return results['zscore']


def qqe_signal(close, rsi_period: int = 14, smooth: int = 5, factor: float = 4.238):
    """
    QQE Signal

    :param close: 价格数据
    :param rsi_period: RSI周期
    :param smooth: 平滑系数
    :param factor: 系数
    :return:
    """
    # Sample price data (replace with your actual price data)
    # Calculate RSI
    close = close.iloc[:, 0]
    wilders_period = rsi_period * 2 - 1

    rsi = talib.RSI(close, rsi_period)
    rsi_ma = talib.EMA(rsi, smooth)
    atr_rsi = abs(rsi_ma.shift(1) - rsi_ma)
    ma_atr_rsi = talib.EMA(atr_rsi, wilders_period)
    dar = talib.EMA(ma_atr_rsi, wilders_period) * factor

    longband = np.zeros_like(close)
    shortband = np.zeros_like(close)
    trend = np.zeros_like(close)

    delta_fast_atr_rsi = dar
    rs_index = rsi_ma.values
    newshortband = rs_index + delta_fast_atr_rsi
    newlongband = rs_index - delta_fast_atr_rsi

    for i in range(2, len(close)):
        longband[i] = max(longband[i - 1], newlongband[i]) if rs_index[i - 1] > longband[i - 1] and rs_index[i] > \
                                                              longband[i - 1] else newlongband[i]
        shortband[i] = min(shortband[i - 1], newshortband[i]) if rs_index[i - 1] < shortband[i - 1] and rs_index[i] < \
                                                                 shortband[i - 1] else newshortband[i]
        if (rs_index[i] > shortband[i - 1] and rs_index[i - 1] < shortband[i - 2]) \
                or (rs_index[i] < shortband[i - 1] and rs_index[i - 1] > shortband[i - 2]):
            trend[i] = 1
        elif (rs_index[i] < longband[i - 1] and rs_index[i - 1] > longband[i - 2]) \
                or (rs_index[i] > longband[i - 1] and rs_index[i - 1] < longband[i - 2]):
            trend[i] = -1
        elif trend[i - 1] != 0:
            trend[i] = trend[i - 1]
        else:
            trend[i] = 1

    fast_atr_rsi_tl = np.where(trend == 1, longband, shortband)

    # Find all the QQE Crosses
    qq_exlong = np.zeros_like(close)
    qq_exshort = np.zeros_like(close)

    for i in range(1, len(close)):
        qq_exlong[i] = qq_exlong[i - 1] + 1 if fast_atr_rsi_tl[i] < rs_index[i] else 0
        qq_exshort[i] = qq_exshort[i - 1] + 1 if fast_atr_rsi_tl[i] > rs_index[i] else 0
    long_entry = qq_exlong == 1
    short_entry = qq_exshort == 1
    signals = np.full(shape=(close.shape[0], 2), fill_value=0)
    signals[long_entry, 0] = 1
    signals[short_entry, 1] = 1
    signals = pd.DataFrame(signals, index=close.index, columns=['long', 'short'])
    return signals['long'], signals['short']

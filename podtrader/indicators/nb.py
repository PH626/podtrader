import math

import numpy as np
from numba import njit

from ..utils import linear_regression, linear_regression_y_value, shift


@njit(cache=True)
def hist_price_low_nb(low: np.ndarray, period: int = 10) -> np.ndarray:
    """
    Calculate the historical low prices for a given period.
    :param low: 1D array of low prices
    :param period: rolling period
    :return: array of historical low prices
    """
    # Ensure the input is flattened
    if low.ndim != 1:
        low = low.flatten()

    n = low.shape[0]  # Get the length of the array
    hist_low = np.empty(n, dtype=np.float64)  # Create an empty array
    hist_low[:] = np.nan  # Fill the array with NaN values

    if period <= 0 or period > n:
        return hist_low

    # Calculate historical lows
    for i in range(period, n):
        hist_low[i] = np.min(low[i - period:i])

    return hist_low


@njit(cache=True)
def hist_price_high_nb(high: np.ndarray, period: int = 10) -> np.array:
    """
    Calculate the historical high prices for a given period.
    :param high: 1D array of high prices
    :param period: rolling period
    :return: array of historical high prices
    """
    # Ensure the input is flattened
    if high.ndim != 1:
        high = high.flatten()

    n = high.shape[0]
    hist_high = np.empty(n, dtype=np.float64)
    hist_high[:] = np.nan

    if period <= 0 or period > n:
        return hist_high

    for i in range(period, n):
        hist_high[i] = np.max(high[i - period:i])

    return hist_high


@njit(cache=True)
def hist_price_cdl_low_nb(open: np.array, close: np.array, period: int = 10) -> np.array:
    """
    Calculate the historical low prices for a given period.
    if open > close, use close, otherwise use open.
    :param open: open prices
    :param close: close prices
    :param period: period
    :return:
    """
    # Determine the candle low prices
    cdl_low = np.where(open > close, close, open)
    return hist_price_low_nb(
        low=cdl_low,
        period=period
    )


@njit(cache=True)
def hist_price_cdl_high_nb(open: np.array, close: np.array, period: int = 10) -> np.array:
    """
    Calculate the historical high prices for a given period.
    if open > close, use open, otherwise use close.
    :param open: open prices
    :param close: close prices
    :param period: period
    :return:
    """
    # Determine the candle high prices
    cdl_high = np.where(open > close, open, close)
    return hist_price_high_nb(
        high=cdl_high,
        period=period
    )


@njit(cache=True)
def zigzag(high: np.array, low: np.array, close: np.array, sigma: float = 0.04) -> np.array:
    """
    Calculate the direction change signal.
    :param high: high prices
    :param low: low prices
    :param close: close prices
    :param sigma: price change thresholds/年吗/
    :return:
    """
    extremes = np.full(high.shape, 0)
    # Last extreme is a bottom. Next is a top
    up_zig = True
    tmp_max = high[0]
    tmp_max_idx = 0

    tmp_min = low[0]
    tmp_min_idx = 0

    for i in range(len(close)):
        # last extreme is a bottom
        if up_zig:
            if high[i] > tmp_max:
                # New high, update
                tmp_max = high[i]
                tmp_max_idx = i
            elif close[i] < tmp_max - tmp_max * sigma:
                # Price retraced by sigma %. Top confirmed, record it
                extremes[tmp_max_idx] = 1
                # Setup for next bottom
                up_zig = False
                tmp_min = low[i]
                tmp_min_idx = i
        # last extreme is a top
        else:
            if low[i] < tmp_min:
                # New low, update
                tmp_min = low[i]
                tmp_min_idx = i
            elif close[i] > tmp_min + tmp_min * sigma:
                # Price retraced by sigma %. Bottom confirmed, record it
                extremes[tmp_min_idx] = -1
                # Setup for next top
                up_zig = True
                tmp_max = high[i]
                tmp_max_idx = i

    if up_zig:
        extremes[tmp_max_idx] = 1
    else:
        extremes[tmp_min_idx] = -1
    return extremes


@njit(cache=True)
def find_peaks_and_valleys(arr: np.array) -> np.array:
    """
    找到数组中的峰值和谷值，数组中的峰值可能会由多个相同的值组成，选择第一个，谷值同理

    Args:
        arr: np.array 一维数组
    """
    n = len(arr)
    res = np.full(n, np.nan)
    direction = 0
    last_idx = -1
    for i in range(1, n):
        if np.isnan(arr[i]) or np.isnan(arr[i - 1]):
            continue
        if last_idx == -1:
            last_idx = i - 1
            res[i - 1] = arr[i - 1]

        if arr[i] > arr[last_idx]:
            if direction == -1:
                res[last_idx] = arr[last_idx]
            direction = 1
            last_idx = i
        elif arr[i] < arr[last_idx]:
            if direction == 1:
                res[last_idx] = arr[last_idx]
            last_idx = i
            direction = -1
    if last_idx != -1:
        res[last_idx] = arr[last_idx]
    return res, direction


@njit(cache=True)
def zigzag2(high: np.array, low: np.array, depth: int = 12, deviation: int = 5, backstep: int = 2, minitick: float = 0.01) -> np.array:
    """
    计算zigzag指标

    Args:
        high: np.array 高价数组
        low: np.array 低价数组
        depth: int, default 12
        deviation: int, default 5
        backstep: int, default 2
        minitick: float, default 0.01

    Returns:
        direction: np.array 信号方向
        peaks: np.array 峰值
        valleys: np.array 谷值
    """
    high = high.flatten()
    low = low.flatten()
    n = len(high)
    # 计算high和low是否满足条件
    high_conditions = np.full(n, 0)
    low_conditions = np.full(n, 0)
    for i in range(depth, n + 1):
        h = np.max(high[i - depth:i])
        l = np.min(low[i - depth:i])
        if i < n:
            high_conditions[i] = 1 if (h - high[i - 1]) <= deviation * minitick else 0
            low_conditions[i] = 1 if (low[i - 1] - l) <= deviation * minitick else 0
    hr = np.full(n, 0)
    lr = np.full(n, 0)

    # 计算high和low上一个等于1的位置到当前位置的距离， 没有等于1的位置则为0
    last_high_index = -1
    last_low_index = -1
    for i in range(n):
        if high_conditions[i] == 1:
            last_high_index = i
        if low_conditions[i] == 1:
            last_low_index = i
        if last_high_index != -1:
            hr[i] = i - last_high_index
        if last_low_index != -1:
            lr[i] = i - last_low_index

    direction = np.full(n, 0)
    last_direction = -1
    for i in range(n):
        if hr[i] <= lr[i]:
            last_direction = i
        if last_direction != -1:
            d = -1 if (i - last_direction) >= backstep else 1
            direction[i] = d

    # 计算z1和z2
    z1 = np.full(n, np.nan)
    z2 = np.full(n, np.nan)
    z = low.copy()
    for i in range(1, n):
        if direction[i] != direction[i - 1]:
            z1[i] = z2[i - 1]
            z2[i] = z[i - 1]
        else:
            z1[i] = z1[i - 1]
            z2[i] = z2[i - 1]

        if direction[i] > 0:
            if high[i] > z2[i]:
                z2[i] = high[i]
                z[i] = low[i]
            if low[i] < z[i]:
                z[i] = low[i]
        elif direction[i] < 0:
            if low[i] < z2[i]:
                z2[i] = low[i]
                z[i] = high[i]
            if high[i] > z[i]:
                z[i] = high[i]

    # 计算z1和z2的的极值点
    z1_new, z1_direction = find_peaks_and_valleys(z1)
    z2_new, z2_direction = find_peaks_and_valleys(z2)
    # ffill nan
    for i in range(n):
        if np.isnan(z1_new[i]):
            z1_new[i] = z1_new[i - 1]
        if np.isnan(z2_new[i]):
            z2_new[i] = z2_new[i - 1]
    if direction[-1] == 1:
        if z1_direction == 1:
            return direction, z1_new, z2_new
        else:
            return direction, z2_new, z1_new
    else:
        if z1_direction == 1:
            return direction, z1_new, z2_new
        else:
            return direction, z2_new, z1_new


@njit(cache=True)
def uut(open: np.array, high: np.array, low: np.array, close: np.array) -> np.array:
    """

    U = close[t] > high[t-1 and close[t] > open[t]
    T形态：下影线很小或者没有，有上影线
    T点：T形态的最高价
    C点：第一个U点之后的第一个K线的最低价

    出现UUT形态，不一定连续，但是股价不能穿上一个U的底部

    :return: [C, T, R]
    """
    open = open.flatten()
    high = high.flatten()
    low = low.flatten()
    close = close.flatten()
    n = len(close)

    # Find U points
    U_points = np.full(n, False)
    T_points = np.full(n, False)
    for t in range(n):
        if close[t] > high[t - 1] and close[t] > open[t]:
            U_points[t] = True
        # Find T points
        cdl = open[t] - close[t]
        if cdl == 0:
            continue
        # 下影线的长度
        low_shadow = (close[t] - low[t]) / cdl
        # 上影线的长度
        high_shadow = high[t] - open[t]
        # T形态：下影线长度很小或者没有，有上影线
        if cdl > 0 and low_shadow < 0.1 and high_shadow > 0:
            T_points[t] = True

    # Find UUT points
    res = np.full((n, 2), np.nan)
    U1 = -1
    U2 = -1
    for t in range(n):
        # Find U1
        if U1 == -1:
            if U_points[t]:
                U1 = t
        # Find U2
        elif U2 == -1:
            if low[t] < low[U1]:
                U1 = -1
                continue
            if U_points[t]:
                U2 = t
        else:
            if low[t] < low[U2]:
                U1 = -1
                U2 = -1
                continue
            if U_points[t]:
                U1 = U2
                U2 = t
                continue
            if T_points[t]:
                res[t, 0] = low[U1 - 1]
                res[t, 1] = high[t]
                U1 = -1
                U2 = -1
    # Fill nan
    for i in range(1, n):
        if np.isnan(res[i, 0]):
            res[i, 0] = res[i - 1, 0]
            res[i, 1] = res[i - 1, 1]
    R = res[:, 1] - res[:, 0]
    return res[:, 0], res[:, 1], R


@njit(cache=True)
def _get_val(start, end, delay, k, b, window_close, upper_deviation, lower_deviation, close, previous_high_delay_bar):
    x_val = np.arange(start, end + delay, 1)
    y_val = linear_regression_y_value(k, b, np.arange(len(x_val)))
    y_val_std = np.std(window_close - y_val[:-delay])
    upper_line_val = y_val + upper_deviation * y_val_std
    lower_line_val = y_val - lower_deviation * y_val_std
    high_val = close[start:end - previous_high_delay_bar].max()
    low_val = close[start:end - previous_high_delay_bar].min()
    return x_val, y_val, y_val_std, upper_line_val, lower_line_val, high_val, low_val


@njit(cache=True)
def linear_regression_channel_breakout(
        close: np.array,
        high: np.array,
        low: np.array,
        regression_time_range: int = 30,
        delay_bar: int = 3,
        upper_deviation: float = 2.5,
        lower_deviation: float = 2.5,
        previous_high_delay_bar: float = 0.3,
        upper_slope: float = 1,
        lower_slope: float = -1,
        pattern_number_code: int = 1,
):
    """
     计算线性回归通道指标。

     参数：
     close (np.ndarray): 收盘价数组，表示历史价格数据。
     pattern_number_code (int): 模式编号，用于标识特定的突破模式：
         1 - 下通道，上突破模式
         2 - 下通道，下突破模式
         3 - 上通道，下突破模式
         4 - 上通道，上突破模式
         5 - 中通道，上突破模式
         6 - 中通道，下突破模式
     regression_time_range (int): 用于计算线性回归通道的历史K线数量，例如30。
     delay_bar (int): 延迟条数，包含<=3个蜡烛检查信号，如果=3，则包含delay=1,2。
     upper_deviation (float): 上线的标准差倍数，例如1.8。
     lower_deviation (float): 下线的标准差倍数，例如1.8。
     previous_high_delay_bar (int): 避免使用最近6个蜡烛的最高点或最低点，在30个K线中排除最后6个蜡烛扫描到的最高或最低点。
     upper_slope (float): 上通道的斜率，用于进一步的分析或调整。
     lower_slope (float): 下通道的斜率，用于进一步的分析或调整。

     返回：
     tuple: 返回上通道和下通道的数组。
    """
    close = (close + high + low) / 3
    close = close.flatten()
    signals = np.full_like(close, False, dtype=np.bool_)  # 初始化信号数组，默认为 False
    x_arr = []
    upper_arr = []
    lower_arr = []
    middle_arr = []
    signal_i = []
    delay_arr = []
    delay_bar_arr = np.arange(1, delay_bar + 1, 1)
    previous_high_delay_bar = round(regression_time_range * previous_high_delay_bar)

    for i in range(len(close)):
        for delay in delay_bar_arr:
            # 跳过前 regression_time_range + delay_bar 个数据点
            if i < regression_time_range + delay:
                continue
            start = i - regression_time_range - delay
            end = i - delay
            window_close = close[start:end]
            # 计算线性回归的斜率 (k) 和截距 (b)
            k, b = linear_regression(window_close)
            # 处理模式 1 和 2
            x_val, y_val, y_val_std, upper_line_val, lower_line_val, high_val, low_val = _get_val(
                start, end,
                delay, k, b,
                window_close,
                upper_deviation,
                lower_deviation,
                close,
                previous_high_delay_bar
            )
            if pattern_number_code == 1 or pattern_number_code == 2:
                if k < lower_slope:
                    # 模式 1: 上突破
                    if pattern_number_code == 1:
                        if close[i] > high_val and close[i] > upper_line_val[-1]:
                            signals[i] = True  # 记录信号为 True
                            x_arr.append(x_val)
                            upper_arr.append(upper_line_val)
                            lower_arr.append(lower_line_val)
                            middle_arr.append(y_val)
                            signal_i.append(i)
                            delay_arr.append(delay)
                            break
                    # 模式 2: 下突破
                    else:
                        if close[i] < lower_line_val[-1]:
                            signals[i] = True  # 记录信号为 True
                            x_arr.append(x_val)
                            upper_arr.append(upper_line_val)
                            lower_arr.append(lower_line_val)
                            middle_arr.append(y_val)
                            signal_i.append(i)
                            delay_arr.append(delay)
                            break
            # 处理模式 3 和 4
            if pattern_number_code == 3 or pattern_number_code == 4:
                # 判断斜率是否在合理范围内
                if k > upper_slope:
                    if pattern_number_code == 3:
                        if close[i] < low_val and close[i] < lower_line_val[-1]:
                            signals[i] = True  # 记录信号为 True
                            x_arr.append(x_val)
                            upper_arr.append(upper_line_val)
                            lower_arr.append(lower_line_val)
                            middle_arr.append(y_val)
                            signal_i.append(i)
                            delay_arr.append(delay)
                            break
                    # 模式 4: 上突破
                    else:
                        if close[i] > upper_line_val[-1]:
                            signals[i] = True  # 记录信号为 True
                            x_arr.append(x_val)
                            upper_arr.append(upper_line_val)
                            lower_arr.append(lower_line_val)
                            middle_arr.append(y_val)
                            signal_i.append(i)
                            delay_arr.append(delay)
                            break
            if pattern_number_code == 5 or pattern_number_code == 6:
                if lower_slope < k < upper_slope:
                    if pattern_number_code == 5:
                        if close[i] > high_val and close[i] > upper_line_val[-1]:
                            signals[i] = True  # 记录信号为 True
                            x_arr.append(x_val)
                            upper_arr.append(upper_line_val)
                            lower_arr.append(lower_line_val)
                            middle_arr.append(y_val)
                            signal_i.append(i)
                            delay_arr.append(delay)
                            break
                    else:
                        if close[i] < low_val and close[i] < lower_line_val[-1]:
                            signals[i] = True  # 记录信号为 True
                            x_arr.append(x_val)
                            upper_arr.append(upper_line_val)
                            lower_arr.append(lower_line_val)
                            middle_arr.append(y_val)
                            signal_i.append(i)
                            delay_arr.append(delay)
                            break
    return signals

import numpy as np
import numba as nb

__all__ = [
    'shift',
    'linear_regression',
    'linear_regression_y_value',
    'myround',
    'moving_sum_np',
    'moving_std_np',
    'clean_signals'
]


@nb.jit(cache=True)
def shift(arr: np.ndarray, n: int) -> np.ndarray:
    """
    Shift the array n steps
    :param arr: array
    :param n: steps
    :return:
    """
    if n == 0:
        return arr
    if n > 0:
        return np.concatenate((np.full(n, np.nan), arr[:-n]))
    else:
        return np.concatenate((arr[-n:], np.full(-n, np.nan)))


@nb.njit(cache=True)
def linear_regression(y: np.ndarray) -> np.ndarray:
    """
    Calculate the linear regression of a series of values
    :param y: np.ndarray
    :return: np.ndarray
    """
    n = len(y)
    x_range = np.arange(n)
    sum_x = np.sum(x_range)
    sum_y = np.sum(y)
    sum_xy = np.sum(x_range * y)
    sum_x_squared = np.sum(x_range * x_range)
    k = (n * sum_xy - sum_x * sum_y) / (n * sum_x_squared - sum_x * sum_x)
    b = (sum_y - k * sum_x) / n
    return np.array([k, b])


@nb.njit(cache=True)
def linear_regression_y_value(k, b, x_values):
    """
    计算给定斜率和截距的直线在多个 x 值下的 y 值
    :param k: 斜率
    :param b: 截距
    :param x_values: 一维数组，表示 x 值
    :return: 一维数组，表示对应的 y 值
    """

    return k * x_values + b


def myround(value, precision: int = 4):
    value = str(value)
    if value.find('.') == -1:
        return value
    int_part, dec_part = value.split('.')
    if len(dec_part) <= precision:
        return value
    return f"{int_part}.{dec_part[:precision]}"


@nb.njit(cache=True)
def moving_sum_np(arr: np.array, window: int = 1):
    """
    Calculate the moving sum of an array
    :param arr: np.array
    :param window: int
    :return: np.array
    """
    n = len(arr)
    if window == 1:
        return arr
    if window >= n:
        return np.full(n, np.sum(arr))
    res = np.full(n, np.nan)
    for i in range(window - 1, n):
        res[i] = np.sum(arr[i - window + 1:i + 1])
    return res


@nb.njit(cache=True)
def moving_std_np(arr: np.array, window: int = 1):
    """
    Calculate the moving standard deviation of an array
    :param arr: np.array
    :param window: int
    :return: np.array
    """
    n = len(arr)
    if window == 1:
        return np.zeros(n)
    if window >= n:
        return np.full(n, np.std(arr))
    res = np.full(n, np.nan)
    for i in range(window - 1, n):
        res[i] = np.std(arr[i - window + 1:i + 1])
    return res


@nb.njit(cache=True)
def clean_signals(signals: np.ndarray) -> np.ndarray:
    """
    Clean the signals
    :param signals: np.ndarray, [entry, exit]
    :return: np.ndarray
    """
    cleaned_signals = np.full(signals.shape, False)
    in_position = False
    for i in range(signals.shape[0]):
        entry = signals[i, 0]
        exit_ = signals[i, 1]

        # 如果没有持仓，且有进场信号，则进场
        if not in_position and entry:
            cleaned_signals[i, 0] = True
            in_position = True

        # 如果有持仓，且有出场信号，则出场
        if in_position and exit_:
            cleaned_signals[i, 1] = True
            in_position = False
    return cleaned_signals

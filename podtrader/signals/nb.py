import numpy as np
from numba import njit


@njit(cache=True)
def dwnbreak_signal_nb(left: np.array, right: np.array, continuous_time: int = 1) -> np.array:
    """
    计算连续几天指标A跌穿指标B
    
    Args:
        left: 指标A
        right: 指标B
    :return:
    """
    left = left.flatten()
    right = right.flatten()
    signals = np.full(shape=left.shape, fill_value=False)
    if left.shape[0] == 0:
        return signals
    for i in range(continuous_time, left.shape[0]):
        flag2 = left[i - continuous_time] > right[i - continuous_time]
        flag1 = np.all(left[i - continuous_time + 1: i + 1] < right[i - continuous_time + 1: i + 1])
        if flag1 and flag2:
            signals[i] = True
    return signals


@njit(cache=True)
def upbreak_signal_nb(left: np.array, right: np.array, continuous_time: int = 1) -> np.array:
    """
    计算连续几天指标A涨穿指标B
    :param left: 指标A
    :param right: 指标B
    :param continuous_time: 连续时间
    :return:
    """
    left = left.flatten()
    right = right.flatten()
    signals = np.full(shape=left.shape, fill_value=False)
    if left.shape[0] == 0:
        return signals
    for i in range(continuous_time, left.shape[0]):
        flag2 = left[i - continuous_time] < right[i - continuous_time]
        flag1 = np.all(left[i - continuous_time + 1: i + 1] > right[i - continuous_time + 1: i + 1])
        if flag1 and flag2:
            signals[i] = True
    return signals


@njit(cache=True)
def equal_signal_nb(left: np.array, right: np.array, continuous_time: int = 1) -> np.array:
    """
    计算连续几天指标A等于指标B
    :param left: 指标A
    :param right: 指标B
    :param continuous_time: 连续时间
    :return:
    """
    left = left.flatten()
    right = right.flatten()
    signals = np.full(shape=left.shape, fill_value=False)
    if left.shape[0] == 0:
        return signals
    for i in range(continuous_time, left.shape[0]):
        if np.all(left[i - continuous_time + 1: i + 1] == right[i - continuous_time + 1: i + 1]):
            signals[i] = True
    return signals


# @njit(cache=True)
def gt_signal_nb(left: np.array, right: np.array, continuous_time: int = 1) -> np.array:
    """
    计算连续几天指标A大于指标B
    :param left: 指标A
    :param right: 指标B
    :param continuous_time: 连续时间
    :return:
    """
    left = left.flatten()
    right = right.flatten()
    signals = np.full(shape=left.shape, fill_value=False)
    if left.shape[0] == 0:
        return signals
    for i in range(continuous_time, left.shape[0] + 1):
        if np.all(left[i - continuous_time: i] > right[i - continuous_time: i]):
            signals[i - 1] = True
    return signals


@njit(cache=True)
def gte_signal_nb(left: np.array, right: np.array, continuous_time: int = 1) -> np.array:
    """
    计算连续几天指标A大于等于指标B
    :param left: 指标A
    :param right: 指标B
    :param continuous_time: 连续时间
    :return:
    """
    left = left.flatten()
    right = right.flatten()
    signals = np.full(shape=left.shape, fill_value=False)
    if left.shape[0] == 0:
        return signals
    for i in range(continuous_time, left.shape[0] + 1):
        if np.all(left[i - continuous_time: i] >= right[i - continuous_time: i]):
            signals[i - 1] = True
    return signals


@njit(cache=True)
def lt_signal_nb(left: np.array, right: np.array, continuous_time: int = 1) -> np.array:
    """
    计算连续几天指标A小于指标B
    :param left: 指标A
    :param right: 指标B
    :param continuous_time: 连续时间
    :return:
    """
    left = left.flatten()
    right = right.flatten()
    signals = np.full(shape=left.shape, fill_value=False)
    if left.shape[0] == 0:
        return signals
    for i in range(continuous_time, left.shape[0] + 1):
        if np.all(left[i - continuous_time: i] < right[i - continuous_time: i]):
            signals[i - 1] = True
    return signals


@njit(cache=True)
def lte_signal_nb(left: np.array, right: np.array, continuous_time: int = 1) -> np.array:
    """
    计算连续几天指标A小于等于指标B
    :param left: 指标A
    :param right: 指标B
    :param continuous_time: 连续时间
    :return:
    """
    left = left.flatten()
    right = right.flatten()
    signals = np.full(shape=left.shape, fill_value=False)
    if left.shape[0] == 0:
        return signals
    for i in range(continuous_time, left.shape[0] + 1):
        if np.all(left[i - continuous_time: i] <= right[i - continuous_time: i]):
            signals[i - 1] = True
    return signals

from datetime import datetime

from dateutil.relativedelta import relativedelta

__all__ = [
    'get_day_aggregated_time'
]


def get_day_aggregated_time(exchange: str, input_time: datetime):
    """
    计算聚合时间

    Args:
        exchange: 交易所
        input_time: 输入时间

    Returns:

    """
    dt = input_time
    if exchange in ['IDEALPRO', 'FX', 'CME', 'CBOT']:
        dt = input_time + relativedelta(hours=7)
    dt = dt.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )
    return dt

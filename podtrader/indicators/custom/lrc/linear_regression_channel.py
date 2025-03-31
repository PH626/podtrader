from vectorbt import IndicatorFactory

from ...nb import linear_regression_channel_breakout

__all__ = ['LRC']

LRC = IndicatorFactory(
    input_names=['close', 'high', 'low'],
    param_names=[
        'regression_time_range',
        'delay_bar',
        'upper_deviation',
        'lower_deviation',
        'previous_high_delay_bar',
        'upper_slope',
        'lower_slope',
        'pattern_number_code'
    ],
    output_names=['signal'],
).from_apply_func(
    linear_regression_channel_breakout,
    regression_time_range=30,
    delay_bar=3,
    upper_deviation=2.5,
    lower_deviation=2.5,
    previous_high_delay_bar=0.3,
    upper_slope=1,
    lower_slope=-1,
    pattern_number_code=1,
)

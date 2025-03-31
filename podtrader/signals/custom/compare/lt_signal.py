from vectorbt import IndicatorFactory

from ...nb import lt_signal_nb

__all__ = ['LT']

LT = IndicatorFactory(
    input_names=['left', 'right'],
    param_names=['continuous_time'],
    output_names=['signal'],
).from_apply_func(
    lt_signal_nb,
    continuous_time=1
)

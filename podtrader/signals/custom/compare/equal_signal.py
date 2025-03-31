from vectorbt import IndicatorFactory

from ...nb import equal_signal_nb

__all__ = ['EQ']

EQ = IndicatorFactory(
    input_names=['left', 'right'],
    param_names=['continuous_time'],
    output_names=['signal'],
).from_apply_func(
    equal_signal_nb,
    continuous_time=1
)

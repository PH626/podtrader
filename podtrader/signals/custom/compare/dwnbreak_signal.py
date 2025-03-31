from vectorbt import IndicatorFactory

from ...nb import dwnbreak_signal_nb

__all__ = ['DWN_BREAK']

DWN_BREAK = IndicatorFactory(
    input_names=['left', 'right'],
    param_names=['continuous_time'],
    output_names=['signal'],
).from_apply_func(
    dwnbreak_signal_nb,
    continuous_time=1
)

from vectorbt import IndicatorFactory

from ...nb import upbreak_signal_nb

__all__ = ['UP_BREAK']

UP_BREAK = IndicatorFactory(
    input_names=['left', 'right'],
    param_names=['continuous_time'],
    output_names=['signal'],
).from_apply_func(
    upbreak_signal_nb,
    continuous_time=1
)

from vectorbt import IndicatorFactory

from ...nb import gte_signal_nb

__all__ = ['GTE']

GTE = IndicatorFactory(
    input_names=['left', 'right'],
    param_names=['continuous_time'],
    output_names=['signal'],
).from_apply_func(
    gte_signal_nb,
    continuous_time=1
)

from vectorbt import IndicatorFactory

from ...nb import lte_signal_nb

__all__ = ['LTE']

LTE = IndicatorFactory(
    input_names=['left', 'right'],
    param_names=['continuous_time'],
    output_names=['signal'],
).from_apply_func(
    lte_signal_nb,
    continuous_time=1
)

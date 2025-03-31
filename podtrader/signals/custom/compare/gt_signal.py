from vectorbt import IndicatorFactory

from ...nb import gt_signal_nb

__all__ = ['GT']

GT = IndicatorFactory(
    input_names=['left', 'right'],
    param_names=['continuous_time'],
    output_names=['signal'],
).from_apply_func(
    gt_signal_nb,
    continuous_time=1
)

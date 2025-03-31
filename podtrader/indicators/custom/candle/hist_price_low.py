from vectorbt import IndicatorFactory

from ...nb import hist_price_low_nb

__all__ = ['HIST_PRICE_LOW']

HIST_PRICE_LOW = IndicatorFactory(
    input_names=["low"],
    param_names=["period"],
    output_names=["hist_low"],
).from_apply_func(
    hist_price_low_nb,
    period=10
)

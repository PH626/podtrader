from vectorbt import IndicatorFactory

from ...nb import hist_price_high_nb

__all__ = ['HIST_PRICE_HIGH']

HIST_PRICE_HIGH = IndicatorFactory(
    input_names=["high"],
    param_names=["period"],
    output_names=["hist_high"],
).from_apply_func(
    hist_price_high_nb,
    period=10
)

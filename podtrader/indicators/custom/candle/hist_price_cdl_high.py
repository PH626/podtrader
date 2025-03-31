from vectorbt import IndicatorFactory

from ...nb import hist_price_cdl_high_nb

__all__ = ['HIST_PRICE_CDL_HIGH']

HIST_PRICE_CDL_HIGH = IndicatorFactory(
    input_names=["open_", "close"],
    param_names=["period"],
    output_names=["hist_price_cdl_high"],
).from_apply_func(
    hist_price_cdl_high_nb,
    period=10
)

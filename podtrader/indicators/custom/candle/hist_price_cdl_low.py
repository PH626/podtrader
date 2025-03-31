from vectorbt import IndicatorFactory
from ...nb import hist_price_cdl_low_nb

__all__ = ['HIST_PRICE_CDL_LOW']

HIST_PRICE_CDL_LOW = IndicatorFactory(
    input_names=["open_", "close"],
    param_names=["period"],
    output_names=["hist_price_cdl_low"],
).from_apply_func(
    hist_price_cdl_low_nb,
    period=10
)

from vectorbt import IndicatorFactory
from ...nb import zigzag2

__all__ = ['ZIGZAG']

ZIGZAG = IndicatorFactory(
    input_names=["high", "low"],
    param_names=["depth", "deviation", "backstep", "minitick"],
    output_names=["trend", "peak", "valley"],
).from_apply_func(
    zigzag2,
    depth=12,
    deviation=5,
    backstep=2,
    minitick=0.01
)

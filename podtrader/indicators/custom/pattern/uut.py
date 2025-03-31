from vectorbt import IndicatorFactory
from ...nb import uut

__all__ = ['UUT']

UUT = IndicatorFactory(
    input_names=["open", "high", "low", "close"],
    param_names=[],
    output_names=["C", "T", "R"],
).from_apply_func(
    uut,
)

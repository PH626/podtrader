from vectorbt import IndicatorFactory
from ...pyc import qqe_signal

__all__ = ['QQE']

QQE = IndicatorFactory(
    input_names=["close"],
    param_names=["rsi_period", "smooth", "factor"],
    output_names=["long", "short"],
).from_apply_func(
    qqe_signal,
    rsi_period=14,
    smooth=5,
    factor=4.238,
    keep_pd=True
)

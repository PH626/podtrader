from vectorbt import IndicatorFactory

from ...pyc import zscore

__all__ = ['ZSCORE']

ZSCORE = IndicatorFactory(
    input_names=['close'],
    param_names=[
        'benchmark',
        'interval',
        'degree',
        'train_dataset',
        'test_dataset',
        'cum_days',
        'std_days',
        'train_start_time',
    ],
    output_names=['zscore']
).from_apply_func(
    zscore,
    benchmark=None,
    interval='1d',
    degree=3,
    train_dataset=4,
    test_dataset=5,
    cum_days=1,
    std_days=252,
    train_start_time='2015-01-01',
    keep_pd=True
)

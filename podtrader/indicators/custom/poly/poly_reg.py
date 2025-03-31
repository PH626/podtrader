from vectorbt import IndicatorFactory

from ...pyc import poly_reg

__all__ = ['POLY_REG']

POLY_REG = IndicatorFactory(
    input_names=['close'],
    param_names=[
        'benchmark',
        'interval',
        'degree',
        'train_dataset',
        'test_dataset',
        'train_start_time',
    ],
    output_names=['log_diff', 'poly_reg']
).from_apply_func(
    poly_reg,
    benchmark=None,
    interval='1d',
    degree=3,
    train_dataset=4,
    test_dataset=5,
    train_start_time='2015-01-01',
    keep_pd=True,
)

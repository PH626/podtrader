from podtrader.backtest_engine import BacktestEngine
from podtrader.entities import *

# 定义投资标的
investment = Investment(
    symbol='YM1!',
    secType='futures',
    exchange='CBOT',
)

# 创建指标
indicators = [
    Indicator(
        uniqueId='QQE',
        name='QQE',
        description='QQE指标',
        interval='1d',
        investment=investment,
        pkg='vector-house',
        func='QQE',
        openStop=False,
        temporary=False,
    ),
    Indicator(
        uniqueId='ADX',
        name='ADX',
        description='ADX指标',
        interval='1d',
        investment=investment,
        pkg='talib',
        func='ADX',
        openStop=False,
        temporary=False,
    )
]

# 创建信号
signals = [
    Signal(
        uniqueId='S1',
        name='',
        description='',
        left='QQE.long',
        func='EQ',
        right='1',
    ),
    Signal(
        uniqueId='S2',
        name='',
        description='',
        left='QQE.short',
        func='EQ',
        right='1',
    ),
    Signal(
        uniqueId='S3',
        name='',
        description='',
        left='ADX.real',
        func='GT',
        right='20',
    )
]

# 创建交易规则
rules = [
    Rule(
        uniqueId='R1',
        name='R1',
        description='R1',
        ruleType=4,
        action=1,
        transactions=[
            CascadeTransaction(expression='S1 & S3', size=100, sizeType=0),
        ]
    ),
    Rule(
        uniqueId='R2',
        name='R2',
        description='R2',
        ruleType=1,
        action=2,
        transactions=[
            CascadeTransaction(expression='S2', size=100, sizeType=0),
        ]
    )
]

# Create Backtest Engine
engine = BacktestEngine(
    init_cash=100000.0,
    commission=0.0,
    slippage=0.0,
    investment=investment,
    start_time='2023-01-01',
    interval='1d',
    datasource='TV',
    indicators=indicators,
    signals=signals,
    rules=rules,
)

# Run Backtest
engine.run()
print(engine.get_total_stats())

from podtrader.backtest_engine import BacktestEngine
from podtrader.entities import *

# Define an investment
investment = Investment(
    symbol='AAPL',
    secType='stock',
    exchange='NASDAQ',
)

# Create Indicator
indicators = [
    Indicator(
        uniqueId='sma10',
        func='SMA',
        pkg='talib',
        interval='1d',
        investment=investment,
        params=[
            Parameter(
                key='timeperiod',
                value=10,
                type='int'
            )
        ]
    ),
    Indicator(
        uniqueId='sma20',
        func='SMA',
        pkg='talib',
        interval='1d',
        investment=investment,
        params=[
            Parameter(
                key='timeperiod',
                value=20,
                type='int'
            )
        ]
    ),
    Indicator(
        uniqueId='qqe',
        func='QQE',
        pkg='vector-house',
        interval='1d',
        investment=investment,
        params=[
            Parameter(
                key='rsi_period',
                value=14,
                type='int'
            ),
            Parameter(
                key='smooth',
                value=5,
                type='int'
            ),
            Parameter(
                key='factor',
                value=4.238,
                type='float'
            ),
        ]
    )
]


# Create Action
actions = [
    Action(
        uniqueId='a1',
        func='GT',
        sourceIndicator='sma10.real',
        targetIndicator='sma20.real',
        params=[
            Parameter(
                key='continuous_time',
                value=1,
                type='int'
            )
        ]
    ),
    Action(
        uniqueId='a2',
        func='EQUAL',
        sourceIndicator='qqe.short',
        targetIndicator='1',
        params=[
            Parameter(
                key='continuous_time',
                value=1,
                type='int'
            )
        ]
    )
]

# Create Rules
rules = [
    Rule(
        uniqueId='r1',
        ruleType=4,
        action=1,
        expression='a1',
        maxFundAllocation=100.0
    ),
    Rule(
        uniqueId='r2',
        ruleType=1,
        action=2,
        expression='a2',
        maxFundAllocation=100.0
    )
]

# Create Backtest Engine
bt_engine = BacktestEngine(
    init_cash=100000.0,
    commission=0.0,
    slippage=0.0,
    investment=investment,
    start_time='2024-01-01',
    interval='1d',
    datasource='VH',
    indicators=indicators,
    actions=actions,
    rules=rules,
)

# Run Backtest
bt_engine.run()

print(bt_engine.get_total_stats())

# 累计收益
# print("Cumulative Return: ")
# print(bt_engine.get_cum_return())
# print("")
#
# # 基准收益
# print("Benchmark Return: ")
# print(bt_engine.get_benchmark_return())
# print("")
#
# # 最大回撤
# print("Max Drawdown: ")
# print(bt_engine.get_max_drawdown())
# print("")
#
# # 年化统计表
# print("Annual Statistics: ")
# print(bt_engine.get_annual_stats())
# print("")
#
# # Summary
# print("Summary: ")
# print(bt_engine.get_summary())
# print("")
#
# # Additional Statistics
# print("Additional Statistics: ")
# print(bt_engine.get_additional_stats())
# print("")
#
# # Total statistics
# print("Total Statistics: ")
# print(bt_engine.get_total_stats())
# print("")
#
# # 订单
# print("Orders: ")
# print(bt_engine.get_orders())
# print("")
#
# bt_engine.plot()

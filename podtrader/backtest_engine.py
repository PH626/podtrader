from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
from dateutil.relativedelta import relativedelta
from typing import List, Dict, Any, Union

from .brokerage.backtest_brokerage import BacktestBrokerage
from .entities import (
    Investment,
    InvestmentT,
    IndicatorListT,
    SignalListT,
    RuleListT
)
from ._typings import intervalT
from .events import BacktestEventEngine, TickEvent, SignalEvent, EventType
from .indicators import IndicatorExecutor
from .providers import BacktestDataFeed, download_historical_data, CandleManager
from .rules import TradeRule
from .signals import SignalExecutor
from .utils import backtest_2d


def _load_price(instrument_target, interval: Union[str, intervalT], start_time: str = None, end_time: str = None,
                datasource: str = 'YF'):
    """
    下载历史数据

    :param instrument_target: 投资标的
    :param interval: 回测频率，可选值：'1d', '1h', '1m'
    :param datasource: 数据源
    :param start_time: 开始时间
    :param end_time: 结束时间
    :return:
    """
    if start_time is None:
        start_time = datetime.now()
        start_time = start_time - relativedelta(years=2)
        start_time = start_time.strftime('%Y-%m-%d')
    data = download_historical_data(
        symbol=instrument_target.symbol,
        sec_type=instrument_target.secType,
        exchange=instrument_target.exchange,
        interval=interval,
        start=start_time,
        end=end_time,
        datasource=datasource
    )
    data.index.name = 'dt'
    return data


class PlotBase:
    def __init__(self):
        self.cum_return: List[List[str, float]] = []
        self.benchmark_return: List[List[str, float]] = []
        self.max_drawdown: List[List[str, float]] = []
        self.annual_stats: List[Dict[str, Any]] = []
        self.month_return: Dict[str, Any] = {}
        self.summary: List[Dict[str, Any]] = []
        self.additional_stats: List[Dict[str, Any]] = []
        self.total_stats: List[Dict[str, Any]] = []
        self.orders: List[Dict[str, Any]] = []
        self.trades: List[Dict[str, Any]] = []

    def parse_bt_result(self, results: Dict[str, Any]):
        # 根据类的属性名，将结果中的数据解析到类的属性中
        for key, value in results.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self

    def get_cum_return(self):
        cum_ret = pd.DataFrame(self.cum_return, columns=['date', 'cum_return'])
        cum_ret['date'] = pd.to_datetime(cum_ret['date'])
        cum_ret = cum_ret.set_index('date')
        return cum_ret

    def plot_cum_return(self):
        cum_ret = self.get_cum_return()
        cum_ret.plot()
        plt.show()

    def get_benchmark_return(self):
        benchmark_ret = pd.DataFrame(self.benchmark_return, columns=['date', 'benchmark_return'])
        benchmark_ret['date'] = pd.to_datetime(benchmark_ret['date'])
        benchmark_ret = benchmark_ret.set_index('date')
        return benchmark_ret

    def plot_benchmark_return(self):
        benchmark_ret = self.get_benchmark_return()
        benchmark_ret.plot()
        plt.show()

    def get_max_drawdown(self):
        max_drawdown = pd.DataFrame(self.max_drawdown, columns=['date', 'drawdown'])
        max_drawdown['date'] = pd.to_datetime(max_drawdown['date'])
        max_drawdown = max_drawdown.set_index('date')
        return max_drawdown

    def plot_max_drawdown(self):
        drawdown = self.get_max_drawdown()
        drawdown.plot()
        plt.show()

    def get_annual_stats(self):
        return pd.DataFrame(self.annual_stats)

    def get_month_return(self):
        return self.month_return

    def get_summary(self):
        return pd.DataFrame(self.summary)

    def get_additional_stats(self):
        return pd.DataFrame(self.additional_stats)

    def get_total_stats(self):
        return pd.DataFrame(self.total_stats)

    def get_orders(self):
        return pd.DataFrame(self.orders)

    def get_trades(self):
        return pd.DataFrame(self.trades)

    def results(self):
        return {
            "cumReturn": self.cum_return,
            "benchmarkReturn": self.benchmark_return,
            "maxDrawdown": self.max_drawdown,
            "annualStats": self.annual_stats,
            "monthReturn": self.month_return,
            "summary": self.summary,
            "additionalStats": self.additional_stats,
            "totalStats": self.total_stats,
            "orders": self.orders,
            "trades": self.trades,
        }

    def plot(self):
        """
        绘制回测结果
        """
        fig, ax = plt.subplots(2, 1, figsize=(12, 8))
        cum_ret = self.get_cum_return()
        benchmark_ret = self.get_benchmark_return()

        cum_ret.plot(ax=ax[0])
        benchmark_ret.plot(ax=ax[0])

        drawdown = self.get_max_drawdown()
        drawdown.plot(ax=ax[1])

        plt.show()


class RunningConfig:
    def __init__(self, config: List[Dict[str, Any]] = None):
        # 自定义参数
        if config is None:
            config = []
        self.config = config

        # 默认数据
        self.current_time: datetime = None
        self.open: float = None
        self.high: float = None
        self.low: float = None
        self.close: float = None
        self.volume: int = None

        self.last_buy_time: Union[str, datetime] = None
        self.last_buy_price: float = None
        self.buy_time: Union[str, datetime] = None
        self.buy_price: float = None

        self.last_sell_time: Union[str, datetime] = None
        self.last_sell_price: float = None
        self.sell_time: Union[str, datetime] = None
        self.sell_price: float = None

        self.position: int = 0
        self.cash: float = 0.0

    def update(self, key: str, value: Any):
        if hasattr(self, key):
            setattr(self, key, value)

    def update_all(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                if key == 'buy_price':
                    self.last_buy_price = self.buy_price
                elif key == 'buy_time':
                    self.last_buy_time = self.buy_time
                elif key == 'sell_price':
                    self.last_sell_price = self.sell_price
                elif key == 'sell_time':
                    self.last_sell_time = self.sell_time
                setattr(self, key, value)

    def get_params(self):
        params = {
            'dt': self.current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
            'last_buy_time': self.last_buy_time,
            'last_buy_price': self.last_buy_price,
            'buy_time': self.buy_time,
            'buy_price': self.buy_price,
            'last_sell_time': self.last_sell_time,
            'last_sell_price': self.last_sell_price,
            'sell_time': self.sell_time,
            'sell_price': self.sell_price,
            'position': self.position,
            'cash': self.cash
        }
        return params


class BacktestEngine(PlotBase):
    def __init__(self, init_cash: float = 10000.0, commission: float = 0.0, slippage: float = 0.0,
                 investment: InvestmentT = None, start_time: str = '2015-01-01', end_time: str = None,
                 interval: Union[str, intervalT] = '1d', datasource: str = 'TV', indicators: IndicatorListT = None,
                 signals: SignalListT = None, rules: RuleListT = None, runConfig: List[Dict[str, Any]] = None):
        """
        回测引擎

        Args:
            init_cash: 初始资金
            commission: 佣金
            slippage: 滑点
            investment: 投资标的
            start_time: 回测开始时间
            end_time: 回测结束时间
            interval: 回测频率
            datasource: 数据源
            indicators: 指标
            rules: 交易规则
            runConfig: 运行参数
        """
        super(BacktestEngine, self).__init__()
        self.init_cash = init_cash
        self.commission = commission
        self.slippage = slippage
        if isinstance(investment, dict):
            investment = Investment.parse_obj(investment)
        self.instrument_target = investment
        self.start_time = start_time
        self.start_calculate_time = datetime.strptime(start_time, '%Y-%m-%d')
        self.end_time = end_time
        self.interval = interval
        self.datasource = datasource

        # 运行参数
        self.run_config = RunningConfig(config=runConfig)

        # 指标
        self.indicators = []
        if indicators is not None:
            for ind in indicators:
                self.indicators.append(IndicatorExecutor.from_obj(ind))

        # 交易动作
        self.signals = []
        if signals is not None:
            for signal in signals:
                self.signals.append(SignalExecutor.from_obj(signal))

        # 交易规则
        self.rules = []
        if rules is not None:
            for rule in rules:
                self.rules.append(TradeRule.from_rule(rule))

        # 初始化回测经纪商
        self._backtest_brokerage = BacktestBrokerage(init_cash=init_cash)
        # 历史数据
        self.symbol_interval_candles = {}
        self._candle_manager = CandleManager()
        # 交易日历
        self._data_feed: BacktestDataFeed = BacktestDataFeed()
        # 事件队列
        self._events_engine = BacktestEventEngine(self._data_feed)

    def _init_historical_data(self):
        """
        加载数据
        """
        # self.logger.info(f"开始加载数据...")
        # self.logger.info("-" * 20)
        symbol_intervals = {}

        for ind in self.indicators:
            symbol = ind.investment.__str__()
            if symbol not in symbol_intervals:
                symbol_intervals[symbol] = {
                    'investment': ind.investment,
                    'intervals': {ind.interval}
                }
            else:
                symbol_intervals[symbol]['intervals'].add(ind.interval)

        for symbol, item in symbol_intervals.items():
            investment = item['investment']
            intervals = item['intervals']
            self.symbol_interval_candles[symbol] = {}
            for interval in intervals:
                data = _load_price(
                    instrument_target=investment,
                    interval=interval,
                    start_time=self.start_time,
                    end_time=self.end_time,
                    datasource=self.datasource
                )
                self.symbol_interval_candles[symbol][interval] = data
                # self.logger.info(f"{symbol} [{interval}] 初始化完成：{len(data)} 条数据")
        # self.logger.info(f"数据加载完成！")
        # self.logger.info("-" * 20)

    def _init_data_feed(self):
        """
        初始化交易日历
        """
        # self.logger.info(f"初始化交易日历...")
        # self.logger.info("-" * 20)
        data = _load_price(
            instrument_target=self.instrument_target,
            interval=self.interval,
            start_time=self.start_time,
            end_time=self.end_time,
            datasource=self.datasource
        )
        self._data_feed.set_data_source(data)
        # self.logger.info(f"交易日历初始化完成：{len(data)} 条数据")
        # self.logger.info("-" * 20)

    def _set_up(self):
        """
        初始化回测引擎
        1. 下载数据；
        2. 初始化交易日历；
        3. 注册事件处理器；
        """
        # self.logger.info(f'初始化回测引擎...')
        # self.logger.info(f"初始资金：{self.init_cash}")
        # self.logger.info(f"佣金：{self.commission}")
        # self.logger.info(f"滑点：{self.slippage}")
        # self.logger.info(f"回测标的：{self.instrument_target.symbol}")
        # self.logger.info(f"回测频率：{self.interval}")
        # self.logger.info(f"回测数据源：{self.datasource}")
        # self.logger.info(f"回测时间：{self.start_time} - {self.end_time}")

        # 下载数据
        self._init_historical_data()
        # 初始化交易日历
        self._init_data_feed()
        # 注册事件处理器
        self._events_engine.register_handler(
            EventType.TICK,
            self._tick_event_handler
        )
        self._events_engine.register_handler(
            EventType.SIGNAL,
            self._strategy_event_handler
        )
        # self.logger.info(f'回测引擎初始化完成！')

    def _tick_event_handler(self, tick_event: TickEvent) -> None:
        """
        处理TickEvent
        1. 更新当前时间
        2. 聚合不同频率的数据

        :param tick_event:
        :return:
        """
        try:
            self._current_time = tick_event.timestamp
            # 聚合不同频率的数据
            for symbol, interval_candle in self.symbol_interval_candles.items():
                for interval, candles in interval_candle.items():
                    tmp_data = candles.loc[:self._current_time]
                    if len(tmp_data) < 2:
                        continue
                    tmp_data = tmp_data.iloc[-2:].reset_index().to_dict(orient='records')
                    # 添加倒数第二根K线的目的是为保证频率数据的完整性
                    self._candle_manager.put(
                        symbol=symbol,
                        interval=interval,
                        candle=tmp_data[-2],
                        replace=True
                    )
                    tick_bar = {
                        'dt': tmp_data[-1]['dt'],
                        'open': tick_event.open,
                        'high': tick_event.high,
                        'low': tick_event.low,
                        'close': tick_event.close,
                        'volume': tick_event.volume
                    }
                    # 使用最新的tick数据更新K线数据，如果存在相同时间的K线数据，回自动聚合
                    self._candle_manager.put(
                        symbol=symbol,
                        interval=interval,
                        candle=tick_bar,
                        replace=False
                    )

            if self._current_time < self.start_calculate_time:
                return

            # 更新运行参数
            bar = {
                'current_time': self._current_time,
                'open': tick_event.open,
                'high': tick_event.high,
                'low': tick_event.low,
                'close': tick_event.close,
                'volume': tick_event.volume
            }
            self.run_config.update_all(**bar)
            run_config = self.run_config.get_params()
            # 计算指标
            for ind in self.indicators:
                # 如果设置开仓后不再计算指标，则跳过
                if ind.openStop and self.run_config.position > 0:
                    continue
                candles = self._candle_manager.get_by_symbol_and_interval(
                    symbol=ind.investment.__str__(),
                    interval=ind.interval,
                    return_type='df'
                )
                if candles is None or len(candles) < 2:
                    continue
                res = ind.run(candles)
                if res is None:
                    continue
                for column, series in res.items():
                    key = f"{ind.uniqueId}.{column}"
                    run_config[key] = series

            # 计算动作
            for signal in self.signals:
                res = signal.run(run_config).iloc[-1]
                run_config[signal.uniqueId] = res

            # 计算规则
            events = []
            for rule in self.rules:
                event = rule.run(run_config)
                if event is not None:
                    events.append(event)
            # 根据优先级从小到大排序
            events = sorted(events, key=lambda x: x.priority)
            for event in events:
                self._events_engine.put(event)
        except Exception as e:
            pass
            # self.logger.error(f"处理TickEvent时发生异常：{e}")

    def _strategy_event_handler(self, event: SignalEvent) -> None:
        """
        处理策略事件
        """
        res = self._backtest_brokerage.place_order(event)
        if res is None:
            return
        self.run_config.update_all(**res)

    def set_investment(self, investment: InvestmentT):
        """
        设置回测标的
        :param investment:
        :return:
        """
        if isinstance(investment, dict):
            investment = Investment.parse_obj(investment)
        self.instrument_target = investment
        # self.logger.info(f'Investment set to {self.instrument_target.symbol}!')

    def start_backtest(self, signals):
        main_candles = _load_price(
            instrument_target=self.instrument_target,
            interval=self.interval,
            start_time=self.start_time,
            end_time=self.end_time,
            datasource=self.datasource
        )
        if main_candles is None:
            # self.logger.error('No historical data found!')
            return

        main_candles['long_entry'] = False
        main_candles['short_entry'] = False
        main_candles['long_exit'] = False
        main_candles['short_exit'] = False
        main_candles['size'] = 0

        main_candles.loc[signals.index, 'long_entry'] = signals['long_entry']
        main_candles.loc[signals.index, 'short_entry'] = signals['short_entry']
        main_candles.loc[signals.index, 'long_exit'] = signals['long_exit']
        main_candles.loc[signals.index, 'short_exit'] = signals['short_exit']
        main_candles.loc[signals.index, 'size'] = signals['size']

        if self.end_time is None or self.end_time == '':
            main_candles = main_candles.loc[self.start_time:]
        else:
            main_candles = main_candles.loc[self.start_time:self.end_time]

        res = backtest_2d(
            main_candles,
            commission=self.commission,
            slippage=self.slippage,
            init_cash=self.init_cash,
            freq=self.interval
        )
        self.parse_bt_result(res)

    def run(self, backtest: bool = True):
        self._set_up()
        self._events_engine.run()
        signals = self._backtest_brokerage.get_signals()
        # self.logger.info(f"Strategy execution completed!")
        if backtest:
            self.start_backtest(signals)
        return signals

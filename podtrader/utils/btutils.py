import math
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
import vectorbt as vbt
import warnings

from ..utils import myround

warnings.filterwarnings("ignore")

__all__ = ['backtest_2d']


def cum_ret_cal(pf: Any, use_first_order: bool = False, benchmark_asset: str = None):
    """
    累计收益 + 基准收益

    :param pf: Portfolio
    :param use_first_order: bool 是否从第一笔订单开始计算
    :param benchmark_asset: str 基准资产
    """
    cum_ret = pf.get_cumulative_returns()
    if benchmark_asset is None:
        close = pf.close
    else:
        close = None
    if use_first_order:
        if not pf.orders.records_readable.empty:
            signal_idx = pf.orders.records_readable['Signal Timestamp'].iloc[0]
            cum_ret = cum_ret.loc[signal_idx:]
            close = close.loc[signal_idx:]
    init_close = close.iloc[0]
    benchmark_ret = (close - init_close) / init_close + 1
    cum_ret.index = cum_ret.index.astype(str)
    benchmark_ret.index = benchmark_ret.index.astype(str)
    cum_ret = cum_ret.reset_index().values.tolist()
    benchmark_ret = benchmark_ret.reset_index().values.tolist()
    return cum_ret, benchmark_ret


def max_drawdown_cal(pf: Any):
    """
    最大回撤
    """
    drawdown = pf.drawdown
    drawdown.index = drawdown.index.astype(str)
    drawdown = drawdown.abs() * 100
    drawdown = drawdown.reset_index().values.tolist()
    return drawdown


def monthly_returns_cal(pf: Any) -> dict:
    """
    月度收益
    """
    returns = pf.returns
    monthly_returns = returns.copy()
    monthly_returns = monthly_returns.reset_index()
    monthly_returns.columns = ['date', 'return']
    monthly_returns['date'] = pd.to_datetime(monthly_returns['date'])
    monthly_returns['year'] = monthly_returns['date'].dt.year
    monthly_returns['month'] = monthly_returns['date'].dt.month

    heatmap = []
    xaxis = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    yaxis = []
    y = -1
    for year, group in monthly_returns.groupby('year'):
        y = y + 1
        yaxis.append(str(year))
        m = -1
        for month in range(1, 13):
            m = m + 1
            month_return = group[group['month'] == month]
            if month_return.empty:
                heatmap.append([m, y, '-'])
            else:
                cum_month_return = month_return['return'].sum() * 100
                cum_month_return = round(cum_month_return, 2)
                if math.isnan(cum_month_return) or cum_month_return == 0.0:
                    heatmap.append([m, y, '-'])
                else:
                    heatmap.append([m, y, round(cum_month_return, 2)])
    month_return_heatmap = {
        'xAxis': xaxis,
        'yAxis': yaxis,
        'heatmap': heatmap
    }
    return month_return_heatmap


def annual_stats_cal(first_year, pf: Any):
    """
    年化统计
    """
    orders = pf.orders.records_readable
    orders = orders.set_index('Signal Index')
    orders.index = pd.to_datetime(orders.index)
    trades = pf.get_trades().records_readable
    trades = trades.set_index('Exit Index')
    trades.index = pd.to_datetime(trades.index)
    position_mark = pf.position_mask
    drawdown = pf.drawdown
    now_year = datetime.now().year
    results = []
    exist_trade_years = trades.index.year.tolist()
    exist_order_years = orders.index.year.tolist()
    for y in range(first_year, now_year + 1, 1):
        str_year = str(y)
        year_positions = position_mark.loc[str_year]
        position_coverage = year_positions[year_positions == True].shape[0] / year_positions.shape[0] * 100
        position_coverage = round(position_coverage, 4)
        year_drawdown = drawdown.loc[str_year]
        max_drwadown = np.abs(year_drawdown.min()) * 100
        max_drwadown = round(max_drwadown, 4)
        if y in exist_trade_years:
            year_trades = trades.loc[str_year]
        else:
            year_trades = pd.DataFrame()
        if y in exist_order_years:
            year_orders = orders.loc[str_year]
        else:
            year_orders = pd.DataFrame()
        year_benchmark = pf.bm_returns.loc[str_year]
        if year_trades.empty:
            total_return = ''
            best_trade = ''
            worst_trade = ''
            avg_winning_trade = ''
            avg_losing_trade = ''
        else:
            total_return = year_trades['PnL'].sum() / 100
            total_return = round(total_return, 4)
            best_trade = year_trades['Return'].max() * 100
            best_trade = round(best_trade, 4)
            worst_trade = year_trades['Return'].min() * 100
            worst_trade = round(worst_trade, 4)
            avg_winning_trade = year_trades[year_trades['PnL'] > 0]['Return'].mean() * 100
            if math.isnan(avg_winning_trade):
                avg_winning_trade = ''
            else:
                avg_winning_trade = round(avg_winning_trade, 4)
            avg_losing_trade = year_trades[year_trades['PnL'] < 0]['Return'].mean() * 100
            if math.isnan(avg_losing_trade):
                avg_losing_trade = ''
            else:
                avg_losing_trade = round(avg_losing_trade, 4)
        benchmark_return = year_benchmark.vbt.returns.total() * 100
        benchmark_return = round(benchmark_return, 4)
        item = {
            'year': y,
            'position_coverage': position_coverage,
            'total_return': total_return,
            'benchmark_return': benchmark_return,
            'max_drawdown': max_drwadown,
            'total_orders': year_orders.shape[0],
            'total_trades': year_trades.shape[0],
            'best_trade': best_trade,
            'worst_trade': worst_trade,
            'avg_winning_trade': avg_winning_trade,
            'avg_losing_trade': avg_losing_trade,
        }
        results.append(item)
    return results


def parse_orders(pf: Any):
    """
    解析订单
    """
    orders = pf.orders.records_readable
    trades = pf.trades.records_readable
    orders = orders[['Order Id', 'Timestamp', 'Size', 'Price', 'Fees', 'Side']]
    orders.columns = ['order_id', 'signal_index', 'size', 'price', 'fees', 'side']
    orders['price'] = orders['price'].round(4)
    orders['fees'] = orders['fees'].round(4)
    orders['size'] = orders['size'].round(4)
    orders = orders.to_dict(orient='records')

    trades_copy = trades.copy()
    trades_copy = trades_copy.rename(
        columns={
            'Size': 'size',
            'Entry Timestamp': 'entry_index',
            'Avg Entry Price': 'avg_entry_price',
            'Entry Fees': 'entry_fees',
            'Exit Timestamp': 'exit_index',
            'Avg Exit Price': 'avg_exit_price',
            'Exit Fees': 'exit_fees',
            'PnL': 'pnl',
            'Return': 'return',
            'Direction': 'direction',
            'Status': 'status'
        },
    )
    columns = [
        'size',
        'entry_index',
        'avg_entry_price',
        'entry_fees',
        'exit_index',
        'avg_exit_price',
        'exit_fees',
        'pnl',
        'return',
        'direction',
        'status'
    ]
    trades_copy = trades_copy[columns]
    trades_copy['size'] = trades_copy['size'].round(4)
    trades_copy['entry_index'] = trades_copy['entry_index'].astype(str)
    trades_copy['exit_index'] = trades_copy['exit_index'].astype(str)
    trades_copy['avg_entry_price'] = trades_copy['avg_entry_price'].round(4)
    trades_copy['entry_fees'] = trades_copy['entry_fees'].round(4)
    trades_copy['avg_exit_price'] = trades_copy['avg_exit_price'].round(4)
    trades_copy['exit_fees'] = trades_copy['exit_fees'].round(4)
    trades_copy['pnl'] = trades_copy['pnl'].round(4)
    trades_copy['return'] = trades_copy['return'].round(4)
    trades_copy['status'] = trades_copy['status'].astype(str)
    trades_copy = trades_copy.to_dict(orient='records')

    trades = trades.set_index('Exit Timestamp')
    if not trades.empty:
        if trades['Status'].iloc[-1] == 'Open':
            # ['order_id', 'signal_index', 'size', 'price', 'fees', 'side']
            abstract_order = {
                'order_id': len(orders),
                'signal_index': trades.index[-1],
                'size': trades['Size'].iloc[-1],
                'price': trades['Avg Exit Price'].iloc[-1],
                'fees': trades['Exit Fees'].iloc[-1],
                'side': trades['Direction'].iloc[-1]
            }
            orders.append(abstract_order)
        exit_dict = {}
        for index, row in trades.iterrows():
            exit_dict[index] = row.to_dict()

        orders = pd.DataFrame(orders)
        orders['PnL'] = orders['signal_index'].apply(
            lambda x: exit_dict[x].get('PnL', None) if x in exit_dict else None)
        orders['Return'] = orders['signal_index'].apply(
            lambda x: exit_dict[x].get('Return', None) if x in exit_dict else None)
        orders['Direction'] = orders['signal_index'].apply(
            lambda x: exit_dict[x].get('Direction', None) if x in exit_dict else None)
        if 'PnL' not in orders.columns:
            orders['PnL'] = 0.0
        orders['PnL'] = orders['PnL'].fillna(0.0)
        if 'Return' not in orders.columns:
            orders['Return'] = 0.0
        orders['Return'] = orders['Return'].fillna(0.0)
        orders['signal_index'] = orders['signal_index'].astype(str)
    else:
        orders['PnL'] = 0.0
        orders['Return'] = 0.0
        orders['Direction'] = None

    return orders, trades_copy


def parse_stats(bt_data):
    bt_data = bt_data.replace(np.nan, None)
    bt_data = bt_data.replace(np.inf, None)
    bt_data = bt_data.to_dict()
    # 保留6位小数
    stats = {}
    for k, v in bt_data.items():
        if isinstance(v, pd.Timestamp):
            value = v.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(v, float):
            value = round(v, 6)
        elif isinstance(v, pd.Timedelta):
            value = str(v)
        elif v is None or math.isnan(v):
            value = None
        else:
            value = float(v)
        stats[k] = value
    return stats


def stats_cal(pf: Any, orders: pd.DataFrame, init_cash: float, freq: str = '1d'):
    stats = parse_stats(pf.stats().transpose())
    summary = pd.DataFrame(
        columns=['Long', 'Short', 'Total'],
        index=['Trades', 'Wins', 'Losses', 'P&L', '% P&L']
    )
    additional_stats = pd.DataFrame(
        columns=['Long', 'Short', 'Total'],
        index=['Avg P&L', 'Total Wins', 'Total Losses', 'Avg Win', 'Avg Loss', 'Max Win', 'Max Loss']
    )
    # Long
    long_orders = orders[orders['Direction'] == 'Long']
    summary.loc['Trades', 'Long'] = long_orders.shape[0]
    summary.loc['Wins', 'Long'] = long_orders[long_orders['PnL'] > 0].shape[0]
    summary.loc['Losses', 'Long'] = long_orders[long_orders['PnL'] < 0].shape[0]
    summary.loc['P&L', 'Long'] = long_orders['PnL'].sum()
    summary.loc['% P&L', 'Long'] = long_orders['PnL'].sum() / init_cash * 100
    additional_stats.loc['Avg P&L', 'Long'] = long_orders['PnL'].sum() / summary.loc['Trades', 'Long']
    additional_stats.loc['Total Wins', 'Long'] = long_orders[long_orders['PnL'] > 0]['PnL'].sum()
    additional_stats.loc['Total Losses', 'Long'] = long_orders[long_orders['PnL'] < 0]['PnL'].sum()
    additional_stats.loc['Avg Win', 'Long'] = long_orders[long_orders['PnL'] > 0]['PnL'].mean()
    additional_stats.loc['Avg Loss', 'Long'] = long_orders[long_orders['PnL'] < 0]['PnL'].mean()
    additional_stats.loc['Max Win', 'Long'] = long_orders[long_orders['PnL'] > 0]['PnL'].max()
    additional_stats.loc['Max Loss', 'Long'] = long_orders[long_orders['PnL'] < 0]['PnL'].min()

    # Short
    short_orders = orders[orders['Direction'] == 'Short']
    summary.loc['Trades', 'Short'] = short_orders.shape[0]
    summary.loc['Wins', 'Short'] = short_orders[short_orders['PnL'] > 0].shape[0]
    summary.loc['Losses', 'Short'] = short_orders[short_orders['PnL'] < 0].shape[0]
    summary.loc['P&L', 'Short'] = short_orders['PnL'].sum()
    summary.loc['% P&L', 'Short'] = short_orders['PnL'].sum() / init_cash * 100
    additional_stats.loc['Avg P&L', 'Short'] = short_orders['PnL'].sum() / summary.loc['Trades', 'Short']
    additional_stats.loc['Total Wins', 'Short'] = short_orders[short_orders['PnL'] > 0]['PnL'].sum()
    additional_stats.loc['Total Losses', 'Short'] = short_orders[short_orders['PnL'] < 0]['PnL'].sum()
    additional_stats.loc['Avg Win', 'Short'] = short_orders[short_orders['PnL'] > 0]['PnL'].mean()
    additional_stats.loc['Avg Loss', 'Short'] = short_orders[short_orders['PnL'] < 0]['PnL'].mean()
    additional_stats.loc['Max Win', 'Short'] = short_orders[short_orders['PnL'] > 0]['PnL'].max()
    additional_stats.loc['Max Loss', 'Short'] = short_orders[short_orders['PnL'] < 0]['PnL'].min()

    # Total
    summary.loc['Trades', 'Total'] = stats['Total Trades']
    summary.loc['Wins', 'Total'] = orders[orders['PnL'] > 0].shape[0]
    summary.loc['Losses', 'Total'] = orders[orders['PnL'] < 0].shape[0]
    summary.loc['P&L', 'Total'] = orders['PnL'].sum()
    summary.loc['% P&L', 'Total'] = stats['Total Return [%]']
    if stats['Total Trades'] == 0:
        stats['Total Trades'] = 1
    additional_stats.loc['Avg P&L', 'Total'] = orders['PnL'].sum() / stats['Total Trades']
    additional_stats.loc['Total Wins', 'Total'] = orders[orders['PnL'] > 0]['PnL'].sum()
    additional_stats.loc['Total Losses', 'Total'] = orders[orders['PnL'] < 0]['PnL'].sum()
    additional_stats.loc['Avg Win', 'Total'] = orders[orders['PnL'] > 0]['PnL'].mean()
    additional_stats.loc['Avg Loss', 'Total'] = orders[orders['PnL'] < 0]['PnL'].mean()
    additional_stats.loc['Max Win', 'Total'] = orders[orders['PnL'] > 0]['PnL'].max()
    additional_stats.loc['Max Loss', 'Total'] = orders[orders['PnL'] < 0]['PnL'].min()

    summary = summary.fillna(0.0)
    additional_stats = additional_stats.fillna(0.0)

    summary = summary.applymap(myround)
    summary = summary.reset_index()
    summary.columns = ['name', 'long', 'short', 'total']
    summary = summary.to_dict(orient='records')

    additional_stats = additional_stats.applymap(myround)
    additional_stats = additional_stats.reset_index()
    additional_stats.columns = ['name', 'long', 'short', 'total']
    additional_stats = additional_stats.to_dict(orient='records')

    # sharpe_ratio = sharpe_ratio_cal(pf.returns)
    # sortino_ratio = sortino_ratio_cal(pf.returns)
    total_stats = pf.stats().transpose()
    # total_stats['Sharpe Ratio'] = sharpe_ratio
    # total_stats['Sortino Ratio'] = sortino_ratio
    total_stats = total_stats.apply(myround)
    total_stats = total_stats.reset_index()
    total_stats.columns = ['name', 'value']
    total_stats = total_stats.to_dict(orient='records')
    return summary, additional_stats, total_stats


def sharpe_ratio_cal(returns, risk_free_rate=0.05, freq='1d'):
    # 计算年化收益率
    annualized_return = np.mean(returns) * 252  # 假设一年有252个交易日
    # 计算年化波动率
    annualized_volatility = np.std(returns) * np.sqrt(252)
    # 计算 Sharpe Ratio
    sharpe = (annualized_return - risk_free_rate) / annualized_volatility
    return sharpe


def sortino_ratio_cal(returns, risk_free_rate=0.05, target_rate=0.):
    # 计算年化收益率
    annualized_return = np.mean(returns) * 252  # 假设一年有252个交易日
    # 计算低于目标回报的负收益
    downside_returns = returns[returns < target_rate]
    # 计算负收益的标准差
    downside_deviation = np.std(downside_returns) * np.sqrt(252)  # 下行风险年化
    # 计算 Sortino Ratio
    sortino = (annualized_return - risk_free_rate) / downside_deviation if downside_deviation != 0 else np.nan
    return sortino


def backtest_2d(candles: pd.DataFrame, commission: float = 0.0001, slippage: float = 0.0001, init_cash: float = 10000.0,
                freq: str = '1d', use_first_order: bool = False, benchmark_asset: str = None):
    """
    回测
    """
    # 初始化年化收益率
    vbt.settings["returns"]["year_freq"] = 252
    vbt.settings["returns"]["defaults"]['risk_free'] = np.power((1 + 0.05), 1 / 252) - 1

    first_year = candles.index[0].year
    pf = vbt.Portfolio.from_signals(
        close=candles['close'],
        open=candles['open'],
        high=candles['high'],
        low=candles['low'],
        entries=candles['long_entry'],
        exits=candles['long_exit'],
        short_entries=candles['short_entry'],
        short_exits=candles['short_exit'],
        size=candles['size'],
        size_type=vbt.portfolio.enums.SizeType.Amount,
        fees=commission,
        slippage=slippage,
        init_cash=init_cash,
        freq=freq,
        tp_stop=np.nan
    )

    # 解析订单
    orders, trades = parse_orders(pf)
    # # 累计收益 + 基准收益
    # cum_ret, benchmark = cum_ret_cal(
    #     pf,
    #     use_first_order=use_first_order,
    #     benchmark_asset=benchmark_asset
    # )
    # # 最大回撤
    # drawdown = max_drawdown_cal(pf)
    # # 年化统计
    # annual_stats = annual_stats_cal(first_year, pf)
    # # 月度收益
    # month_return_heatmap = monthly_returns_cal(pf)
    # 统计
    summary, additional_stats, total_stats = stats_cal(
        pf,
        orders.copy(),
        init_cash,
        freq=freq
    )
    # if use_first_order:
    #     bret = myround((benchmark[-1][1] - 1) * 100)
    #     for item in total_stats:
    #         if item['name'] == '% Benchmark Return':
    #             item['value'] = bret
    #             break

    orders = orders.to_dict(orient='records')
    return {
        'cum_return': [],
        'benchmark_return': [],
        'max_drawdown': [],
        'annual_stats': [],
        'month_return': [],
        'summary': summary,
        'additional_stats': additional_stats,
        'total_stats': total_stats,
        'orders': orders,
        'trades': trades
    }

import pandas as pd
import time
from typing import Dict

from .custom import *
from ..entities import Signal, SignalT
from ..utils import get_expr_keys


# 运算符映射
_LOGIC_MAP = {
    'EQUAL': '==',
    'GT': '>',
    'GTE': '>=',
    'LT': '<',
    'LTE': '<=',
}


class SignalExecutor:
    def __init__(self, left: str, func: str, right: str, uniqueId: str = None, name: str = None,
                 description: str = None, openStop: bool = False, params: Dict = None):
        """
        动作执行器

        :param left: 左表达式
        :param func: 信号函数
        :param right: 右表达式
        :param name: 信号名称
        :param description: 信号描述
        :param openStop: 开仓后，还未平仓，是否可以计算
        """
        self.func_name = func
        if uniqueId is None:
            uniqueId = str(hash(f"{func}{int(time.time() * 1000)}"))
        self.uniqueId = uniqueId
        self.name = name
        self.description = description
        self.openStop = openStop

        self.left = left
        self.right = right
        self.params = params if params is not None else {}
        self.func = globals()[func]
        self.input_names = self.func.input_names
        self.param_names = self.func.param_names
        self.output_names = self.func.output_names

        # 获取表达式中的关键字
        self.left_keys = get_expr_keys(left)
        self.right_keys = get_expr_keys(right)

    @classmethod
    def from_obj(cls, signal: SignalT):
        if isinstance(signal, dict):
            signal = Signal.parse_obj(signal)
        return cls(
            left=signal.left,
            func=signal.func,
            right=signal.right,
            uniqueId=signal.uniqueId,
            name=signal.name,
            description=signal.description,
            openStop=signal.openStop,
            params=signal.get_params()
        )

    def run(self, run_config: dict) -> bool:
        """
        运行信号

        :param run_config: 运行配置
        :return: 信号值
        """
        left_expr = self.left + ''
        for k in self.left_keys:
            if k in run_config:
                left_expr = left_expr.replace(k, f"run_config['{k}']")
        left = eval(left_expr)

        right_expr = self.right + ''
        for k in self.right_keys:
            if k in run_config:
                right_expr = right_expr.replace(k, f"run_config['{k}']")
        right = eval(right_expr)

        left_type = type(left)
        right_type = type(right)

        # 1. 如果left和right的类型都是float, int, str, bool, 则直接计算
        if left_type in [int, float, str, bool] and right_type in [int, float, str, bool]:
            if self.func_name not in _LOGIC_MAP:
                raise ValueError(f"不支持的运算符：{self.func_name}")
            logic = _LOGIC_MAP[self.func_name]
            res = eval(f"{left} {logic} {right}")

        # 2. 如果left是float，right是Series，或者left是Series，right是float，保持数据维度一致
        if left_type in [int, float, str, bool]:
            left = pd.Series([left] * len(right), index=right.index)
            _type = type(right.iloc[0])
            left = left.astype(float)
        if right_type in [int, float, str, bool]:
            right = pd.Series([right] * len(left), index=left.index)
            _type = type(left.iloc[0])
            right = right.astype(_type)

        params = {
            'left': left,
            'right': right,
            **self.params
        }
        config = self.func.run(**params)
        results = []
        for k in self.output_names:
            results.append(getattr(config, k))
        results = pd.concat(results, axis=1)
        results.columns = self.output_names
        return results['signal']

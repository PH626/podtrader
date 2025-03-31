from typing import Dict, Union, Optional
from pydantic import BaseModel, Field

from .investment import InvestmentT
from .indicator import IndicatorListT
from .signal import SignalListT
from .rule import RuleListT


__all__ = [
    "BacktestEnvironment",
    "BacktestConfig",
    "BacktestEnvironmentT",
    "BacktestConfigT"
]


class BacktestEnvironment(BaseModel):
    id: Optional[str] = Field(default=None, description="环境唯一标识")
    name: Optional[str] = Field(default=None, description="回测环境名称")
    description: Optional[str] = Field(default=None, description="回测环境描述")
    interval: str = Field(default='1d', description="回测数据频率，例如 '1d', '1h'")
    initialCapital: float = Field(default=100000.0, ge=0, description="初始资金，必须大于等于0")
    commission: float = Field(default=0.0, ge=0, description="手续费，必须大于等于0")
    slippage: float = Field(default=0.0, ge=0, description="滑点，必须大于等于0")
    investment: Optional[InvestmentT] = Field(default=None, description="回测的投资对象")
    startTime: str = Field(default='2015-01-01', description="回测起始时间")
    endTime: Optional[str] = Field(default=None, description="回测结束时间")


class BacktestConfig(BaseModel):
    environment: Optional[BacktestEnvironment] = Field(default=None, description="回测环境配置")
    indicators: IndicatorListT = Field(default_factory=list, description="指标列表")
    signals: SignalListT = Field(default_factory=list, description="交易信号列表")
    rules: RuleListT = Field(default_factory=list, description="交易规则列表")


BacktestEnvironmentT = Union[Dict, BacktestEnvironment]
BacktestConfigT = Union[Dict, BacktestConfig]

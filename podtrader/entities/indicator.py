from typing import List, Dict, Union, Optional
from pydantic import BaseModel, Field
from .investment import InvestmentT
from .parameter import ParameterGetter

__all__ = [
    "Indicator",
    "IndicatorT",
    "IndicatorListT"
]


class Indicator(ParameterGetter, BaseModel):
    uniqueId: Optional[str] = Field(default=None, description="唯一标识")
    name: Optional[str] = Field(default=None, description="指标名称")
    description: Optional[str] = Field(default=None, description="指标描述")
    interval: Optional[str] = Field(default=None, description="数据频率")
    investment: Optional[InvestmentT] = Field(default=None, description="投资对象")
    pkg: Optional[str] = Field(default=None, description="指标包名")
    func: Optional[str] = Field(default=None, description="指标函数名")
    openStop: bool = Field(default=False, description="开仓后未平仓时是否可以计算")
    temporary: bool = Field(default=False, description="是否临时指标")

    def __str__(self):
        return f"{self.pkg}.{self.func}"


IndicatorT = Union[Dict, Indicator]
IndicatorListT = Union[List[Dict], List[Indicator]]
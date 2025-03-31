from typing import List, Dict, Union, Optional
from pydantic import BaseModel, Field
from .parameter import ParameterGetter

__all__ = [
    "Signal",
    "SignalT",
    "SignalListT",
]


class Signal(ParameterGetter, BaseModel):
    uniqueId: Optional[str] = Field(default=None, description="唯一标识")
    name: Optional[str] = Field(default=None, description="信号名称")
    description: Optional[str] = Field(default=None, description="信号描述")
    left: Optional[str] = Field(default=None, description="左表达式")
    func: Optional[str] = Field(default=None, description="函数名")
    right: Optional[str] = Field(default=None, description="右表达式")
    openStop: bool = Field(default=False, description="开仓后未平仓时是否可以计算")

    def __str__(self):
        return f"{self.left} {self.func} {self.right}"


SignalT = Union[Dict, Signal]
SignalListT = Union[List[Dict], List[Signal]]
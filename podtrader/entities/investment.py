from typing import Union, Dict
from pydantic import BaseModel, Field

__all__ = ["Investment", "InvestmentT"]


class Investment(BaseModel):
    symbol: str = Field(default="", description="股票或资产的代码")
    localSymbol: str = Field(default="", description="本地交易所代码")
    secType: str = Field(default="", description="证券类型")
    lastTradeDateOrContractMonth: str = Field(default="", description="合约到期日或月份")
    strike: float = Field(default=0.0, ge=0, description="期权行权价")
    right: str = Field(default="", description="期权方向（Call 或 Put）")
    multiplier: str = Field(default="", description="合约乘数")
    exchange: str = Field(default="", description="交易所")
    currency: str = Field(default="", description="交易货币")

    def __str__(self):
        return (
            f"Investment(symbol={self.symbol}, secType={self.secType}, exchange={self.exchange}, "
            f"currency={self.currency}, strike={self.strike}, right={self.right})"
        )


InvestmentT = Union[Dict, Investment]

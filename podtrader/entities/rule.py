from typing import Union, Dict, List, Optional
from pydantic import BaseModel, Field, PositiveInt


__all__ = [
    "CascadeTransaction",
    "TransactionT",
    "TransactionListT",
    "Rule",
    "RuleT",
    "RuleListT",
]


class CascadeTransaction(BaseModel):
    """
    级联表达式
    """
    expression: Optional[str] = Field(default=None, description="交易表达式")
    size: PositiveInt = Field(default=1, description="交易数量，必须为正整数")
    sizeType: int = Field(default=0, description="交易数量类型")

    def __str__(self):
        return f"CascadeTransaction(expression={self.expression}, size={self.size}, sizeType={self.sizeType})"


class Rule(BaseModel):
    """
    交易规则
    """
    uniqueId: Optional[str] = Field(default=None, description="唯一标识")
    name: Optional[str] = Field(default=None, description="规则名称")
    description: Optional[str] = Field(default=None, description="规则描述")
    ruleType: int = Field(default=0, description="规则类型")
    action: int = Field(default=0, description="规则动作")
    transactions: List[CascadeTransaction] = Field(default_factory=list, description="交易列表")

    def __str__(self):
        transactions_str = ", ".join(str(tx) for tx in self.transactions) if self.transactions else "None"
        return (
            f"Rule(uniqueId={self.uniqueId}, name={self.name}, description={self.description}, "
            f"ruleType={self.ruleType}, action={self.action}, transactions=[{transactions_str}])"
        )


TransactionT = Union[Dict, CascadeTransaction]
TransactionListT = Union[List[Dict], List[CascadeTransaction]]
RuleT = Union[Dict, Rule]
RuleListT = Union[List[Dict], List[Rule]]
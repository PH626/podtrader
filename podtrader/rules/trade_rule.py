import time

from ..entities import Rule, RuleT, CascadeTransaction, TransactionListT
from ..events import SignalEvent
from ..enums import RuleType, TradeAction

from ..utils import get_expr_keys


class TradeRule:
    def __init__(self, uniqueId: str = None, name: str = None, description: str = None, ruleType: int = 0,
                 action: int = 0, transactions: TransactionListT = None):
        """
        交易规则

        Args:
            uniqueId: str, 唯一标识
            name: str, 名称
            description: str, 描述
            ruleType: int, 规则类型
            action: int, 0: Buy, 1: Sell, 2: Short
            transactions: List, 交易列表
        """
        if uniqueId is None:
            uniqueId = str(hash(f"RULE{int(time.time() * 1000)}"))
        self.uniqueId = uniqueId
        self.name = name
        self.description = description
        self.ruleType = RuleType(ruleType)
        self.action = TradeAction(action)

        if transactions is None:
            transactions = []
        self.transactions = []
        for tx in transactions:
            if isinstance(tx, dict):
                tx = CascadeTransaction.parse_obj(tx)
            self.transactions.append(tx)

    @classmethod
    def from_rule(cls, rule: RuleT):
        if isinstance(rule, dict):
            rule = Rule.parse_obj(rule)
        return cls(
            uniqueId=rule.uniqueId,
            name=rule.name,
            description=rule.description,
            ruleType=rule.ruleType,
            action=rule.action,
            transactions=rule.transactions
        )

    def transact(self, tx: CascadeTransaction, run_config: dict):
        """
        交易

        Args:
            tx: CascadeTransaction, 交易
            run_config: dict, 运行配置
        """
        expr = tx.expression + ''
        keys = get_expr_keys(tx.expression)
        for k in keys:
            if k in run_config:
                expr = expr.replace(k, f"run_config['{k}']")
        flag = eval(expr)
        if not flag:
            return

        # 触发信号，创建交易事件
        event = SignalEvent()
        event.rule_type = self.ruleType
        event.action = self.action
        event.price = run_config['close']
        event.size = tx.size
        event.size_type = tx.sizeType
        event.priority = self.ruleType.value
        event.timestamp = run_config['dt']
        return event

    def run(self, run_config: dict):
        """
        运行规则

        Args:
            run_config: dict, 运行配置
        """
        for tx in self.transactions:
            event = self.transact(tx, run_config)
            if event is not None:
                return event
        return None

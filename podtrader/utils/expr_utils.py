import re
from typing import List

__all__ = ['get_expr_keys']


def get_expr_keys(expr: str) -> List[str]:
    """
    从表达式中提取关键字（变量名），去除数学运算符、逻辑运算符、比较运算符和连接符。

    关键字可包含：数字、大小写字母、下划线 `_`、原点 `.`

    Args:
        expr (str): 表达式

    Returns:
        List[str]: 关键字列表

    Example:
        >>> get_expr_keys('close & ma.5 + volume_1 / high > low')
        ['close', 'ma.5', 'volume_1', 'high', 'low']
    """
    # 使用正则匹配关键字
    return list(set(re.findall(r'\b[a-zA-Z0-9_.]+\b', expr)))

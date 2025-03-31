from podtrader.utils import get_expr_keys

expr = "1.8 * (I01.T - I01.C)"
print(get_expr_keys(expr))

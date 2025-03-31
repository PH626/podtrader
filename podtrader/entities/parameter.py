from pydantic import BaseModel
from typing import List, Dict, Union

__all__ = ["Parameter", "ParameterGetter", "ParamsT"]


class Parameter(BaseModel):
    name: str = None
    key: str = None
    type: str = None
    value: Union[str, int, float] = None
    describe: str = None


class ParameterGetter(BaseModel):
    params: List[Parameter] = []

    def get_params(self) -> Dict:
        params = {}
        for param in self.params:
            value = param.value
            if param.type == 'int':
                value = int(value)
            elif param.type == 'float':
                value = float(value)
            params[param.key] = value
        return params


ParamsT = Union[List[Dict], List[Parameter]]

"""Registered operational errors. Scientific verdicts never use exceptions."""
from copy import deepcopy
from dataclasses import dataclass, field, replace
import json
from .vocab import RESOURCES
from .redact import safe


@dataclass(frozen=True)
class Problem:
    code: str
    category: str
    message: str
    details: dict=field(default_factory=dict)
    recovery: str=''
    retryable: bool=False
    cause_chain: tuple=()

    def as_dict(self):
        return safe(deepcopy({'code':self.code,'category':self.category,'message':self.message,
            'details':self.details,'recovery':self.recovery,'retryable':self.retryable,'cause_chain':list(self.cause_chain)}))


def problem(code,message=None,details=None):
    registry={row['code']:row for row in json.loads((RESOURCES/'errors.json').read_text(encoding='utf-8'))}
    if code not in registry:raise ValueError('Unknown registered error code')
    row=registry[code]
    return Problem(code,row['category'],message or row['meaning'],deepcopy(details or {}),row['recovery'],row['retryable'])


class ToolkitError(Exception):
    def __init__(self,code,message=None,details=None,*,recovery=None):
        self.problem=problem(code,message,details)
        if recovery is not None:self.problem=replace(self.problem,recovery=recovery)
        super().__init__(self.problem.message)


class CapabilityError(ToolkitError):
    pass

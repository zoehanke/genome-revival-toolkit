"""Single constructor for scientific verdict values, including negative results."""
from copy import deepcopy
from .schemas import require
from .redact import safe


def make(*,check,scope,moment,subject,outcome,issuer,summary,evidence=None,basis=(),
         constraint_id=None,applicability=None,rule_refs=(),does_not_establish=()):
    value=deepcopy({'schema':'verdict-v1','check':check,'scope':scope,'moment':moment,
        'subject':subject,'constraint_id':constraint_id,'outcome':outcome,'issuer':issuer,
        'summary':summary,'evidence':safe(evidence or {}),'basis':list(basis),'applicability':applicability,
        'rule_refs':list(rule_refs),'does_not_establish':list(does_not_establish)})
    return require('verdict-v1',value,'CAPABILITY_OUTPUT_INVALID')

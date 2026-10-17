"""JCS serialization; floats and duplicate JSON keys are not protocol data."""
from decimal import Decimal
import json
import rfc8785
from .errors import ToolkitError


def _validate(value):
    if value is None or type(value) in (str,bool,int):return
    if isinstance(value,list):
        for item in value:_validate(item)
        return
    if isinstance(value,dict) and all(isinstance(key,str) for key in value):
        for item in value.values():_validate(item)
        return
    raise ToolkitError('PLAN_PARAM_INVALID','Use JSON values with integers or decimal strings; no bare floats.')


def dumps(value):
    _validate(value)
    try:return rfc8785.dumps(value)
    except (ValueError,TypeError) as error:
        raise ToolkitError('PLAN_PARAM_INVALID','Value is outside JCS domain.',{'type':type(error).__name__}) from error


def loads(text):
    def unique(pairs):
        result={}
        for key,value in pairs:
            if key in result:raise ToolkitError('PLAN_SCHEMA_INVALID','Duplicate JSON key.')
            result[key]=value
        return result
    try:value=json.loads(text,object_pairs_hook=unique)
    except (ValueError,UnicodeError) as error:
        raise ToolkitError('PLAN_SCHEMA_INVALID','Invalid UTF-8 JSON.') from error
    _validate(value)
    return value


def decimal_string(value):
    if not isinstance(value,(Decimal,int,str)) or isinstance(value,bool):
        raise ToolkitError('PLAN_PARAM_INVALID','Pass a Decimal, integer or decimal string.')
    number=Decimal(value)
    if not number.is_finite():raise ToolkitError('PLAN_PARAM_INVALID','Decimal must be finite.')
    return format(number,'f')

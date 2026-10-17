"""Safe diagnostics, never a transformation of stored scientific documents."""
import re


def long_sequence_literal(value):
    if isinstance(value,str):return len(value)>200 and set(value.upper())<={'A','C','G','T','N'}
    if isinstance(value,dict):return any(long_sequence_literal(v) for v in value.values())
    if isinstance(value,list):return any(long_sequence_literal(v) for v in value)
    return False


def safe(value):
    if isinstance(value,str):
        return re.sub(r'(?i)(?<![a-z])[acgtn]{8,}(?![a-z])','[sequence omitted]',value)
    if isinstance(value,dict):return {str(k):safe(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)):return [safe(v) for v in value]
    return value

"""Only normalization of host syntax; never capability execution."""
from copy import deepcopy
import re
from dna_design_core.kernel.errors import ToolkitError


def reference(value,sources):
    if isinstance(value,str) and value.startswith('@'):
        text=value[1:]
        if text in sources:return {'source':text}
        match=re.fullmatch(r'([a-z][a-z0-9_]{0,31})\.([a-zA-Z_][a-zA-Z0-9_]*)(?:\[(\d+)\])?',text)
        if match:
            result={'step':match[1],'port':match[2]}
            if match[3] is not None:result['index']=int(match[3])
            return result
        raise ToolkitError('PLAN_REF_UNRESOLVED','Invalid compact reference.')
    return deepcopy(value)


def pipeline(document,declarations,sources):
    result=deepcopy(document)
    for step in result.get('steps',[]):
        if not isinstance(step,dict):continue
        use=step.get('use','');name=use.split('@')[0]
        if '@' not in use and name in declarations:step['use']=name+'@'+declarations[name]['declaration']['version']
        step['inputs']={k:reference(v,sources) for k,v in step.get('inputs',{}).items()}
        step['params']={k:reference(v,sources) if isinstance(v,str) and v.startswith('@') else deepcopy(v) for k,v in step.get('params',{}).items()}
        if 'expects' in step:step['expects']['on']=reference(step['expects']['on'],sources)
    for output in result.get('outputs',[]):output['from']=reference(output['from'],sources)
    return result


def revision(document,declarations,sources):
    result=deepcopy(document)
    for operation in result.get('operations',[]):
        if operation.get('op')=='add_step':
            operation['step']=pipeline({'steps':[operation['step']],'outputs':[]},declarations,sources)['steps'][0]
        elif operation.get('op')=='set_outputs':
            operation['outputs']=pipeline({'steps':[],'outputs':operation['outputs']},declarations,sources)['outputs']
    return result

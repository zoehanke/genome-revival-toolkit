"""Goal versions and their sole digest producer."""
from copy import deepcopy
from pathlib import Path
from dna_design_core.kernel import canonical, ids, schemas
from dna_design_core.kernel.errors import ToolkitError


def digest(document):return ids.document_id(document)


def current(events):
    result=None
    for event in events:
        if event['type']=='goal.declared':result=deepcopy(event['payload']['document'])
        elif event['type']=='goal.amended':
            # This writer emits top-level replacements, never accepts host patches.
            for operation in event['payload']['diff']:
                if operation['op']!='replace' or operation['path'].count('/')!=1:
                    raise ToolkitError('JOURNAL_CHAIN_BROKEN','Unsupported goal amendment record.')
                key=operation['path'][1:].replace('~1','/').replace('~0','~')
                result[key]=deepcopy(operation['value'])
    return result


def prepare(document,previous=None,*,declarations):
    result=deepcopy(document)
    constraints=result.get('constraints',[])
    for index,constraint in enumerate(constraints if isinstance(constraints,list) else []):
        if not isinstance(constraint,dict):continue
        if 'origin' in constraint:
            raise ToolkitError('PLAN_GOAL_BINDING_INVALID','Constraint origin is program-derived; omit it from the request.',{'location':'/constraints/'+str(index)+'/origin'},recovery='Omit constraint origin; the program derives it from source_quote and original_request.')
        quote=constraint.get('source_quote');original=result.get('original_request')
        constraint['origin']='user_quoted' if isinstance(quote,str) and quote and isinstance(original,str) and quote in original else 'host_derived'
    schemas.require('goal-v1',result,recovery='Correct the request against goal-v1 and submit the goal again.')
    if previous:
        if result['original_request']!=previous['original_request']:raise ToolkitError('PLAN_GOAL_BINDING_INVALID','original_request cannot change.')
        if result['version']!=previous['version']+1 or result['parent_digest']!=digest(previous):raise ToolkitError('PLAN_GOAL_BINDING_INVALID','Goal version parent differs.')
        if not {c['id'] for c in previous['constraints']}<={c['id'] for c in result['constraints']}:
            raise ToolkitError('PLAN_GOAL_BINDING_INVALID','Constraints cannot disappear; mark dropped with a reason.')
    elif result['version']!=1 or result['parent_digest'] is not None:raise ToolkitError('PLAN_GOAL_BINDING_INVALID','Initial goal must be version 1.')
    targets={t['id'] for t in result['targets']}
    if len(targets)!=len(result['targets']) or len({c['id'] for c in result['constraints']})!=len(result['constraints']) or len({s['source_id'] for s in result['sources']})!=len(result['sources']):raise ToolkitError('PLAN_ID_INVALID')
    for index,constraint in enumerate(result['constraints']):
        if constraint['target'] not in targets:raise ToolkitError('PLAN_GOAL_BINDING_INVALID')
        location='/constraints/'+str(index)
        name,_,version=constraint['check'].partition('@');entry=declarations.get(name)
        declaration=entry['declaration'] if entry else None
        if declaration is None or declaration['role']!='CHECK' or not declaration.get('evaluates_constraint') or declaration['version']!=version:
            raise ToolkitError('PLAN_CAPABILITY_UNKNOWN','Constraint must reference a registered CHECK marked evaluates_constraint at the recorded version.',{'location':location+'/check','check':constraint['check']},recovery='Use describe checks or describe goal-kinds, then reference a constraint CHECK at its recorded version.')
        findings=[{**finding,'location':location+'/params'+finding['location']} for finding in schemas.issues(declaration['params'],constraint['params'])]
        if findings:raise ToolkitError('PLAN_PARAM_INVALID','Constraint parameters violate their check declaration.',{'location':findings[0]['location'],'findings':findings})
        if constraint['status']=='dropped' and not constraint.get('drop_reason'):raise ToolkitError('PLAN_GOAL_BINDING_INVALID','Dropped constraints need a reason.')
    return result


def amend_payload(previous,document,reason,actor,started):
    if not reason.strip():raise ToolkitError('PLAN_WHY_MISSING','Goal amendment needs a reason.')
    patch=[{'op':'replace','path':'/'+key,'value':deepcopy(value)} for key,value in document.items() if previous.get(key)!=value]
    return {'goal_digest':digest(document),'version':document['version'],'previous_digest':digest(previous),'diff':patch,'by':actor,'reason':reason,'amended_after_start':started}

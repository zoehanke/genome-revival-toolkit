"""Static whole-plan admission. No import or call of a capability implementation."""
from copy import deepcopy
from dna_design_core.kernel import schemas
from dna_design_core.kernel.errors import problem
from dna_design_core.kernel.redact import long_sequence_literal


def check(plan,goal,declarations,states,unavailable=()):
    problems=[]
    def add(code,location,message=None):problems.append(problem(code,message,{'location':location}).as_dict())
    for index,step in enumerate(plan.get('steps',[]) if isinstance(plan,dict) and isinstance(plan.get('steps'),list) else []):
        if not isinstance(step,dict) or not isinstance(step.get('inputs'),dict):continue
        declaration=declarations.get(str(step.get('use','')).split('@')[0],{}).get('declaration',{})
        for port in declaration.get('inputs',[]):
            if port['type']!='materials' or port['name'] not in step['inputs']:continue
            ref=step['inputs'][port['name']]
            if not isinstance(ref,dict) or set(ref)!={'step','port'}:
                add('PLAN_INPUT_UNBOUND','/steps/'+str(index)+'/inputs/'+port['name'],
                    'materials input must reference one earlier materials output; concatenated sources, steps and literal lists are not supported.')
    if problems:return problems
    shape=schemas.issues('pipeline-v1',plan)
    if shape:
        for issue in shape:add('PLAN_SCHEMA_INVALID',issue['location'])
        return problems
    source_types={s['source_id']:'material' if s.get('as')=='material' else 'artifact' for s in goal['sources']}
    artifacts={s['path'] for s in goal['sources']}
    artifacts.update(a['run_path'] for row in states.values() if row.get('completed') and not row.get('superseded_by') for a in row['completed']['payload']['outputs']['artifacts'])
    previous={};names=set(source_types)
    def ref_type(ref,allowed,location,self_step=None,collection=False):
        if not isinstance(ref,dict):add('PLAN_REF_UNRESOLVED',location);return None
        if 'literal' in ref:return 'value'
        if 'source' in ref:
            if ref['source'] not in source_types:add('PLAN_REF_UNRESOLVED',location)
            return source_types.get(ref['source'])
        if 'artifact' in ref:
            if ref['artifact'] not in artifacts:add('PLAN_REF_UNRESOLVED',location)
            return 'artifact'
        step_id=ref.get('step')
        if step_id not in allowed or step_id!=self_step and (states.get(step_id,{}).get('state')=='FAILED' or states.get(step_id,{}).get('superseded_by')):
            add('PLAN_REF_UNRESOLVED',location);return None
        outputs=allowed[step_id]
        port=outputs.get(ref.get('port'))
        if port is None:add('PLAN_REF_UNRESOLVED',location);return None
        if port['type']=='materials':
            if 'index' in ref:return 'material'
            if not collection:add('PLAN_REF_UNRESOLVED',location,'Multi-material item reference needs explicit index.')
            return 'materials'
        if 'index' in ref and ref['index']!=0:add('PLAN_REF_UNRESOLVED',location,'Single-value reference index must be zero.')
        return port['type']
    for index,step in enumerate(plan['steps']):
        location='/steps/'+str(index);name,_,version=step['use'].partition('@')
        if step['step_id'] in names:add('PLAN_ID_INVALID',location)
        names.add(step['step_id'])
        item=declarations.get(name)
        if item is None or item['declaration']['role']!='ACTION' or item['declaration']['version']!=version or name in unavailable:
            add('PLAN_CAPABILITY_UNKNOWN',location);continue
        declaration=item['declaration'];ports={p['name']:p for p in declaration['inputs']}
        for key in step['inputs'].keys()-ports.keys():add('PLAN_INPUT_UNBOUND',location+'/inputs/'+key)
        for key,port in ports.items():
            if key not in step['inputs']:
                if port['required']:add('PLAN_INPUT_UNBOUND',location+'/inputs/'+key)
                continue
            ref=step['inputs'][key];actual=ref_type(ref,previous,location+'/inputs/'+key,collection=port['type']=='materials')
            if actual is not None and actual!=port['type']:add('PLAN_INPUT_UNBOUND',location+'/inputs/'+key,
                'materials input requires an earlier materials output.' if port['type']=='materials' else None)
            if 'literal' in ref and port['constraints'] and schemas.issues(port['constraints'],ref['literal']):add('PLAN_PARAM_INVALID',location+'/inputs/'+key)
        params=deepcopy(step['params']);parameter_schema=deepcopy(declaration['params'])
        for key,value in list(params.items()):
            if isinstance(value,dict) and set(value)&{'source','step','artifact','literal'}:
                ref_type(value,previous,location+'/params/'+key)
                if 'literal' in value:params[key]=value['literal']
                else:
                    if isinstance(parameter_schema,dict) and parameter_schema.get('additionalProperties') is False and key not in parameter_schema.get('properties',{}) and not parameter_schema.get('patternProperties'):
                        add('PLAN_PARAM_INVALID',location+'/params/'+key)
                    params.pop(key)
                    if isinstance(parameter_schema,dict):
                        parameter_schema['required']=[k for k in parameter_schema.get('required',[]) if k!=key]
        if schemas.issues(parameter_schema,params):add('PLAN_PARAM_INVALID',location+'/params')
        if long_sequence_literal(step['params']) or long_sequence_literal(step['inputs']):add('PLAN_PARAM_INVALID',location,'Sequences longer than 200 nt require a file.')
        outputs={p['name']:p for p in declaration['outputs']}
        if 'expects' in step:
            expectation=step['expects'];actual=ref_type(expectation['on'],{**previous,step['step_id']:outputs},location+'/expects/on',step['step_id'])
            op=expectation['op'];value=expectation['value']
            if 'pointer' in expectation['on'] and actual not in {'document','value'}:add('PLAN_EXPECT_INVALID',location+'/expects')
            if op in {'gte','lte','between'} and actual!='value' and 'pointer' not in expectation['on']:add('PLAN_EXPECT_INVALID',location+'/expects')
            if op in {'gte','lte','length_equals'} and type(value) is not int:add('PLAN_EXPECT_INVALID',location+'/expects')
            if op=='between' and (not isinstance(value,list) or len(value)!=2 or not all(type(v) is int for v in value)):add('PLAN_EXPECT_INVALID',location+'/expects')
        previous[step['step_id']]=outputs
    targets={t['id'] for t in goal['targets']}
    for index,output in enumerate(plan['outputs']):
        if output['target'] not in targets:
            ref=output['from'];port=previous.get(ref.get('step'),{}).get(ref.get('port'),{})
            role=port.get('output_role')
            needed=" with role '"+role+"'" if role else ' compatible with the producer output role'
            add('PLAN_OUTPUT_INVALID','/outputs/'+str(index),
                "Output '"+output['name']+"' requires target '"+output['target']+"'"+needed+
                '; add that target to the goal or bind this output to an existing target of the required role.')
        ref_type(output['from'],previous,'/outputs/'+str(index)+'/from')
    for constraint in goal['constraints']:
        if constraint['status']!='active':continue
        name,_,version=constraint['check'].partition('@');entry=declarations.get(name)
        if entry is None or not entry['declaration'].get('evaluates_constraint') or entry['declaration']['version']!=version:add('PLAN_CAPABILITY_UNKNOWN','/goal/constraints')
    return problems

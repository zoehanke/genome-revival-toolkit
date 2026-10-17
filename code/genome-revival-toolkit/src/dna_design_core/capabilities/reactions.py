"""Replay recorded sequence reactions from roots, full oligos and actual parameters."""
from dna_design_core.kernel.public import ToolkitError,material_id,document_id
from .recorded import parameters,catalog as frozen_catalog
from .material_evidence import root_materials
from .builtin.checks import _arguments

REACTIONS={'pcr.simulate','restriction.digest','assembly.ligate','assembly.gibson','assembly.inverse_pcr'}
OPERATIONS=REACTIONS|{'seq.rotate'}
METHODS={'pcr':'pcr.simulate','gibson':'assembly.gibson','inverse_pcr':'assembly.inverse_pcr'}


def _projection(material):return {k:material[k] for k in ['sequence','topology','ends']}


def _preparation_records(records):
    """Keep physical reactions and their recorded coordinate-transform paths.

    An independent editing/model branch is not a preparation predecessor.
    It must neither supply a candidate to simulation nor block a valid chain.
    """
    def output_ids(record):
        return {mid for ids in record['payload']['outputs']['materials'].values() for mid in ids}
    selected={r['event'] for r in records if r['name'] in REACTIONS}
    derived={mid for r in records if r['event'] in selected for mid in output_ids(r)}
    for record in records:
        if record['name']=='seq.rotate' and derived.intersection(record['payload']['input_ids'].values()):
            selected.add(record['event']);derived.update(output_ids(record))
    needed={mid for r in records if r['event'] in selected for mid in r['payload']['input_ids'].values()}
    for record in reversed(records):
        if record['name']=='seq.rotate' and needed.intersection(output_ids(record)):
            selected.add(record['event']);needed.update(record['payload']['input_ids'].values())
    return [r for r in records if r['event'] in selected]


def _context(view):
    steps={s['definition']['step_id']:s for s in view.steps()}
    declarations={r['declaration']['id']:r['declaration'] for r in frozen_catalog(view)['capabilities']}
    bindings=[];parents=set()
    for bound in view.pipeline['outputs']:
        ref=bound['from'];step=steps.get(ref.get('step'))
        if step is None or not step['completed'] or step['superseded']:continue
        declaration=declarations[step['definition']['use'].split('@')[0]]
        port=next(p for p in declaration['outputs'] if p['name']==ref['port'])
        if port['output_role'] not in {'construct','primer_set'}:continue
        parents.add(ref['step'])
        if port['type'] in {'material','materials'}:
            bindings.append({'parent':ref['step'],'port':ref['port'],'id':step['completed']['payload']['outputs']['materials'][ref['port']][ref.get('index',0)]})
    records=[]
    for identity,step in steps.items():
        name=step['definition']['use'].split('@')[0]
        if step['completed'] and not step['superseded'] and name in OPERATIONS:
            payload=step['started']['payload']
            records.append({'event':step['completed']['hash'],'seq':step['completed']['seq'],'parent':identity,'name':name,'declaration':declarations[name],
                'payload':{**payload,'input_ids':{k:v['id'] for k,v in payload['inputs'].items()},'outputs':step['completed']['payload']['outputs']},'step':step})
    for event in view.events('call.recorded'):
        payload=event['payload'];name=payload['capability']['id'];parent=steps.get(payload['parent'])
        if name not in OPERATIONS or parent is None or parent['superseded'] or not parent['completed'] or 'outputs' not in payload:continue
        records.append({'event':event['hash'],'seq':event['seq'],'parent':payload['parent'],'name':name,'declaration':declarations[name],'payload':payload,'step':None})
    return steps,declarations,parents,bindings,_preparation_records(sorted(records,key=lambda r:r['seq']))


def _routes(view,step):
    result=[]
    for identities in step['completed']['payload']['outputs']['documents'].values():
        for identity in identities:
            value=view.document(identity)
            if isinstance(value,dict) and value.get('schema')=='route-plan-v1':result.append(value)
    return result


def run(ctx,identity,names=None):
    from .builtin.check.content import verdict
    view=ctx.view;strict=identity=='check.reaction_chain'
    steps,declarations,required_parents,bindings,records=_context(view)
    matched=[r for r in records if r['name'] in (names or REACTIONS)]
    if not matched:
        outcome='UNKNOWN' if strict and required_parents else 'NOT_APPLICABLE'
        return verdict(ctx,identity,outcome,'No supported preparation reaction was recorded.' if outcome=='UNKNOWN' else 'No matching sequence reaction was recorded.',
            {'recomputed':[],'differences':[],'not_checked':sorted(required_parents) if strict else []},scope='preparation_model')
    differences=[];not_checked=[];recomputed=[];calculated={};records_by_parent={}
    for record in records:records_by_parent.setdefault(record['parent'],[]).append(record)
    roots={}
    for parent in records_by_parent:
        originals,_=root_materials(view,parent)
        roots[parent]={r['material_id']:r['material'] for r in originals}
    # Explicit top-level short literal materials are also original declared
    # inputs, not products inferred from the candidate.
    for step in steps.values():
        if step['completed'] and not step['superseded'] and step['definition']['use'].split('@')[0]=='seq.make_material' and 'literal' in step['definition']['inputs'].get('sequence',{}):
            for ids in step['completed']['payload']['outputs']['materials'].values():
                for mid in ids:
                    for pool in roots.values():pool[mid]=view.material(mid)
    cache={}
    for record in records:
        payload=record['payload'];parent=record['parent'];key=record['event']
        try:
            params=parameters(payload)
            args={};fallback=None
            for port in record['declaration']['inputs']:
                name=port['name']
                if name not in payload['input_ids']:continue
                mid=payload['input_ids'][name]
                if mid in cache:args[name]=cache[mid]
                elif mid in roots[parent]:args[name]=roots[parent][mid]
                elif name in {'forward','reverse'} or not strict:
                    if record['step'] is not None:
                        if fallback is None:fallback=_arguments(view,record['step'])[0]
                        args[name]=fallback[name]
                    else:args[name]=view.material(mid)
                else:raise ToolkitError('CHECK_UNAVAILABLE','Reaction input lacks an original template or simulated predecessor.')
            result=ctx.call(record['name']+'@'+record['declaration']['version'],inputs=args,params=params)
            actual={name:[material_id(v) for v in (data if isinstance(data,list) else [data])] for name,data in result.products.items()}
            expected=payload['outputs']['materials']
            if actual!=expected:
                differences.append({'event':key,'parent':parent,'fields':['materials'],'recorded':document_id(expected),'recomputed':document_id(actual)})
                continue
            for name,data in result.products.items():
                values=data if isinstance(data,list) else [data]
                for mid,value in zip(expected[name],values):cache[mid]=value
            calculated[key]=result.products
            recomputed.append({'event':key,'parent':parent,'capability':record['name'],'params_digest':payload['params_digest']})
        except ToolkitError as error:
            if error.problem.code in {'STORE_CORRUPT','PLAN_PARAM_INVALID','CAPABILITY_OUTPUT_INVALID'}:
                differences.append({'event':key,'parent':parent,'fields':['params_digest'] if error.problem.code=='STORE_CORRUPT' else ['reaction_result'],'failure_code':error.problem.code})
            else:not_checked.append({'event':key,'parent':parent,'reason':error.problem.message})
    # Every candidate read occurs after the simulations above. Calculators
    # receive only actual templates, complete primers and recorded parameters.
    if strict:
        for parent in required_parents:
            step=steps[parent];parent_records=records_by_parent.get(parent,[]);route_rows=_routes(view,step)
            direct=step['definition']['use'].split('@')[0] in REACTIONS
            if not parent_records:
                not_checked.append({'parent':parent,'reason':'No supported reaction chain for this preparation output.'});continue
            if not route_rows and not direct:
                not_checked.append({'parent':parent,'reason':'No declared route accompanies this preparation output.'});continue
            terminal=None
            if route_rows:
                if len(route_rows)!=1 or route_rows[0].get('method') not in METHODS:
                    not_checked.append({'parent':parent,'reason':'Route method is unsupported or ambiguous.'});continue
                route=route_rows[0];wanted=METHODS[route['method']]
                eligible=[r for r in parent_records if r['name']==wanted and r['event'] in calculated]
                if route.get('reactions'):
                    last=route['reactions'][-1]
                    eligible=[r for r in eligible if r['payload']['outputs']['materials'].get('product')==[last.get('product_id')]]
                    # Declarations are compared with program records, never
                    # substituted for actual execution parameters.
                    for reaction in route['reactions']:
                        method=METHODS.get(reaction.get('method'))
                        matches=[r for r in parent_records if r['event'] in calculated and r['name']==method and r['payload']['outputs']['materials'].get('product')==[reaction.get('product_id')]]
                        if len(matches)!=1 or parameters(matches[0]['payload'])!=reaction.get('params') or [matches[0]['payload']['input_ids'][p['name']] for p in matches[0]['declaration']['inputs'] if p['name'] in matches[0]['payload']['input_ids']]!=reaction.get('inputs'):
                            differences.append({'parent':parent,'fields':['route_reaction']})
                if len(eligible)!=1:
                    not_checked.append({'parent':parent,'reason':'Route has no unique recomputed terminal reaction.'});continue
                terminal=calculated[eligible[0]['event']]['product']
                if route['method']=='inverse_pcr' and route.get('rotation_to_template_origin'):
                    # Origin choice is a declared coordinate transform, not
                    # a physical reaction or candidate-sequence input.
                    terminal=ctx.call('seq.rotate',inputs={'material':terminal},params={'origin':route['rotation_to_template_origin']}).products['material']
            elif direct:
                outputs=calculated.get(parent_records[-1]['event'],{})
                terminal=outputs.get('product')
            for bound in (b for b in bindings if b['parent']==parent):
                if terminal is None:
                    not_checked.append({'parent':parent,'reason':'No simulated product is available for the bound material.'});continue
                actual_material=view.material(bound['id'])
                expected=_projection(terminal);actual=_projection(actual_material)
                fields=[k for k in expected if expected[k]!=actual[k]]
                if fields:differences.append({'parent':parent,'fields':fields,'recomputed':document_id(expected),'candidate':document_id(actual)})
    outcome='FAIL' if differences else 'UNKNOWN' if not_checked else 'PASS'
    return verdict(ctx,identity,outcome,'Recorded sequence reactions recomputed before candidate comparison.',
        {'recomputed':recomputed,'differences':differences,'not_checked':not_checked,'candidate_used_as_simulation_input':False},scope='preparation_model')

"""D7 union from the frozen catalog, including every executed capability."""
from copy import deepcopy
from dna_design_core.kernel import ids


def derive(snapshot, goal, plan, events, also=()):
    declarations={r['declaration']['id']:r['declaration'] for r in snapshot['capabilities']}
    required={}
    def add(use,params=None,constraint=None):
        name,_,version=use.partition('@');decl=declarations.get(name,{})
        item={'check':name,'version':version or decl.get('version'),'params':deepcopy(params or {}),'constraint':deepcopy(constraint),'scope':decl.get('scope','content_model')}
        key=ids.document_id(item);required[key]={'id':key,**item}
    for check in snapshot['profiles']['always']:add(check)
    if any(e['type']=='step.completed' and e['payload']['outputs']['materials'] for e in events):
        for check in snapshot['profiles']['on_material_output']:add(check)
    definitions={s['step_id']:s for s in plan['steps']}
    for output in plan['outputs']:
        ref=output['from'];step=definitions.get(ref.get('step'),{})
        decl=declarations.get(step.get('use','').split('@')[0],{})
        port=next((p for p in decl.get('outputs',[]) if p['name']==ref.get('port')),None)
        if port:
            for check in snapshot['profiles']['roles'].get(port['output_role'],[]):add(check)
    for constraint in goal['constraints']:
        if constraint['status']=='active':add(constraint['check'],constraint['params'],constraint)
    used={e['payload']['capability']['id'] for e in events if e['type'] in {'step.started','call.recorded'}}
    for name in sorted(used):
        decl=declarations.get(name,{})
        for row in decl.get('final_checks',[]):add(row['check'],row.get('params'))
        if decl.get('model'):add('check.model_agreement')
    for check in also:add(check)
    return list(required.values())

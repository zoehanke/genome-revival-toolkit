"""Discover declared primer documents and complete primer invocation values."""
from .recorded import catalog,parameters
from .builtin.checks import _arguments


def primer_documents(view):
    declarations={r['declaration']['id']:r['declaration'] for r in catalog(view)['capabilities']}
    steps={s['definition']['step_id']:s for s in view.steps()};subjects=set()
    # D7 profile scope is derived from bound producer roles. An unbound
    # diagnostic primer proposal is not silently promoted to an order.
    for binding in view.pipeline['outputs']:
        reference=binding['from'];step=steps.get(reference.get('step'))
        if step is None:continue
        declaration=declarations[step['definition']['use'].split('@')[0]]
        port=next(p for p in declaration['outputs'] if p['name']==reference['port'])
        if port['output_role'] in {'construct','primer_set'}:subjects.add(reference['step'])
    result=[]
    for step in view.steps():
        if not step['completed'] or step['superseded'] or step['definition']['step_id'] not in subjects:continue
        declaration=declarations[step['definition']['use'].split('@')[0]]
        for port in declaration['outputs']:
            if port['output_role']!='primer_set':continue
            if port['type']!='document':
                result.append({'parent':step['definition']['step_id'],'invalid':'Marked primer output has no supported document shape.'});continue
            identity=step['completed']['payload']['outputs']['documents'][port['name']][0]
            document=view.document(identity)
            item={'parent':step['definition']['step_id'],'document_id':identity,'document':document,'producer_parameters':parameters(step['started']['payload'])}
            if not isinstance(document,dict) or document.get('schema')!='primer-set-v1' or not isinstance(document.get('primers'),list):item['invalid']='Unsupported primer-set document shape.'
            result.append(item)
    return result


def primer_uses(view,parent):
    methods={'pcr.simulate','assembly.inverse_pcr'};rows=[]
    for step in view.steps():
        if step['definition']['step_id']!=parent or not step['completed'] or step['superseded'] or step['definition']['use'].split('@')[0] not in methods:continue
        inputs=_arguments(view,step)[0];params=parameters(step['started']['payload'])
        rows.extend({'event':step['started']['hash'],'name':name,'material':inputs[name],
                     'core_length':params.get(name+'_core_length') or len(inputs[name]['sequence'])} for name in ['forward','reverse'])
    for event in view.events('call.recorded'):
        payload=event['payload']
        if payload['parent']!=parent or payload['capability']['id'] not in methods or 'outputs' not in payload:continue
        params=parameters(payload)
        for name in ['forward','reverse']:
            material=view.material(payload['input_ids'][name])
            rows.append({'event':event['hash'],'name':name,'material':material,
                         'core_length':params.get(name+'_core_length') or len(material['sequence'])})
    return rows

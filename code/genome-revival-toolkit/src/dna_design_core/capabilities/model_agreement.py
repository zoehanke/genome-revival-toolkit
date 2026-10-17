"""D3 independent model dispatch; only sequence, topology and ends are compared."""
from copy import deepcopy
from dna_design_core.kernel.public import Outcome, capability, document_id, normalize_material,ToolkitError
from .declaration import check
from .builtin.checks import _arguments, _declarations, _verdict
from .recorded import parameters,nested_inputs


@capability(check('check.model_agreement','content_model',
    'dna_design_core.capabilities.model_agreement:compare',
    'Compare the recorded product with an independently declared model.',composite=True))
def compare(ctx) -> Outcome:
    declarations=_declarations(ctx.view);differences=[];compared=[];not_checked=[]
    invocations=[]
    for step in ctx.view.steps():
        declaration=declarations[step['definition']['use'].split('@')[0]]
        if not declaration.get('model') or step['completed'] is None:continue
        inputs,_,identities,original=_arguments(ctx.view,step)
        invocations.append((step['definition']['step_id'],declaration,inputs,step['started']['payload'],
            step['completed']['payload']['outputs'],identities!=original))
    for event in ctx.view.events('call.recorded'):
        payload=event['payload'];declaration=declarations[payload['capability']['id']]
        if not declaration.get('model'):continue
        if 'outputs' not in payload:
            not_checked.append({'event':event['hash'],'reason':'Nested model invocation failed before producing an output.'});continue
        if 'params' not in payload or 'params_digest' not in payload:
            not_checked.append({'event':event['hash'],'reason':'Nested invocation parameters are not recorded.'});continue
        inputs=nested_inputs(ctx.view,declaration,payload)
        invocations.append((event['hash'],declaration,inputs,payload,payload['outputs'],False))
    for identity,declaration,inputs,payload,outputs,changed_inputs in invocations:
        model=declarations[declaration['model']]
        try:params=parameters(payload)
        except ToolkitError as error:
            if error.problem.code=='STORE_CORRUPT':differences.append({'step_id':identity,'fields':['params_digest']})
            else:not_checked.append({'event':identity,'reason':'Invocation parameters are not available.'})
            continue
        names=model['params'].get('properties',{}) if isinstance(model['params'],dict) else {}
        result=ctx.call(model['id']+'@'+model['version'],
            inputs={p['name']:inputs[p['name']] for p in model['inputs'] if p['name'] in inputs},
            params={name:deepcopy(params[name]) for name in names if name in params})
        actual=normalize_material(result.products['product'])
        recorded=ctx.view.material(outputs['materials']['product'][0])
        before={key:recorded[key] for key in ['sequence','topology','ends']}
        after={key:actual[key] for key in ['sequence','topology','ends']}
        fields=[key for key in before if before[key]!=after[key]]
        if changed_inputs:fields.append('input_ids')
        row={'step_id':identity,'model':model['id'],
             'recorded_result':document_id(before),'model_result':document_id(after)}
        compared.append(row)
        if fields:differences.append({**row,'fields':fields})
    outcome='FAIL' if differences else 'UNKNOWN' if not_checked or not compared else 'PASS'
    return _verdict(ctx,'check.model_agreement','content_model',outcome,
        'Recorded and model products compared without annotations.',
        {'compared':compared,'differences':differences,'not_checked':not_checked})

"""Shared construction of exportable Core declarations; no second registry."""
from dna_design_core.kernel.public import core_version


def action(identity, summary, implementation, inputs, outputs, *, effects=('pure',), params=None, final_checks=()):
    return {'schema':'capability-v1','id':identity,'version':core_version(),'role':'ACTION',
            'summary':summary,'effects':list(effects),'deterministic':True,'requires_runtime':[],
            'inputs':inputs,'params':params or {'type':'object','properties':{},'additionalProperties':False},
            'outputs':outputs,'step_checks':[],'final_checks':[{'check':name} for name in final_checks],
            'does_not_establish':['Wet-laboratory performance or biological function.'],
            'source':{'algorithm_refs':[],'implemented_in':implementation},'owner':'core','granularity':'atomic'}


def check(identity, scope, implementation, summary, *, constraint=False, composite=False, params=None):
    value=action(identity,summary,implementation,[],[],effects=('reads_files',),params=params)
    value.update(role='CHECK',scope=scope,evaluates_constraint=constraint,offline=True,
                 fixtures={'pass':'tests/fixtures/checks/'+identity+'.pass.json','fail':'tests/fixtures/checks/'+identity+'.fail.json'},
                 granularity='composite' if composite else 'atomic')
    return value

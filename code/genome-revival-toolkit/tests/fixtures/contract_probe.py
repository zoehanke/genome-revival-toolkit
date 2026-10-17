"""Temporary external Kits; oracles are specified by each test, never generated."""
from copy import deepcopy
import json
from pathlib import Path


def action(name,inputs=(),outputs=(),*,params=None,model=None,owner='contract_probe'):
    value={'schema':'capability-v1','id':owner+'.'+name,'version':'0.0.0','role':'ACTION',
           'summary':'Synthetic contract probe.','effects':['pure'],'deterministic':True,'requires_runtime':[],
           'inputs':list(inputs),'params':params or {'type':'object','properties':{},'additionalProperties':False},
           'outputs':list(outputs),'step_checks':[],'final_checks':[],'does_not_establish':['Biological validity.'],
           'source':{'algorithm_refs':[],'implemented_in':'grt_'+owner+'.capabilities.unit:'+name},
           'owner':'kit:'+owner,'granularity':'atomic'}
    if model:value['model']=owner+'.'+model
    return value


def port(name,kind,*,input=False,schema=None,schema_ref=None):
    value={'name':name,'type':kind}
    if input:value.update(required=True,constraints={},description='Constructed input.')
    else:value['output_role']=None
    if schema is not None:value['schema']=deepcopy(schema)
    if schema_ref is not None:value['schema_ref']=schema_ref
    return value


def build(root,definitions,*,knowledge=None,owner='contract_probe'):
    """definitions: declaration, explicit function source. No code is imported here."""
    root=Path(root);(root/'capabilities').mkdir(parents=True)
    text='from dna_design_core.kernel.public import Outcome, capability, make, core_version\n'
    names=[]
    for declaration,source in definitions:
        name='capabilities/'+declaration['id'].split('.')[-1]+'.json';names.append(name)
        (root/name).write_text(json.dumps(declaration,indent=2)+'\n',encoding='utf-8',newline='\n')
        text+='\n@capability('+repr(declaration)+')\n'+source+'\n'
        for variant,path in declaration.get('fixtures',{}).items():
            target=root/path;target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(json.dumps({'expected':'PASS' if variant=='pass' else 'FAIL','oracle':{'kind':'construction','reason':'Explicit synthetic control.'}})+'\n',encoding='utf-8')
    (root/'capabilities/unit.py').write_text(text,encoding='utf-8',newline='\n')
    packs=[]
    for name,value in (knowledge or {}).items():
        path=root/name;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n');packs.append(name)
    manifest={'schema':'kit-v1','name':owner,'title':'Synthetic contract probe','version':'0.0.0',
              'requires_core':{'minimum':'0.0.0','maximum_exclusive':'1.0.0'},
              'contributes':{'capabilities':names,'knowledge':packs,'templates':[],'text':[]},
              'does_not_establish':['Biological validity.'],'review':'knowledge/review/'}
    (root/'kit.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    return root


def goal(sources=()):
    return {'schema':'goal-v1','version':1,'parent_digest':None,'original_request':'Inspect constructed contract results.',
            'sources':list(sources),'declared_context':[],'targets':[{'id':'t1','role':'analysis','required':True}],
            'constraints':[],'intents':[]}


def plan(digest,steps,output):
    return {'schema':'pipeline-v1','version':1,'goal_digest':digest,'steps':steps,
            'outputs':[{'name':'result','from':output,'target':'t1'}]}


def step(name,use,inputs=None,params=None):
    return {'step_id':name,'use':'contract_probe.'+use,'inputs':inputs or {},'params':params or {},'why':'Exercise an explicit contract.'}


COUNT={'type':'object','properties':{'count':{'type':'integer'}},'required':['count'],'additionalProperties':False}


def inline_definitions(*,bad_output=False,strict_input=False):
    incoming=deepcopy(COUNT)
    if strict_input:incoming['properties']['count']['maximum']=5
    return [(action('produce',outputs=[port('document','document',schema=COUNT)]),
             'def produce(ctx):\n    return Outcome(documents={"document":{"count":'+('"seven"' if bad_output else '7')+'}})\n'),
            (action('consume',[port('document','document',input=True,schema=incoming)],[port('number','value')]),
             'def consume(ctx, document):\n    return Outcome(values={"number":document["count"]})\n')]


def knowledge_definitions(pack='kit:contract_probe/knowledge/table.json'):
    params={'type':'object','properties':{'pack':{'type':'string'}},'additionalProperties':False}
    reader=action('read',outputs=[port('number','value')],params=params)
    checker=action('check_read',params=params)
    checker.update(role='CHECK',scope='content_model',evaluates_constraint=False,offline=True,
                   fixtures={'pass':'fixtures/read.pass.json','fail':'fixtures/read.fail.json'})
    return [(reader,'def read(ctx, pack='+repr(pack)+'):\n    value=ctx.knowledge(pack)\n    value["parameters"]["count"]=99\n    return Outcome(values={"number":ctx.knowledge(pack)["parameters"]["count"]})\n'),
            (checker,'def check_read(ctx, pack='+repr(pack)+'):\n    value=ctx.knowledge(pack)\n    return Outcome(verdicts=[make(check={"id":"contract_probe.check_read","version":core_version()},scope="content_model",moment="final",issuer="check_capability",subject={"kind":"run","id":ctx.view.events()[0]["run_id"]},outcome="PASS" if value["parameters"]["count"]==7 else "FAIL",summary="Frozen knowledge read.",evidence={"count":value["parameters"]["count"]},basis=[e["hash"] for e in ctx.view.events()],does_not_establish=["Biological validity."])])\n')]


def rule(root):
    value=json.loads((Path(root)/'tests/fixtures/schemas/rule-v1.valid.json').read_text(encoding='utf-8'))['data']
    value['parameters']={'count':7}
    return value


def model_definitions(*,sequence='ACGT',topology='linear',ends=None,feature=False):
    incoming=port('template','material',input=True)
    params={'type':'object','properties':{'offset':{'type':'integer'},'unused':{'type':'integer'}},'required':['offset'],'additionalProperties':False}
    original=action('original',[incoming],[port('product','material')],params=params,model='predict')
    model=action('predict',[deepcopy(incoming)],[port('product','material')],params={'type':'object','properties':{'offset':{'type':'integer'}},'required':['offset'],'additionalProperties':False})
    product={'sequence':sequence,'topology':topology,'ends':ends}
    if feature:product['features']=[{'start':0,'end':1,'type':'misc_feature','label':'model only'}]
    return [(original,'def original(ctx, template, offset, unused=0):\n    assert offset==2 and unused==13\n    return Outcome(products={"product":{"sequence":template["sequence"],"topology":"linear","ends":None}})\n'),
            (model,'def predict(ctx, template, offset):\n    assert offset==2 and template["sequence"]=="ACGT"\n    return Outcome(products={"product":'+repr(product)+'})\n')]


def materials_definitions():
    return [(action('pieces',outputs=[port('pieces','materials')]),
             'def pieces(ctx):\n    return Outcome(products={"pieces":[{"sequence":"ACGT"},{"sequence":"CCGA"}]})\n'),
            (action('total',[port('pieces','materials',input=True)],[port('number','value')]),
             'def total(ctx, pieces):\n    return Outcome(values={"number":sum(len(p["sequence"]) for p in pieces)})\n'),
            (action('single',[port('piece','material',input=True)],[port('number','value')]),
             'def single(ctx, piece):\n    return Outcome(values={"number":len(piece["sequence"])})\n')]

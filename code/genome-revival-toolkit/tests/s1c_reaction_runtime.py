"""A declared, nested PCR route independent of its fixed expected product."""
import json
from pathlib import Path
from dna_design_core.application import api
from dna_design_core.application.run_service import RunService
from tests.fixtures.contract_probe import action,port,build,goal,plan,step


def prepare(folder,*,wrong=False,method='pcr',wrong_order=False,wrong_length=False,extra_rotation=False,thermal_window=None):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    values={'template':{'sequence':'TTAACTGGACTCCGATC','topology':'linear','strandedness':'double'},
            'forward':{'sequence':'AACT','topology':'linear','strandedness':'single'},
            'reverse':{'sequence':'GATC','topology':'linear','strandedness':'single'}}
    sources=[]
    for name,value in values.items():
        path=folder/(name+'.json');path.write_text(json.dumps(value),encoding='utf-8')
        sources.append({'source_id':name,'from':str(path),'as':'material','input_origin':'user_file','declared':{}})
    inputs=[port(name,'material',input=True) for name in values]
    original=action('prepare',inputs,[port('product','material'),port('primers','document',schema={'type':'object'}),port('route','document',schema={'type':'object'})],model='model')
    original['granularity']='composite';original['outputs'][0]['output_role']='construct';original['outputs'][1]['output_role']='primer_set'
    original['params']={'type':'object','properties':{'primer_length':{'type':'integer'},'tm_min':{'type':'string'},'tm_max':{'type':'string'},'tm_parameters':{'type':'object'}},'required':['primer_length'],'additionalProperties':False}
    expected=action('model',inputs,[port('product','material')])
    # Programmed difference is only test fixture input; Core never sees a case id.
    body='''def prepare(ctx, template, forward, reverse, primer_length, tm_min=None, tm_max=None, tm_parameters=None):
    from dna_design_core.kernel.public import material_id
    params={"forward_core_length":4,"reverse_core_length":4}
    result=ctx.call("pcr.simulate",inputs={"template":template,"forward":forward,"reverse":reverse},params=params)
    product=dict(result.products["product"])
    UNRELATED
    CHANGE
    primers={"schema":"primer-set-v1","length_min":4,"length_max":4,"primers":[
        {"id":"f","sequence":forward["sequence"],"core_length":4},
        {"id":"r","sequence":reverse["sequence"],"core_length":4}],"pairs":[{"id":"pcr","forward":"f","reverse":"r"}]}
    CHANGE_ORDER
    CHANGE_LENGTH
    if tm_parameters is not None:primers.update(tm_min=tm_min,tm_max=tm_max,tm_parameters=tm_parameters)
    route={"schema":"route-plan-v1","method":METHOD,"laboratory_status":"NOT_PERFORMED","reactions":[
        {"id":"pcr","method":"pcr","inputs":[material_id(template),material_id(forward),material_id(reverse)],"params":params,"product_id":material_id(result.products["product"])}]}
    return Outcome(products={"product":product},documents={"primers":primers,"route":route})
'''.replace('UNRELATED','from dna_design_core.biology.public import make_material\n    ctx.call("seq.rotate",inputs={"material":make_material("AACGTT",topology="circular",strandedness="double")},params={"origin":1})' if extra_rotation else 'pass').replace('CHANGE_ORDER','primers["primers"][0]["sequence"]="GG"+primers["primers"][0]["sequence"]' if wrong_order else 'pass').replace('CHANGE_LENGTH','primers["primers"][0]["core_length"]=3' if wrong_length else 'pass').replace('CHANGE','product["sequence"]="C"+product["sequence"][1:]' if wrong else 'pass').replace('METHOD',repr(method))
    answer={'sequence':'AACTGGACTCCGATC','topology':'linear','strandedness':'double',
            'ends':{'left':{'kind':'blunt','overhang':''},'right':{'kind':'blunt','overhang':''}},'features':[]}
    kit=build(folder/'external',[(original,body),(expected,'def model(ctx, template, forward, reverse):\n    return Outcome(products={"product":'+repr(answer)+'})\n')])
    root=folder/'run';receipts=[]
    def call(verb,**arguments):
        value=api.call(verb,root=root,kit_dirs=[kit],**arguments);receipts.append({'verb':verb,'receipt':value})
        (folder/'receipts.json').write_text(json.dumps(receipts,indent=2)+'\n',encoding='utf-8');return value
    created=call('run create',directory=root);assert not created['problems'],created
    request=goal(sources);request['targets']=[{'id':'t1','role':'construct','required':True},{'id':'t2','role':'primer_set','required':True}]
    request['constraints']=[{'id':'c1','check':'check.goal.output_present@0.0.0','params':{},'target':'t1','source_quote':'constructed','status':'active'}]
    declared=call('goal declare',request=request);assert not declared['problems'],declared
    settings={'primer_length':4}
    if thermal_window is not None:
        settings.update(tm_min=thermal_window[0],tm_max=thermal_window[1],tm_parameters={
            'dnac1_nM':'250','dnac2_nM':'0','Na_mM':'50','K_mM':'0','Tris_mM':'0',
            'Mg_mM':'0','dNTPs_mM':'0','nn_table':'DNA_NN3','saltcorr':5,'selfcomp':False})
    pipeline=plan(declared['result']['goal_digest'],[step('s1','prepare',{name:{'source':name} for name in values},params=settings)],{'step':'s1','port':'product'})
    pipeline['outputs'].append({'name':'primers','from':{'step':'s1','port':'primers'},'target':'t2'})
    submitted=call('pipeline submit',request=pipeline);assert not submitted['problems'],submitted
    executed=call('run execute');assert executed['state']=='COMPLETED',executed
    return root,kit,call,RunService(root,kit_dirs=[kit])

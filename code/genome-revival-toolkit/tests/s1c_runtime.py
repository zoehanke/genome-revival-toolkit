"""Real public-API material workflows with construction-defined fixtures."""
from copy import deepcopy
import json
from pathlib import Path
from dna_design_core.application import api
from tests.fixtures.contract_probe import action,port,build,goal,plan,step


def feature(*,strand=1,kind='misc_feature'):
    return {'start':0,'end':9,'type':kind,'label':'synthetic',
            'parts':[{'start':0,'end':9,'strand':strand}],'operator':None,'qualifiers':{'label':['synthetic']}}


def material(*,strand=1,kind='misc_feature',sequence='ATGAAATAA'):
    return {'sequence':sequence,'topology':'linear','strandedness':'double','ends':None,
            'features':[feature(strand=strand,kind=kind)]}


def run_material(folder,source,product=None,*,checks=()):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    path=folder/'synthetic.json';path.write_text(json.dumps(source,indent=2)+'\n',encoding='utf-8')
    declaration=action('copy_material',[port('material','material',input=True)],[port('product','material')])
    declaration['outputs'][0]['output_role']='component'
    returned='material' if product is None else repr(deepcopy(product))
    kit=build(folder/'external',[(declaration,'def copy_material(ctx, material):\n    return Outcome(products={"product":'+returned+'})\n')])
    root=folder/'run';receipts=[]
    def call(verb,**arguments):
        result=api.call(verb,root=root,kit_dirs=[kit],**arguments);receipts.append({'verb':verb,'receipt':result})
        (folder/'receipts.json').write_text(json.dumps(receipts,indent=2)+'\n',encoding='utf-8',newline='\n')
        return result
    created=call('run create',directory=root);assert not created['problems'],created
    request=goal([{'source_id':'template','from':str(path),'as':'material','input_origin':'user_file','declared':{}}])
    request['targets'][0]['role']='component'
    request['constraints']=[{'id':'c1','check':'check.goal.output_present@0.0.0','params':{},'target':'t1','source_quote':'constructed','status':'active'}]
    declared=call('goal declare',request=request);assert not declared['problems'],declared
    submitted=call('pipeline submit',request=plan(declared['result']['goal_digest'],[step('s1','copy_material',{'material':{'source':'template'}})],{'step':'s1','port':'product'}))
    assert not submitted['problems'],submitted
    executed=call('run execute');assert executed['state']=='COMPLETED',executed
    judged=call('judge',also=list(checks));assert not judged['problems'],judged
    verdicts={row['verdict']['check']['id']:row['verdict'] for row in judged['result']['verdicts']}
    return root,kit,call,judged,verdicts

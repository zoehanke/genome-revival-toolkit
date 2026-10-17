"""Temporary external Kit fixture. Oracles are constructed counts 8 and 3, difference 5."""
import json
from pathlib import Path


BODY='''import csv
from pathlib import Path
from dna_design_core.kernel.public import Outcome, make, core_version

def parse_counts(ctx, table):
    with Path(table).open(encoding="utf-8",newline="") as stream:
        rows=list(csv.DictReader(stream))
    counts={row["name"]:int(row["count"]) for row in rows}
    return Outcome(documents={"counts":counts})

def difference(ctx, counts):
    return Outcome(documents={"analysis":{"difference":counts["control"]-counts["test"]}},
                   unverified=["Synthetic reported counts are not verified experimental observations."])

def check_difference(ctx):
    failures=[];basis=[]
    for step in ctx.view.steps():
        if not step["completed"] or not step["definition"]["use"].startswith("toy.difference@"):continue
        counts=ctx.view.document(step["started"]["payload"]["inputs"]["counts"]["id"])
        answer=ctx.view.document(step["completed"]["payload"]["outputs"]["documents"]["analysis"][0])
        if answer["difference"]+counts["test"]!=counts["control"]:failures.append(step["definition"]["step_id"])
        basis.append(step["completed"]["hash"])
    return Outcome(verdicts=[make(check={"id":"toy.check_difference","version":core_version()},
        scope="content_model",moment="final",issuer="check_capability",subject={"kind":"run","id":ctx.view.events()[0]["run_id"]},
        outcome="FAIL" if failures or not basis else "PASS",summary="Count difference checked by additive identity.",
        evidence={"different_steps":failures},basis=basis,does_not_establish=["Any biological interpretation."])])
'''


def build(root):
    root=Path(root);(root/'capabilities').mkdir(parents=True);(root/'fixtures').mkdir();(root/'templates').mkdir()
    def write(path,value):
        (root/path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    (root/'capabilities/flow.py').write_text(BODY,encoding='utf-8',newline='\n')
    declarations=[]
    for name,inputs,outputs in [
        ('parse_counts',[{'name':'table','type':'artifact','required':True,'constraints':{},'description':'CSV with name,count; control and test rows.'}],
         [{'name':'counts','type':'document','schema_ref':'urn:grt:schema:goal-v1#/$defs/value','output_role':None}]),
        ('difference',[{'name':'counts','type':'document','required':True,'constraints':{},'schema_ref':'urn:grt:schema:goal-v1#/$defs/value','description':'Integer control and test counts.'}],
         [{'name':'analysis','type':'document','schema_ref':'urn:grt:schema:goal-v1#/$defs/value','output_role':'analysis'}]),
        ('check_difference',[],[])]:
        declaration={'schema':'capability-v1','id':'toy.'+name,'version':'0.0.0','role':'ACTION','summary':'Synthetic count fixture '+name+'.',
                     'effects':['reads_files'],'deterministic':True,'requires_runtime':[],'inputs':inputs,
                     'params':{'type':'object','properties':{},'additionalProperties':False},'outputs':outputs,'step_checks':[],
                     'final_checks':[{'check':'check.replay'},{'check':'check.lineage'},{'check':'toy.check_difference'}] if name=='difference' else [],
                     'does_not_establish':['Biological evidence.'],'source':{'algorithm_refs':[],'implemented_in':'grt_kit_toy.capabilities.flow:'+name},
                     'owner':'kit:toy','granularity':'atomic'}
        if name=='check_difference':
            declaration.update(role='CHECK',scope='content_model',evaluates_constraint=False,offline=True,
                               fixtures={'pass':'fixtures/check.pass.json','fail':'fixtures/check.fail.json'})
        write('capabilities/'+name+'.json',declaration);declarations.append('capabilities/'+name+'.json')
    write('templates/counts.json',{'schema':'pipeline-template-v1','version':1,'goal_digest':'{{goal_digest}}',
          'steps':[{'step_id':'s1','use':'toy.parse_counts','inputs':{'table':{'source':'{{source_id}}'}},'params':{},'why':'Parse synthetic counts.'},
                   {'step_id':'s2','use':'toy.difference','inputs':{'counts':{'step':'s1','port':'counts'}},'params':{},'why':'Compute the count difference.'}],
          'outputs':[{'name':'result','from':{'step':'s2','port':'analysis'},'target':'t1'}],
          'params_schema':{'type':'object','properties':{'goal_digest':{'type':'string','description':'Current goal digest.'},'source_id':{'type':'string','description':'Registered CSV source id.'}},'required':['goal_digest','source_id'],'additionalProperties':False}})
    write('kit.json',{'schema':'kit-v1','name':'toy','title':'Synthetic count fixture','version':'0.0.0',
                     'requires_core':{'minimum':'0.0.0','maximum_exclusive':'1.0.0'},'contributes':{'capabilities':declarations,'knowledge':[],'templates':['templates/counts.json'],'text':[]},
                     'does_not_establish':['Biological evidence.'],'review':'knowledge/review/'})
    (root/'SKILL.md').write_text('---\nname: toy-counts\ndescription: Use only for the synthetic S1 count test, never for biological evidence.\n---\n',encoding='utf-8',newline='\n')
    for variant,value in [('pass',5),('fail',6)]:
        write('fixtures/check.'+variant+'.json',{'oracle':{'kind':'construction','reason':'Eight minus three is five.'},
              'counts':{'control':8,'test':3},'difference':value,'expected':'PASS' if variant=='pass' else 'FAIL'})
    return root

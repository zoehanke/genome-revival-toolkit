"""Public S1.2 CLI boundary cases, with immutable requests and raw receipts."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2];CLI=ROOT/'src/dna_design_core/application/cli.py'
sys.path.insert(0,str(ROOT/'tests'))
from fixtures.contract_probe import (action, port, build, goal, plan, step, rule,
    inline_definitions, knowledge_definitions, model_definitions, materials_definitions)


class Harness:
    def __init__(self,folder,definitions,*,knowledge=None,goal_request=None):
        self.folder=Path(folder);self.folder.mkdir(parents=True,exist_ok=False)
        self.kit=build(self.folder/'external',definitions,knowledge=knowledge);self.run=self.folder/'run';self.receipts=[]
        self.command('run','create',self.run)
        declared=self.command('goal','declare',request=goal_request or goal())
        self.digest=declared['result']['goal_digest']

    def command(self,*arguments,request=None,expected=0,with_kit=True):
        arguments=list(map(str,arguments))
        if arguments[:2]!=['run','create'] and arguments[0]!='describe':arguments+=['--run',str(self.run)]
        if with_kit:arguments+=['--kit-dir',str(self.kit)]
        if request is not None:
            path=self.folder/('request-'+str(len(self.receipts))+'.json')
            path.write_text(json.dumps(request,indent=2)+'\n',encoding='utf-8',newline='\n');arguments+=['--request',str(path)]
        result=subprocess.run([sys.executable,'-X','utf8','-B',str(CLI),*arguments],cwd=self.folder,capture_output=True,text=True,encoding='utf-8')
        receipt=json.loads(result.stdout)
        self.receipts.append({'arguments':arguments,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'receipt':receipt})
        (self.folder/'receipts.json').write_text(json.dumps(self.receipts,indent=2)+'\n',encoding='utf-8',newline='\n')
        assert result.returncode==expected,(arguments,result.returncode,receipt)
        return receipt

    def submit(self,steps,output):
        return self.command('pipeline','submit',request=plan(self.digest,steps,output))

    def events(self):return [json.loads(line) for line in (self.run/'journal.ndjson').read_text(encoding='utf-8').splitlines()]


def run_case(name,folder):
    folder=Path(folder).resolve();folder.mkdir(parents=True,exist_ok=False);summaries=[]
    if name=='inline':
        for variant,options,state,code in [('valid',{},'COMPLETED',None),('bad_output',{'bad_output':True},'HALTED','CAPABILITY_OUTPUT_INVALID'),('bad_input',{'strict_input':True},'HALTED','PLAN_INPUT_UNBOUND')]:
            h=Harness(folder/variant,inline_definitions(**options))
            h.submit([step('s1','produce'),step('s2','consume',{'document':{'step':'s1','port':'document'}})],{'step':'s2','port':'number'})
            receipt=h.command('run','execute',expected=1 if code else 0);assert receipt['state']==state,receipt
            if code:assert receipt['problems'][0]['code']==code
            else:
                completed=[e['payload'] for e in h.events() if e['type']=='step.completed'];assert completed[-1]['values']=={'number':7}
                identity=completed[0]['outputs']['documents']['document'][0]
                assert json.loads((h.run/'store/documents'/(identity+'.json')).read_text(encoding='utf-8'))=={'count':7}
            if variant=='bad_output':assert not any(json.loads(p.read_text(encoding='utf-8'))=={'count':'seven'} for p in (h.run/'store/documents').glob('*.json'))
            summaries.append({'case':variant,'state':state,'failure':code,'commands':len(h.receipts)})
    elif name=='knowledge':
        for variant in ['frozen','corrupt','foreign']:
            h=Harness(folder/variant,knowledge_definitions(),knowledge={'knowledge/table.json':rule(ROOT)})
            h.submit([step('s1','read',params={'pack':'kit:other/knowledge/table.json'} if variant=='foreign' else {})],{'step':'s1','port':'number'})
            if variant=='frozen':
                path=h.kit/'knowledge/table.json';changed=json.loads(path.read_text(encoding='utf-8'));changed['parameters']['count']=42
                path.write_text(json.dumps(changed),encoding='utf-8')
            elif variant=='corrupt':
                catalog=json.loads((h.run/h.events()[0]['payload']['catalog_ref']).read_text(encoding='utf-8'))
                path=h.run/'store/documents'/(catalog['knowledge'][0]['digest']+'.json');changed=json.loads(path.read_text(encoding='utf-8'))
                changed['parameters']['count']=9;path.write_text(json.dumps(changed),encoding='utf-8')
            receipt=h.command('run','execute',expected=0 if variant=='frozen' else 1)
            if variant=='frozen':
                assert receipt['state']=='COMPLETED'
                assert next(e['payload']['values'] for e in h.events() if e['type']=='step.completed')=={'number':7}
                judged=h.command('judge','--also','contract_probe.check_read')
                verdict=next(v['verdict'] for v in judged['result']['verdicts'] if v['verdict']['check']['id']=='contract_probe.check_read')
                assert verdict['outcome']=='PASS' and verdict['evidence']['count']==7,verdict
            else:assert receipt['problems'][0]['code']==('STORE_CORRUPT' if variant=='corrupt' else 'KNOWLEDGE_SOURCE_INVALID')
            summaries.append({'case':variant,'state':receipt['state'],'commands':len(h.receipts)})
    elif name=='model':
        for variant,changes,outcome in [('equal',{},'PASS'),('annotations',{'feature':True},'PASS'),('one_base',{'sequence':'ACGA'},'FAIL'),('topology',{'topology':'circular'},'FAIL'),('ends',{'ends':{'left':'A','right':'T'}},'FAIL')]:
            case=folder/variant;case.mkdir();source=case/'material.json';source.write_text('{"sequence":"ACGT"}',encoding='utf-8')
            request=goal([{'source_id':'template','from':str(source),'as':'material','input_origin':'user_file','declared':{}}])
            h=Harness(case/'cli',model_definitions(**changes),goal_request=request)
            h.submit([step('s1','original',{'template':{'source':'template'}},{'offset':2,'unused':13})],{'step':'s1','port':'product'})
            h.command('run','execute');judged=h.command('judge')
            verdict=next(v['verdict'] for v in judged['result']['verdicts'] if v['verdict']['check']['id']=='check.model_agreement')
            assert verdict['outcome']==outcome,verdict
            assert all(e['payload']['capability']['id']!='contract_probe.predict' for e in h.events() if e['type']=='call.recorded')
            summaries.append({'case':variant,'expected':outcome,'actual':verdict['outcome'],'commands':len(h.receipts)})
        for variant in ['unknown_input','unknown_parameter','no_product']:
            rows=model_definitions()
            if variant=='unknown_input':rows[1][0]['inputs'][0]['name']='absent'
            elif variant=='unknown_parameter':rows[1][0]['params']['properties']['absent']={'type':'integer'}
            else:rows[0][0]['outputs'][0]['name']='result'
            h=Harness(folder/variant,rows)
            diagnostics=h.receipts[0]['receipt']['result']['kit_diagnostics']
            assert any(p['code']=='KIT_MANIFEST_INVALID' and 'model' in p['message'].lower() for p in diagnostics),diagnostics
            receipt=h.command('describe','capability','contract_probe.original',expected=1)
            assert receipt['problems'][0]['code']=='CAPABILITY_UNKNOWN'
            summaries.append({'case':variant,'rejected':True,'commands':len(h.receipts)})
    elif name=='materials':
        for variant,consumer,reference,number in [('collection','total',{'step':'s1','port':'pieces'},8),('item','single',{'step':'s1','port':'pieces','index':1},4)]:
            h=Harness(folder/variant,materials_definitions())
            h.submit([step('s1','pieces'),step('s2',consumer,{'pieces' if consumer=='total' else 'piece':reference})],{'step':'s2','port':'number'})
            h.command('run','execute');done=[e['payload'] for e in h.events() if e['type']=='step.completed'];assert done[-1]['values']=={'number':number}
            judged=h.command('judge');selected={v['verdict']['check']['id']:v['verdict']['outcome'] for v in judged['result']['verdicts']}
            assert selected['check.lineage']=='PASS' and selected['check.replay']=='PASS',selected
            summaries.append({'case':variant,'number':number,'commands':len(h.receipts)})
        h=Harness(folder/'lists_rejected',materials_definitions());before=(h.run/'journal.ndjson').read_bytes()
        for ref in [[{'source':'one'},{'source':'two'}],[{'step':'s1','port':'pieces'},{'step':'s2','port':'pieces'}],{'literal':[{'sequence':'ACGT'}]}]:
            request=plan(h.digest,[step('s1','pieces'),step('s2','total',{'pieces':ref})],{'step':'s2','port':'number'})
            receipt=h.command('pipeline','submit',request=request,expected=1)
            assert receipt['problems'][0]['category']=='INVALID_INPUT'
            assert 'materials' in receipt['result']['failure']['details']['problems'][0]['message']
            assert (h.run/'journal.ndjson').read_bytes()==before
        summaries.append({'case':'lists_rejected','commands':len(h.receipts)})
    elif name=='loader':
        h=Harness(folder/'external',inline_definitions())
        described=h.command('describe','capabilities');assert any(v['id']=='contract_probe.produce' for v in described['result']['description'])
        h.submit([step('s1','produce'),step('s2','consume',{'document':{'step':'s1','port':'document'}})],{'step':'s2','port':'number'})
        h.command('run','execute')
        removed=h.command('describe','capabilities',with_kit=False);assert not any(v['owner']=='kit:contract_probe' for v in removed['result']['description'])
        summaries.append({'case':'external_load_run_remove','commands':len(h.receipts)})
    else:raise ValueError(name)
    summary={'group':name,'passed':True,'cases':summaries,'commands':sum(v['commands'] for v in summaries)}
    (folder/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8',newline='\n')
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--case',choices=['inline','knowledge','model','materials','loader'],required=True);args=parser.parse_args()
    print(json.dumps(run_case(args.case,args.out),indent=2))

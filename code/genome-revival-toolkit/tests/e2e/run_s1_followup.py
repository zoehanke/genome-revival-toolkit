"""S1.1 regressions through the public CLI; retain requests and raw receipts."""
import argparse
import copy
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
CLI=ROOT/'src/dna_design_core/application/cli.py'


def run_case(name,folder):
    folder=Path(folder).resolve();folder.mkdir(parents=True,exist_ok=False)
    run=folder/'run';request=folder/'request.json';receipts=[]
    def write(value):
        nonlocal request
        request=folder/('request-'+str(len(receipts))+'.json')
        request.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
        return request
    def command(*arguments,expected=0):
        result=subprocess.run([sys.executable,'-X','utf8','-B',str(CLI),*map(str,arguments)],cwd=folder,capture_output=True,text=True,encoding='utf-8')
        receipt=json.loads(result.stdout)
        receipts.append({'arguments':list(map(str,arguments)),'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'receipt':receipt})
        (folder/'receipts.json').write_text(json.dumps(receipts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
        assert result.returncode==expected,(name,arguments,result.returncode,receipt)
        return receipt
    command('run','create',run)
    goal={'schema':'goal-v1','version':1,'parent_digest':None,'original_request':'Compute the synthetic reverse complement.',
          'sources':[],'declared_context':[],'targets':[{'id':'t1','role':'analysis','required':True}],
          'constraints':[{'id':'c1','check':'check.goal.output_present@0.0.0','params':{},'target':'t1','source_quote':'reverse complement','status':'active'}],'intents':[]}
    if name=='origin':
        before=(run/'journal.ndjson').read_bytes()
        for supplied in ['host_derived','user_quoted',None]:
            goal['constraints'][0]['origin']=supplied
            receipt=command('goal','declare','--run',run,'--request',write(goal),expected=1)
            assert receipt['problems'][0]['category']=='INVALID_INPUT'
            assert receipt['problems'][0]['location']=='/constraints/0/origin'
            assert (run/'journal.ndjson').read_bytes()==before
    elif name=='invalid_params':
        bad=[({'check':'check.goal.output_present@0.0.0','params':{'field':'sequence'}},'/constraints/0/params/field'),
             ({'params':{'fields':'sequence'}},'/constraints/0/params/fields'),
             ({'params':{'fields':[13]}},'/constraints/0/params/fields/0'),
             ({'check':'missing.check_unknown@0.0.0'},'/constraints/0/check'),
             ({'check':'seq.reverse_complement@0.0.0'},'/constraints/0/check'),
             ({'check':'check.goal.nonempty@0.0.0'},'/constraints/0/check'),
             ({'check':'check.goal.output_present@9.0.0'},'/constraints/0/check')]
        before=(run/'journal.ndjson').read_bytes()
        for changes,location in bad:
            value=copy.deepcopy(goal);value['constraints'][0].update(changes)
            receipt=command('goal','declare','--run',run,'--request',write(value),expected=1)
            assert receipt['problems'][0]['category']=='INVALID_INPUT'
            assert receipt['problems'][0]['location']==location,receipt
            assert (run/'journal.ndjson').read_bytes()==before
        assert not any(e['type']=='goal.declared' for e in map(json.loads,before.splitlines()))
        declared=command('goal','declare','--run',run,'--request',write(goal))
        amended=copy.deepcopy(goal);amended.update(version=2,parent_digest=declared['result']['goal_digest'],reason='Invalid parameter control on goal amend.')
        amended['constraints'][0]['params']={'field':'sequence'};before=(run/'journal.ndjson').read_bytes()
        receipt=command('goal','amend','--run',run,'--request',write(amended),expected=1)
        assert receipt['problems'][0]['category']=='INVALID_INPUT' and receipt['problems'][0]['location']=='/constraints/0/params/field'
        assert (run/'journal.ndjson').read_bytes()==before
    elif name=='schema_recovery':
        before=(run/'journal.ndjson').read_bytes()
        missing=copy.deepcopy(goal);missing.pop('targets')
        malformed=copy.deepcopy(goal);malformed['constraints']=None
        for value in [missing,malformed,[]]:
            receipt=command('goal','declare','--run',run,'--request',write(value),expected=1)
            assert receipt['problems'][0]['category']=='INVALID_INPUT'
            for recovery in [receipt['problems'][0]['recovery'],receipt['result']['failure']['recovery']]:
                assert 'goal-v1' in recovery and 'pipeline-v1' not in recovery,recovery
            assert (run/'journal.ndjson').read_bytes()==before
    elif name in {'fields','fields_missing'}:
        variant='fail' if name=='fields_missing' else 'pass'
        fixture=json.loads((ROOT/'tests/fixtures/checks'/('check.goal.output_present.fields.'+variant+'.json')).read_text(encoding='utf-8'))
        goal['constraints'][0]['params']=fixture['params']
        goal['constraints'].append({**goal['constraints'][0],'id':'c2','source_quote':'A statement not present in the original request.'})
        declared=command('goal','declare','--run',run,'--request',write(goal))
        stored=json.loads((run/'store/documents'/(declared['result']['goal_digest']+'.json')).read_text(encoding='utf-8'))
        assert [c['origin'] for c in stored['constraints']]==['user_quoted','host_derived']
        assert all('origin' not in c for c in json.loads(request.read_text(encoding='utf-8'))['constraints'])
        plan={'schema':'pipeline-v1','version':1,'goal_digest':declared['result']['goal_digest'],
              'steps':[{'step_id':'s1','use':'seq.reverse_complement','inputs':{'sequence':{'literal':fixture['input_sequence']}},'params':{},'why':'Compute the hand-constructed reverse complement.'}],
              'outputs':[{'name':'result','from':{'step':'s1','port':'result'},'target':'t1'}]}
        command('pipeline','submit','--run',run,'--request',write(plan));command('run','execute','--run',run)
        judged=command('judge','--run',run)
        verdicts=[r['verdict'] for r in judged['result']['verdicts'] if r['verdict']['check']['id']==fixture['check']]
        assert len(verdicts)==2 and all(v['outcome']==fixture['expected'] for v in verdicts),verdicts
        sealed=command('seal','--run',run,expected=10 if variant=='fail' else 0)
        assert sealed['result']['sealed']==(variant=='pass')
        if variant=='pass':
            package=Path(sealed['result']['manifest']).parent
            assert json.loads((package/'result.json').read_text(encoding='utf-8'))==fixture['expected_document']
            verified=command('verify',package);assert verified['result']['verified']
        else:
            assert all(row['outcome']=='FAIL' for row in sealed['result']['unsatisfied'])
            assert not list((run/'sealed').glob('*'))
    else:raise ValueError('Unknown constructed case.')
    summary={'case':name,'passed':True,'commands':len(receipts)}
    (folder/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8',newline='\n')
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--case',choices=['origin','invalid_params','fields','fields_missing','schema_recovery'],default='origin');args=parser.parse_args()
    print(json.dumps(run_case(args.case,args.out),indent=2))

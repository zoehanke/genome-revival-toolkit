"""Public-CLI S1 examples with constructed oracles and a zero-connection guard."""
import argparse
import copy
import json
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'tests'))
from fixtures.toy.build import build
from dna_design_core.kernel import schemas
from dna_design_core.storage.chain import read

CLI=ROOT/'src/dna_design_core/application/cli.py'
GUARD=Path(__file__).with_name('network_guard.py')


def run_examples(output):
    output=Path(output).resolve()
    if output.exists():raise ValueError('Choose a new output directory; earlier evidence is retained.')
    output.mkdir(parents=True);receipts=[];network=[]
    def write(path,value):
        path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n');return path
    def command(cwd,*arguments,expected=0):
        audit=output/('network-'+str(len(network))+'.json')
        result=subprocess.run([sys.executable,'-X','utf8','-B',str(GUARD),str(audit),str(CLI),*map(str,arguments)],cwd=cwd,capture_output=True,text=True,encoding='utf-8')
        receipt=json.loads(result.stdout);schemas.require('receipt-v1',receipt)
        receipts.append({'arguments':list(map(str,arguments)),'exit_code':result.returncode,'receipt':receipt})
        write(output/'receipts.json',receipts)
        attempts=json.loads(audit.read_text(encoding='utf-8'))['attempts'];network.append(attempts)
        assert attempts==0,(arguments,attempts)
        assert result.returncode==expected,(arguments,result.returncode,receipt)
        return receipt
    def goal_request(text,sources=()):
        return {'schema':'goal-v1','version':1,'parent_digest':None,'original_request':text,'sources':list(sources),'declared_context':[],
                'targets':[{'id':'t1','role':'analysis','required':True}],
                'constraints':[{'id':'c1','check':'check.goal.output_present@0.0.0','params':{},'target':'t1','source_quote':text,'status':'active'}],'intents':[]}
    summaries={}
    for case in ['b1','b3']:
        folder=output/case;folder.mkdir();run=folder/'run';request=folder/'request.json'
        kit=build(folder/'external-kit') if case=='b3' else None;flags=['--kit-dir',kit] if kit else []
        command(folder,'doctor',*flags)
        listed=command(folder,'describe','capabilities',*flags)
        if kit:
            assert any(c['id']=='toy.difference' for c in listed['result']['description'])
            removed=command(folder,'describe','capabilities')
            assert not any(c['id'].startswith('toy.') for c in removed['result']['description'])
            bad=folder/'bad-kit';bad.mkdir();(bad/'kit.json').write_text('{}',encoding='utf-8')
            diagnostic=command(folder,'describe','kits','--kit-dir',bad,*flags)
            assert diagnostic['result']['kit_diagnostics'][0]['code']=='KIT_MANIFEST_INVALID'
        created=command(folder,'run','create',run,*flags)
        if kit:assert created['result']['notices']
        sources=[]
        if kit:
            (folder/'counts.csv').write_text('name,count\ncontrol,8\ntest,3\n',encoding='utf-8',newline='\n')
            sources=[{'source_id':'table','from':'counts.csv','as':'artifact','input_origin':'researcher_observation','declared':{}}]
        declared=command(folder,'goal','declare','--run',run,'--request',write(request,goal_request('Compute the reverse complement.' if case=='b1' else 'Report the synthetic count difference.',sources)),*flags)
        if case=='b1':
            steps=[{'step_id':'s1','use':'seq.reverse_complement','inputs':{'sequence':{'literal':'AGTCAGAA'}},'params':{},
                    'why':'Compute the reverse complement of the constructed literal.','expects':{'on':{'step':'s1','port':'result','pointer':'/sequence'},'op':'equals','value':'TTCTGACT'}}]
            output_ref={'step':'s1','port':'result'}
        else:
            steps=[{'step_id':'s1','use':'toy.parse_counts','inputs':{'table':{'source':'table'}},'params':{},'why':'Parse the synthetic reported counts.'},
                   {'step_id':'s2','use':'toy.difference','inputs':{'counts':'@s1.counts'},'params':{},'why':'Compute the difference, retaining the intentionally wrong host expectation.',
                    'expects':{'on':{'step':'s2','port':'analysis','pointer':'/difference'},'op':'equals','value':6}}]
            output_ref={'step':'s2','port':'analysis'}
        plan={'schema':'pipeline-v1','version':1,'goal_digest':declared['result']['goal_digest'],'steps':steps,
              'outputs':[{'name':'result','from':output_ref,'target':'t1'}]}
        if kit:
            instantiated=command(folder,'template','instantiate','toy.counts','--request',write(request,{'goal_digest':declared['result']['goal_digest'],'source_id':'table'}),*flags)
            self_contained=instantiated['result']['draft']
            assert self_contained['library_ref']['version']=='0.0.0' and self_contained['version']==1
            assert self_contained['steps'][0]['inputs']['table']=={'source':'table'}
            plan['library_ref']=self_contained['library_ref']
        badplan=copy.deepcopy(plan)
        if case=='b1':badplan['steps'][0]['inputs']['sequence']['literal']='AGTZAGAA'
        else:badplan['steps'][-1]['params']['unknown']=1
        before=(run/'journal.ndjson').read_bytes()
        command(folder,'pipeline','submit','--run',run,'--request',write(request,badplan),*flags,expected=1)
        assert (run/'journal.ndjson').read_bytes()==before
        admitted=command(folder,'pipeline','submit','--run',run,'--request',write(request,plan),*flags)
        assert not any(e['type']=='step.started' for e in read(run/'journal.ndjson'))
        executed=command(folder,'run','execute','--run',run,*flags,expected=1 if kit else 0)
        if kit:
            assert executed['state']=='HALTED'
            events=read(run/'journal.ndjson');failed=next(e for e in events if e['type']=='step.failed')
            new=copy.deepcopy(steps[1]);new.update(step_id='s3',why='Correct the host expectation; preserve the failed step.')
            new['expects'].update(on={'step':'s3','port':'analysis','pointer':'/difference'},value=5)
            revision={'schema':'pipeline-revision-v1','expected_digest':admitted['result']['pipeline_digest'],
                      'trigger':{'kind':'step_failed','step_id':'s2','failure_code':'STEP_EXPECTATION_FAILED','event_refs':[failed['hash']]},
                      'reason':'The hand-constructed difference is five, not six.',
                      'operations':[{'op':'add_step','after':'s2','step':new},{'op':'supersede_step','step_id':'s2','by':'s3'},
                                    {'op':'set_outputs','outputs':[{'name':'result','from':{'step':'s3','port':'analysis'},'target':'t1'}]}]}
            command(folder,'pipeline','revise','--run',run,'--request',write(request,revision),*flags)
            command(folder,'run','execute','--run',run,*flags)
            assert failed in read(run/'journal.ndjson')
        command(folder,'status','--run',run,*flags)
        judgement=command(folder,'judge','--run',run,*flags)
        assert judgement['result']['unsatisfied']==[],judgement
        sealed=command(folder,'seal','--run',run,*flags)
        package=Path(sealed['result']['manifest']).parent
        expected={'sequence':'TTCTGACT'} if case=='b1' else {'difference':5}
        assert json.loads((package/'result.json').read_text(encoding='utf-8'))==expected
        command(folder,'record','render','--run',run,*flags)
        command(folder,'verify',run,*flags)
        copied=folder/'portable'/package.name;shutil.copytree(package,copied)
        retained=folder/'run-retained'
        assert run.resolve().is_relative_to(output) and retained.resolve().is_relative_to(output)
        run.rename(retained)
        verified=command(folder,'verify',copied,*flags)
        assert verified['result']['verified'],verified
        assert not any((copied/'store/materials').glob('*.json'))
        manifest=json.loads((copied/'manifest.json').read_text(encoding='utf-8'))
        assert hashlib.sha256((copied/'manifest.json').read_bytes()).hexdigest()==copied.name
        assert 'seal_id' not in manifest and all(row['path']!='manifest.json' for row in manifest['files'])
        journal=read(copied/'journal-until-seal.ndjson')
        assert sum('environment' in event['payload'] for event in journal)==1
        assert journal[-1]['hash']==manifest['journal_head']
        for event in journal:
            assert len(event['hash'])==64 and set(event['hash'])<=set('0123456789abcdef')
            if event['type']=='step.started':assert all(set(row)=={'id','origin'} for row in event['payload']['inputs'].values())
        card=(copied/'views/runcard.html').read_text(encoding='utf-8')
        assert package.name not in card
        assert all(row in (copied/'views/report.md').read_text(encoding='utf-8') for row in manifest['not_verified'])
        if kit:assert 'data-basis="hash_equal"' in card
        assert 'AGTCAGAA' not in card and 'TTCTGACT' not in card
        summaries[case]={'portable_package':copied.relative_to(output).as_posix(),'run':retained.relative_to(output).as_posix(),
                         'expected':expected,'verified':True,'release_id':manifest['release_id']}
    # Exercise the other closed verbs under the same socket guard.
    auxiliary=output/'auxiliary';auxiliary.mkdir();run=auxiliary/'run';request=auxiliary/'request.json'
    command(auxiliary,'run','create',run)
    goal=goal_request('Record a synthetic request.');declared=command(auxiliary,'goal','declare','--run',run,'--request',write(request,goal))
    goal.update(version=2,parent_digest=declared['result']['goal_digest'],reason='Retain the same goal with a recorded amendment.')
    command(auxiliary,'goal','amend','--run',run,'--request',write(request,goal))
    command(auxiliary,'declare','--run',run,'--request',write(request,{'text':'Synthetic host statement.','origin':'organized_summary'}))
    command(auxiliary,'review','sign','--run',run,'--request',write(request,{}),expected=1)
    command(auxiliary,'run','abandon','--run',run,'--reason','Synthetic closed-verb test.')
    for kind in ['checks','goal-kinds','templates','vocab']:command(auxiliary,'describe',kind)
    summary={'cases':summaries,'commands':len(receipts),'connection_attempts':sum(network),'official_gitlab_ci':'not executed','github_ci':'not run',
             'limits':['Synthetic computational examples only.','No real Kit science or wet experiment was validated.']}
    write(output/'SUMMARY.json',summary)
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True)
    print(json.dumps(run_examples(parser.parse_args().out),ensure_ascii=False,indent=2))

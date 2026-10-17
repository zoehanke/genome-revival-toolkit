"""Three sealed Kit runs through the public, network-blocked CLI only.

Reference files and primers pass through the unmodified D11 handoff templates.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
GUARD=ROOT/'tests/e2e/network_guard.py'
CLI=ROOT/'src/dna_design_core/application/cli.py'


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8');return path


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def produced_file(package,step):
    events=[json.loads(line) for line in (package/'journal-until-seal.ndjson').read_text(encoding='utf-8').splitlines()]
    row=next(e['payload'] for e in events if e['type']=='step.completed' and e['payload']['step_id']==step)
    return package/row['outputs']['artifacts'][0]['run_path']


def goal(sources,targets,constraints=None):
    version=json.loads((ROOT/'VERSIONS.json').read_text(encoding='utf-8'))['core']
    constraints=deepcopy(constraints or [{'id':'present','check':'check.goal.output_present','params':{},'target':targets[0][0],'source_quote':'report result','status':'active'}])
    for row in constraints:row['check']+='@'+version
    return {'schema':'goal-v1','version':1,'parent_digest':None,
            'original_request':'Synthetic computational chain; laboratory steps PLANNED / NOT_PERFORMED.',
            'sources':[{'source_id':name,'from':str(path.relative_to(ROOT)),'as':'artifact','input_origin':'user_file','declared':{}} for name,path in sources.items()],
            'declared_context':[],'targets':[{'id':name,'role':role,'required':True} for name,role in targets],
            'constraints':constraints,'intents':[]}


class Story:
    def __init__(self,output,resume=False):
        self.root=output.resolve();self.resume=resume
        if not resume:self.root.mkdir(parents=True,exist_ok=False)
        self.receipts=json.loads((self.root/'receipts.json').read_text(encoding='utf-8')) if resume else []
    def command(self,*args,expected=0):
        index=len(self.receipts);audit=self.root/f'network-{index:03}.json'
        completed=subprocess.run([sys.executable,'-X','utf8','-B',str(GUARD),str(audit),str(CLI),*map(str,args)],
                                 cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
        # Original raw outputs stay outside source commits. Public receipts below
        # replace only local display paths; sealed bytes are never changed.
        raw=ROOT/'dist/chain-story-raw'/self.root.name;raw.mkdir(parents=True,exist_ok=True)
        (raw/f'{index:03}.stdout.txt').write_text(completed.stdout,encoding='utf-8')
        (raw/f'{index:03}.stderr.txt').write_text(completed.stderr,encoding='utf-8')
        value=json.loads(completed.stdout);network=json.loads(audit.read_text(encoding='utf-8'))
        row={'arguments':[str(a).replace(str(ROOT),'<project>') for a in args],'exit_code':completed.returncode,
             'receipt':value,'network':network}
        self.receipts.append(row)
        public=json.loads(json.dumps(self.receipts).replace(str(ROOT).replace('\\','\\\\'),'<project>'))
        write(self.root/'receipts.json',public)
        assert network['attempts']==0,row
        allowed={expected} if isinstance(expected,int) else set(expected)
        assert completed.returncode in allowed,{'exit':completed.returncode,'receipt':value,'stderr':completed.stderr}
        return value
    def request(self,name,value):return write(self.root/'requests'/name,value)
    def execute(self,name,request,template,settings,adapt=None,mutate=None):
        previous=list((self.root/name/'portable').glob('*')) if self.resume and not mutate else []
        if previous:
            assert len(previous)==1
            verified=self.command('verify',previous[0]);assert verified['result']['verified'],verified
            return previous[0]
        run=self.root/name/'run';self.command('run','create',run)
        declared=self.command('goal','declare','--run',run,'--request',self.request(name+'-goal.json',request))
        settings={'goal_digest':declared['result']['goal_digest'],**settings}
        instantiated=self.command('template','instantiate',template,'--run',run,'--request',self.request(name+'-template.json',settings))
        plan=instantiated['result']['draft']
        if adapt:adapt(plan)
        self.command('pipeline','submit','--run',run,'--request',self.request(name+'-plan.json',plan))
        if mutate:mutate(run)
        executed=self.command('run','execute','--run',run,expected=1 if mutate else 0)
        if mutate:
            # D6 resolves input hashes before step.started. The current failure
            # state can still be RUNNING; C13 records it without asserting a
            # lifecycle transition not required by this negative control.
            assert executed['result']['failure']['code']=='SOURCE_CHANGED' and executed['problems'],executed
            return run
        self.command('judge','--run',run)
        sealed=self.command('seal','--run',run);assert sealed['result']['sealed'],sealed
        package=Path(sealed['result']['manifest']).parent
        self.command('verify',run)
        portable=self.root/name/'portable'/package.name;portable.parent.mkdir(parents=True)
        shutil.copytree(package,portable)
        retained=run.with_name('original-run-retained')
        assert run.resolve().is_relative_to(self.root) and retained.resolve().is_relative_to(self.root)
        run.rename(retained)
        checked=self.command('verify',portable);assert checked['result']['verified'],checked
        return portable


def run(output,resume=False,gene_codon='GCT'):
    story=Story(output,resume=resume);root=story.root;inputs=root/'inputs';inputs.mkdir(exist_ok=resume)
    rng=random.Random(2026101701)
    reference=''.join(rng.choice('ACGT') for _ in range(800))
    # Construct a 120 nt synthetic ORF at the chosen locus after generating
    # the random reference. Function of this model gene is not asserted.
    reference=reference[:300]+'ATG'+gene_codon*38+'TAA'+reference[420:]
    marker='ATG'+'AAA'*30+'TAA';start,end,arm=300,420,50
    donor=reference[start-arm:start]+marker+reference[end:end+arm]
    for name,sequence in [('reference',reference),('marker',marker)]:
        (inputs/(name+'.fasta')).write_text('>synthetic_'+name+'\n'+sequence+'\n',encoding='utf-8')
    targets=[('donor','construct'),('primers','primer_set'),('assay','analysis'),('handoff','analysis')]
    constraints=[{'id':'exact','check':'check.goal.exact_sequence','params':{'sequence':donor},'target':'donor','source_quote':'constructed donor with two 50 bp arms','status':'active'}]
    def export_references(plan):
        next(o for o in plan['outputs'] if o['target']=='handoff')['name']='identity-handoff.json'
    construct=story.execute('construct',goal({'input_reference':inputs/'reference.fasta','input_cargo':inputs/'marker.fasta'},targets,constraints),
        'construct.prepare_gibson',{'reference_source':'input_reference','cargo_source':'input_cargo','donor_target':'donor','primers_target':'primers',
        'assay_target':'assay','handoff_target':'handoff','start':start,'end':end,'arm_length':arm,'cargo_start':0,'cargo_end':len(marker),
        'primer_length':20,'overlap':20},export_references)
    handoff=construct/'identity-handoff.json';h=json.loads(handoff.read_text(encoding='utf-8'))
    oligos={r['id']:r['sequence'] for r in h['primers']}
    for name in ('left_forward','right_reverse'):
        (inputs/(name+'.fasta')).write_text('>synthetic_'+name+'\n'+oligos[name]+'\n',encoding='utf-8')
    sources={'original':construct/'identity_original.gb','edited':construct/'identity_edited.gb','handoff':handoff}
    settings={n+'_source':n for n in ('original','edited','handoff')}
    settings.update(original_topology='linear',edited_topology='linear',target='table',assay_id='flanking',forward_id='left_forward',reverse_id='right_reverse')
    identity=story.execute('identity',goal(sources,[('table','analysis')]),'genome-identity.from_handoff',settings)
    predictions=identity/'identity-expected-results.json'
    # The numbers and reference identities below follow the predeclared edit,
    # not the predicted table: external sites 230..250 and 470..490.
    observations={'observations':[{'id':'fusion1','group':'fusion','colonies':8,'unit':'colony','plated_volume_uL':'100'},
                                  {'id':'control1','group':'control','colonies':30,'unit':'colony','plated_volume_uL':'100'}],
                  'genotype_results':[{'sample_id':'synthetic_'+name,'assay_id':'flanking','background_id':name,
                    'reference_sha256':sha(produced_file(construct,name+'_file')),'result':'positive','control_status':'passed',
                    'observed_band_bp':size,'band_tolerance_bp':0} for name,size in [('original',260),('edited',236)]],
                  'functional_results':[],'observation_origin':'SYNTHETIC_NOT_EXPERIMENTAL'}
    observed=write(inputs/'observations.json',observations)
    evidence_settings={'source_id':'observations','observation_origin':'SYNTHETIC_NOT_EXPERIMENTAL',
                       'predictions_source':'predictions','comparisons':[{'experiment_group':'fusion','control_group':'control'}]}
    evidence=story.execute('evidence',goal({'observations':observed,'predictions':predictions},[('t1','analysis')]),
        'revival-evidence.assess_predictions',evidence_settings)
    def tamper(run):
        path=next((run/'inputs/handoff').iterdir());data=path.read_bytes();offset=data.index(b'"sha256":"')+10
        changed=data[:offset]+(b'0' if data[offset:offset+1]!=b'0' else b'1')+data[offset+1:]
        assert len(changed)==len(data) and sum(a!=b for a,b in zip(data,changed))==1
        path.write_bytes(changed)
    rejected=story.execute('tampered-handoff-byte',goal(sources,[('table','analysis')]),'genome-identity.from_handoff',settings,mutate=tamper)
    story.command('seal','--run',rejected,expected=1)
    # Independently constructed, valid external prediction document, referring
    # to another synthetic background. It must not support the original assays.
    foreign={'schema':'identity-expected-results-v1','assay_id':'flanking','backgrounds':[]}
    for name,spacing in [('original',300),('edited',360)]:
        sequence=oligos['left_forward']+'C'*spacing+oligos['right_reverse'].translate(str.maketrans('ACGT','TGCA'))[::-1]
        path=inputs/('foreign-'+name+'.fasta');path.write_text('>foreign_synthetic\n'+sequence+'\n',encoding='utf-8')
        foreign['backgrounds'].append({'id':name,'reference_sha256':sha(path),'primer_pair':['left_forward','right_reverse'],
            'expected':{'product_count':1,'product_bp':spacing+40,'status':'DISTINGUISHABLE'}})
    foreign_file=write(inputs/'foreign-predictions.json',foreign)
    # Only change source identity. Do not derive a new expected conclusion from Kit output.
    wrong=story.execute('foreign-background',goal({'observations':observed,'predictions':foreign_file},[('t1','analysis')]),
        'revival-evidence.assess_predictions',evidence_settings)
    summary={'construct':str(construct.relative_to(root)),'identity':str(identity.relative_to(root)),
             'evidence':str(evidence.relative_to(root)),'foreign_background':str(wrong.relative_to(root)),
             'seed':2026101701,'reference_bp':800,'edit':[start,end],'arm_bp':arm,'marker_bp':96,'donor_bp':196,
             'gene_codon':gene_codon,
             'expected_band_bp':{'original':260,'edited':236},'connections':sum(r['network']['attempts'] for r in story.receipts),
             'commands':len(story.receipts),'laboratory':'PLANNED / NOT_PERFORMED','official_gitlab_ci':'not executed'}
    write(root/'SUMMARY.json',summary)
    process=subprocess.run([sys.executable,'-X','utf8','-B',str(ROOT/'tests/evidence/chain-story/check.py'),str(root)],
                           cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
    (root/'oracle.stdout.txt').write_text(process.stdout,encoding='utf-8');(root/'oracle.stderr.txt').write_text(process.stderr,encoding='utf-8')
    assert process.returncode==0,process.stdout+process.stderr
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--resume',action='store_true',help='Reuse and verify already sealed positive runs; retain earlier failed controls.')
    parser.add_argument('--gene-codon',choices=['GCT','AAA'],default='GCT',help='AAA is the retained shared-primer negative control; GCT is distinct from the AAA marker.')
    args=parser.parse_args();print(json.dumps(run(args.out,resume=args.resume,gene_codon=args.gene_codon),indent=2))

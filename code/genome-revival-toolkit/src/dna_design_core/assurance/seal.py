"""Only publisher of a sealed directory. All checks precede atomic publication."""
from pathlib import Path
import shutil
import tempfile
import time
from dna_design_core.kernel import canonical, ids, schemas
from dna_design_core.kernel.errors import ToolkitError
from . import labels


def preconditions(state,view):
    required={t['id'] for t in view.goal['targets'] if t['required']}
    bound={b['target'] for b in view.pipeline['outputs']} if view.pipeline else set()
    if state!='COMPLETED' or required-bound or any(s['failure'] and not s['superseded'] for s in view.steps()):
        raise ToolkitError('SEAL_RUN_NOT_COMPLETED')


def publish(temporary,destination):
    deadline=time.monotonic()+1
    for attempt in range(6):
        try:temporary.rename(destination);return
        except PermissionError:
            if attempt==5 or time.monotonic()>=deadline:
                raise ToolkitError('CAPABILITY_INTERNAL','Atomic sealing rename remained locked after bounded retries.',{'attempts':attempt+1}) from None
            time.sleep(0.05*(attempt+1))


def create(root,journal,candidate,result,required,snapshot,goal,plan,render):
    if result['unsatisfied']:
        journal.append('seal.rejected',{k:result[k] for k in ['candidate_digest','unsatisfied']},writer='assurance')
        return {'sealed':False,'candidate_digest':result['candidate_digest'],'unsatisfied':result['unsatisfied'],'present_files':[]}
    root=Path(root);events=journal.events();created=events[0]
    verdicts=[r['verdict'] for r in result['verdicts']]
    label_set=labels.collect(events,snapshot,sealed=True,verdicts=verdicts)
    unverified=labels.not_verified(events,snapshot,goal,verdicts)
    if created['payload']['release_id']=='dev-tree':unverified.append('This development-tree package is not release evidence.')
    temporary=Path(tempfile.mkdtemp(prefix='.sealing-',suffix='.tmp',dir=root))
    destination=None
    try:
        for row in candidate['files']:
            source=Path(candidate['root'])/row['path'];target=temporary/row['path'];target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(source,target)
            if ids.file_sha256(target.read_bytes())!=row['sha256']:raise ToolkitError('STORE_CORRUPT','Staged bytes changed while copying.')
        # These relative copies allow replay after moving only the sealed folder.
        for name in ['inputs','store','work']:
            if (root/name).exists():shutil.copytree(root/name,temporary/name)
        shutil.copyfile(root/'run.json',temporary/'run.json')
        def write(name,value):
            path=temporary/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(canonical.dumps(value))
        write('goal.json',goal);write('pipeline-final.json',plan);write('catalog-snapshots.json',snapshot);write('verdicts.json',result['verdicts'])
        for event in events:
            if event['type']=='pipeline.revised':write('revisions/'+str(event['payload']['version'])+'.json',event['payload'])
        (temporary/'journal-until-seal.ndjson').write_bytes(journal.path.read_bytes())
        view_text=render(events,label_set,unverified)
        (temporary/'views').mkdir()
        (temporary/'views/runcard.html').write_text(view_text['html'],encoding='utf-8',newline='\n')
        (temporary/'views/report.md').write_text(view_text['markdown'],encoding='utf-8',newline='\n')
        roles={row['path']:row['role'] for row in candidate['files']}
        files=[{'path':p.relative_to(temporary).as_posix(),'sha256':ids.file_sha256(p.read_bytes()),
                'role':roles.get(p.relative_to(temporary).as_posix(),'record'),'labels':list(label_set)}
               for p in sorted(temporary.rglob('*')) if p.is_file()]
        goal_event=next(e for e in reversed(events) if e['type'] in {'goal.declared','goal.amended'})
        plan_event=next(e for e in reversed(events) if e['type'] in {'pipeline.declared','pipeline.revised'})
        manifest={'schema':'manifest-v1','run_id':created['run_id'],'release_id':created['payload']['release_id'],
                  'goal_digest':goal_event['payload']['goal_digest'],'pipeline_digest':plan_event['payload']['pipeline_digest'],
                  'revisions':[e['payload']['pipeline_digest'] for e in events if e['type']=='pipeline.revised'],
                  'journal_head':events[-1]['hash'],'catalog_ids':[created['payload']['catalog_id']],
                  'environment_ids':[ids.document_id(created['payload']['environment'])],'files':files,
                  'verdicts':[{'check':r['verdict']['check']['id'],'scope':r['verdict']['scope'],'outcome':r['verdict']['outcome'],'verdict_event':r['event']} for r in result['verdicts']],
                  'profile':{'profiles_digest':snapshot['profiles_digest'],'obligation_ids':[r['id'] for r in required]},
                  'not_verified':sorted(set(unverified)),'labels':label_set,
                  'review_states':{r['pack']:r['review'] for r in snapshot['knowledge']},'kit_receipts':created['payload']['kits']}
        schemas.require('manifest-v1',manifest);write('manifest.json',manifest)
        seal_id=ids.document_id(manifest);destination=root/'sealed'/seal_id;destination.parent.mkdir(exist_ok=True)
        if destination.exists():
            if (destination/'manifest.json').read_bytes()!=(temporary/'manifest.json').read_bytes():raise ToolkitError('STORE_CORRUPT')
        else:publish(temporary,destination)
        journal.append('seal.created',{'seal_id':seal_id,'manifest_digest':seal_id,'journal_head':manifest['journal_head'],
                                      'release_id':manifest['release_id'],'labels':label_set},writer='assurance')
        return {'sealed':True,'seal_id':seal_id,'manifest':str(destination/'manifest.json'),
                'present_files':[str(destination/r['path']) for r in candidate['files']]+[str(destination/'views/runcard.html'),str(destination/'views/report.md')],
                'labels':label_set}
    finally:
        if temporary.exists():shutil.rmtree(temporary)

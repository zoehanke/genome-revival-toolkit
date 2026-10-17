"""Read-only sealed-package integrity and offline checks, with no original run."""
from pathlib import Path
from dna_design_core.kernel import canonical, ids, schemas
from dna_design_core.kernel.errors import ToolkitError
from dna_design_core.storage import chain
from . import obligations,stage,judge


def inspect(root):
    root=Path(root);manifest=canonical.loads((root/'manifest.json').read_bytes());schemas.require('manifest-v1',manifest)
    if ids.document_id(manifest)!=root.name:raise ToolkitError('STORE_CORRUPT','Manifest digest differs from sealed directory name.')
    actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p!=root/'manifest.json'}
    listed={r['path'] for r in manifest['files']}
    if actual!=listed or len(listed)!=len(manifest['files']):raise ToolkitError('STORE_CORRUPT','Sealed file inventory differs.')
    for row in manifest['files']:
        path=root/row['path']
        if not path.is_file() or ids.file_sha256(path.read_bytes())!=row['sha256']:raise ToolkitError('STORE_CORRUPT','Sealed file hash differs.',{'path':row['path']})
    events=chain.read(root/'journal-until-seal.ndjson')
    if not events or events[-1]['hash']!=manifest['journal_head']:raise ToolkitError('JOURNAL_CHAIN_BROKEN')
    recorded={e['hash']:e for e in events if e['type']=='verdict.issued'}
    for verdict in manifest['verdicts']:
        event=recorded.get(verdict['verdict_event'])
        if event is None or any(event['payload']['verdict'][key]!=verdict[key] for key in ['scope','outcome']) or event['payload']['verdict']['check']['id']!=verdict['check']:
            raise ToolkitError('STORE_CORRUPT','Manifest verdict has no matching recorded verdict.')
    return manifest,events


def run(root,invoker,view_factory,manifest,events,snapshot):
    root=Path(root);view=view_factory({});rows=stage.outputs(view,snapshot)
    candidate={'root':str(root),'files':manifest['files'],'outputs':[{k:v for k,v in r.items() if k!='value'} for r in rows],
               'catalog':snapshot,'journal_path':str(root/'journal-until-seal.ndjson'),'sealed':True}
    required=obligations.derive(snapshot,view.goal,view.pipeline,events)
    options=obligations.derive(snapshot,view.goal,view.pipeline,events,[r['check'] for r in manifest['verdicts']])
    wanted=set(manifest['profile']['obligation_ids']);normal={r['id'] for r in required}
    if not normal<=wanted or not wanted<={r['id'] for r in options}:raise ToolkitError('STORE_CORRUPT','Recorded obligations differ from catalog-derived requirements.')
    required=[r for r in options if r['id'] in wanted]
    result=judge.run(invoker,view_factory,None,candidate,required,record=False,offline=True)
    return {'verified':not result['unsatisfied'],'seal_id':root.name,'files_checked':len(manifest['files']),
            'verdicts':[r['verdict'] for r in result['verdicts']],'not_rerun':result['not_rerun'],'unsatisfied':result['unsatisfied']}


def record_result(journal,result):
    for verdict in result['verdicts']:
        journal.append('verdict.issued',{'verdict':verdict},writer='assurance')

"""Export only through format capabilities, preserving producer output roles."""
from pathlib import Path
from dna_design_core.kernel import ids
from dna_design_core.kernel.errors import ToolkitError
from dna_design_core.storage.store import Store


def outputs(view,snapshot):
    declarations={r['declaration']['id']:r['declaration'] for r in snapshot['capabilities']}
    steps={s['definition']['step_id']:s for s in view.steps()};rows=[]
    for binding in view.pipeline['outputs']:
        ref=binding['from'];step=steps.get(ref.get('step'))
        if not step or not step['completed'] or step['superseded']:raise ToolkitError('PLAN_OUTPUT_INVALID','Bound output is not available.')
        decl=declarations[step['definition']['use'].split('@')[0]]
        port=next(p for p in decl['outputs'] if p['name']==ref['port']);payload=step['completed']['payload'];index=ref.get('index',0)
        kind=port['type'];name=port['name']
        if kind=='document':identity=payload['outputs']['documents'][name][index];value=view.document(identity)
        elif kind in {'material','materials'}:identity=payload['outputs']['materials'][name][index];value=view.material(identity);kind='material'
        elif kind=='value':value=payload['values'][name];identity=ids.document_id(value)
        elif kind=='artifact':
            names=[p['name'] for p in decl['outputs'] if p['type']=='artifact']
            artifact=payload['outputs']['artifacts'][names.index(name)]
            value=view.root/artifact['run_path'];identity=artifact['sha256']
            if not value.is_file() or ids.file_sha256(value.read_bytes())!=identity:raise ToolkitError('STORE_CORRUPT','Recorded artifact bytes changed.')
        else:raise ToolkitError('PLAN_OUTPUT_INVALID','Unsupported delivery output type.')
        # PROVISIONAL(C1): preserve the file suffix on a bare binding name.
        destination=binding['name']+(value.suffix if kind=='artifact' and not Path(binding['name']).suffix else '') if kind=='artifact' else binding['name']+'.json'
        rows.append({'path':destination,'id':identity,'kind':kind,'target':binding['target'],'role':port['output_role'],
                     'step_id':ref['step'],'port':name,'value':value})
    return rows


def create(root,view,snapshot,invoker,view_factory):
    directory=Path(root)/'candidate';directory.mkdir(exist_ok=True)
    number=1+max((int(p.name) for p in directory.iterdir() if p.is_dir() and p.name.isdigit()),default=0)
    destination=directory/str(number);destination.mkdir()
    rows=outputs(view,snapshot)
    candidate={'root':str(destination),'files':[],'outputs':[],'catalog':snapshot,
               'journal_path':str(Path(root)/'journal.ndjson'),'sealed':False}
    for row in rows:
        use='format.write_json';inputs={'data':row['value']}
        if row['kind']=='artifact':
            store=Store(root);identity=store.put_file(row['value'].read_bytes())
            if identity!=row['id']:raise ToolkitError('STORE_CORRUPT','Artifact changed before staging.')
            store.get_file(identity);use='format.write_file';inputs={'file':store.path('artifacts',identity)}
        invoker.invoke(use,inputs,{'name':row['path']},parent=row['step_id'],
                       view=view_factory({**candidate,'stage_export':True}))
        candidate['files'].append({'path':row['path'],'sha256':ids.file_sha256((destination/row['path']).read_bytes()),'role':row['role'] or 'intermediate','labels':[]})
        candidate['outputs'].append({k:v for k,v in row.items() if k!='value'})
    return candidate

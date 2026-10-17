"""Read-only checks on recorded inputs, retained content and staged output bytes."""
from copy import deepcopy
from pathlib import Path
from dna_design_core.kernel.public import (Outcome, capability, make, core_version, document_id,
    material_id, file_sha256, event_hash, GENESIS, loads, require_schema, ToolkitError, resolve_reference)
from ..declaration import check
from ..recorded import catalog as frozen_catalog
from .check.goal import (
    claim_reported, components_absent, components_present, exact_sequence,
    regions_unchanged, topology,
)


MODULE='dna_design_core.capabilities.builtin.checks:'


def _verdict(ctx, identity, scope, outcome, summary, evidence=None):
    candidate=ctx.view.candidate
    return Outcome(verdicts=[make(check={'id':identity,'version':core_version()},scope=scope,
        moment=candidate.get('moment','final'),issuer=candidate.get('issuer','check_capability'),
        subject={'kind':'run','id':ctx.view.events()[0]['run_id']},constraint_id=candidate.get('constraint',{}).get('id'),
        outcome=outcome,summary=summary,evidence=evidence or {},basis=[e['hash'] for e in ctx.view.events()],
        does_not_establish=['Experimental performance or correctness of a scientific conclusion.'])])


def _files_match(root, rows):
    return all((root/r['path']).is_file() and file_sha256((root/r['path']).read_bytes())==r['sha256'] for r in rows)


@capability(check('check.readback','file',MODULE+'readback','Read exported JSON or compare unchanged artifact byte identities.'))
def readback(ctx) -> Outcome:
    problems=[]
    for output in ctx.view.candidate['outputs']:
        path=Path(ctx.view.candidate['root'])/output['path']
        try:
            data=path.read_bytes()
            identity=file_sha256(data) if output.get('kind')=='artifact' else document_id(loads(data))
            if identity!=output['id']:problems.append(output['path'])
        except (ToolkitError,OSError,ValueError):problems.append(output['path'])
    return _verdict(ctx,'check.readback','file','FAIL' if problems else 'PASS','Exported content comparison.',{'different_files':problems})


@capability(check('check.manifest','file',MODULE+'manifest','Compare the staged file list with actual bytes and files.'))
def manifest(ctx) -> Outcome:
    candidate=ctx.view.candidate;root=Path(candidate['root']);rows=candidate['files']
    listed={r['path'] for r in rows};actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    if candidate.get('sealed'):actual.discard('manifest.json')
    passed=len(listed)==len(rows) and listed==actual and _files_match(root,rows)
    return _verdict(ctx,'check.manifest','file','PASS' if passed else 'FAIL','File list and byte hashes checked.',{'listed':len(rows),'actual':len(actual)})


@capability(check('check.journal_chain','file',MODULE+'journal_chain','Validate each recorded event and its hash-chain predecessor.'))
def journal_chain(ctx) -> Outcome:
    previous=GENESIS;count=0;passed=True
    try:
        for count,line in enumerate(Path(ctx.view.candidate['journal_path']).read_bytes().splitlines(),1):
            event=loads(line);require_schema('event-v1',event)
            if event['seq']!=count or event['prev']!=previous or event_hash(event)!=event['hash']:passed=False;break
            previous=event['hash']
    except (ToolkitError,OSError,ValueError,KeyError):passed=False
    passed=passed and count>0
    return _verdict(ctx,'check.journal_chain','file','PASS' if passed else 'FAIL','Recorded event chain checked.',{'events':count,'head':previous})


@capability(check('check.store_hashes','file',MODULE+'store_hashes','Recompute stored document, material and raw artifact identities.'))
def store_hashes(ctx) -> Outcome:
    different=[]
    for kind,identify in [('documents',document_id),('materials',material_id)]:
        for path in (ctx.view.root/'store'/kind).glob('*.json'):
            try:
                if identify(loads(path.read_bytes()))!=path.stem:different.append(path.stem)
            except (ToolkitError,OSError,ValueError):different.append(path.stem)
    for path in (ctx.view.root/'store/artifacts').glob('*'):
        if path.is_file() and file_sha256(path.read_bytes())!=path.name:different.append(path.name)
    return _verdict(ctx,'check.store_hashes','file','FAIL' if different else 'PASS','Stored content identities checked.',{'different_ids':different})


@capability(check('check.inputs_unchanged','file',MODULE+'inputs_unchanged','Compare input copies with the registered file hashes.'))
def inputs_unchanged(ctx) -> Outcome:
    sources={e['payload']['source_id']:e['payload'] for e in ctx.view.events('input.registered')};different=[]
    for identity,row in sources.items():
        path=ctx.view.root/row['run_path']
        if not path.is_file() or file_sha256(path.read_bytes())!=row['file_sha256']:different.append(identity)
    for source in ctx.view.goal['sources']:
        row=sources.get(source['source_id']);path=ctx.view.root/source['path']
        if row is None or row['run_path']!=source['path'] or row['file_sha256']!=source['sha256']:different.append(source['source_id'])
    return _verdict(ctx,'check.inputs_unchanged','file','FAIL' if different else 'PASS','Registered input copies checked.',{'different_sources':different})


@capability(check('check.goal.nonempty','user_goal',MODULE+'goal_nonempty','Require at least one active, computable goal constraint.'))
def goal_nonempty(ctx) -> Outcome:
    count=sum(c['status']=='active' for c in ctx.view.goal['constraints'])
    return _verdict(ctx,'check.goal.nonempty','user_goal','PASS' if count else 'UNKNOWN','Active goal constraints counted.',{'active':count})


@capability(check('check.goal.target_role_met','user_goal',MODULE+'target_role_met','Compare required targets with producer-declared output roles.'))
def target_role_met(ctx) -> Outcome:
    outputs=ctx.view.candidate['outputs'];missing=[]
    for target in ctx.view.goal['targets']:
        matches=[o for o in outputs if o['target']==target['id']]
        if target['required'] and not matches or any(o['role']!=target['role'] for o in matches):missing.append(target['id'])
    return _verdict(ctx,'check.goal.target_role_met','user_goal','FAIL' if missing else 'PASS','Producer roles compared with target roles.',{'unmet_targets':missing})


@capability(check('check.goal.output_present','user_goal',MODULE+'output_present','Check that the constrained target has a retained output.',constraint=True,
    params={'type':'object','properties':{'fields':{'type':'array','items':{'type':'string'}}},'additionalProperties':False}))
def output_present(ctx,fields: list[str] | None=None) -> Outcome:
    target=ctx.view.candidate.get('constraint',{}).get('target')
    rows=[o for o in ctx.view.candidate['outputs'] if target is None or o['target']==target]
    passed=bool(rows) and all((Path(ctx.view.candidate['root'])/o['path']).is_file() for o in rows)
    missing=[]
    if fields:
        for row in rows:
            document=ctx.view.document(row['id']) if row['kind']=='document' else None
            absent=[name for name in fields if not isinstance(document,dict) or name not in document]
            if absent:missing.append({'path':row['path'],'fields':absent})
    evidence={'outputs':len(rows)}
    if fields:evidence.update(required_fields=fields,missing_fields=missing)
    return _verdict(ctx,'check.goal.output_present','user_goal','PASS' if passed and not missing else 'FAIL','Bound output presence checked.',evidence)


def _declarations(view):return {r['declaration']['id']:r['declaration'] for r in frozen_catalog(view)['capabilities']}


def _resolve(view, ref):
    if 'literal' in ref:return deepcopy(ref['literal'])
    if 'source' in ref:
        row=next(s for s in view.goal['sources'] if s['source_id']==ref['source']);path=view.root/row['path']
        return loads(path.read_bytes()) if row.get('as')=='material' else path
    if 'artifact' in ref:return view.root/ref['artifact']
    step=next(s for s in view.steps() if s['definition']['step_id']==ref['step']);payload=step['completed']['payload'];outputs=payload['outputs'];port=ref['port'];index=ref.get('index',0)
    if port in outputs['documents']:return view.document(outputs['documents'][port][index])
    if port in outputs['materials']:return resolve_reference(view,ref,frozen_catalog(view))
    if port in payload['values']:return deepcopy(payload['values'][port])
    declaration=_declarations(view)[step['definition']['use'].split('@')[0]]
    names=[p['name'] for p in declaration['outputs'] if p['type']=='artifact']
    return view.root/outputs['artifacts'][names.index(port)]['run_path']


def _arguments(view, step):
    definition=step['definition'];declaration=_declarations(view)[definition['use'].split('@')[0]]
    inputs={name:_resolve(view,ref) for name,ref in definition['inputs'].items()}
    identities={p['name']:file_sha256(Path(inputs[p['name']]).read_bytes()) if p['type']=='artifact' else material_id(inputs[p['name']]) if p['type']=='material' else document_id(inputs[p['name']]) for p in declaration['inputs'] if p['name'] in inputs}
    original={key:row['id'] for key,row in step['started']['payload']['inputs'].items()}
    params={key:_resolve(view,value) if isinstance(value,dict) and set(value)&{'source','step','artifact','literal'} else deepcopy(value) for key,value in definition['params'].items()}
    return inputs,params,identities,original


@capability(check('check.lineage','content_model',MODULE+'lineage','Match explicit input bindings to the recorded content identities.'))
def lineage(ctx) -> Outcome:
    different=[]
    for step in ctx.view.steps():
        if step['completed'] is None:continue
        _,_,identities,original=_arguments(ctx.view,step)
        if identities!=original:different.append(step['definition']['step_id'])
    return _verdict(ctx,'check.lineage','content_model','FAIL' if different else 'PASS','Input bindings and identities compared.',{'different_steps':different})


@capability(check('check.replay','content_model',MODULE+'replay','Recompute deterministic steps from their recorded inputs and versions.',composite=True))
def replay(ctx) -> Outcome:
    differences=[];not_replayed=[]
    for step in ctx.view.steps():
        if step['completed'] is None:continue
        definition=step['definition'];decl=_declarations(ctx.view)[definition['use'].split('@')[0]]
        if not decl['deterministic']:not_replayed.append(definition['step_id']);continue
        inputs,params,identities,original=_arguments(ctx.view,step)
        recorded=step['completed']['payload'];outputs=recorded['outputs']
        result=ctx.call(definition['use'],inputs=inputs,params=params)
        actual={'materials':{k:[material_id(v) for v in (vs if isinstance(vs,list) else [vs])] for k,vs in result.products.items()},
                'documents':{k:[document_id(v)] for k,v in result.documents.items()},
                'artifacts':[file_sha256(Path(result.artifacts[p['name']]).read_bytes()) for p in decl['outputs'] if p['type']=='artifact'],
                'values':result.values,'unverified':result.unverified}
        expected={**outputs,'artifacts':[a['sha256'] for a in outputs['artifacts']],'values':recorded['values'],'unverified':recorded['unverified']}
        fields=[key for key in expected if expected[key]!=actual[key]]
        if identities!=original:fields.append('input_ids')
        if fields:differences.append({'step_id':definition['step_id'],'input_ids':identities,'recorded_input_ids':original,'recorded_result':document_id(expected),'replayed_result':document_id(actual),'fields':fields})
    return _verdict(ctx,'check.replay','content_model','FAIL' if differences else 'PASS','Deterministic output identities compared.',{'differences':differences,'not_replayed':not_replayed})


@capability(check('check.dna_value_valid','content_model',MODULE+'dna_value_valid','Check DNA-valued document outputs against the IUPAC DNA alphabet.'))
def dna_value_valid(ctx) -> Outcome:
    values=[ctx.view.document(o['id']) for o in ctx.view.candidate['outputs'] if o['kind']=='document']
    sequences=[v['sequence'] for v in values if isinstance(v,dict) and 'sequence' in v]
    passed=bool(sequences) and all(isinstance(s,str) and bool(s) and set(s.upper())<=set('ACGTRYSWKMBDHVN') for s in sequences)
    return _verdict(ctx,'check.dna_value_valid','content_model','PASS' if passed else 'FAIL','DNA-valued document alphabet checked.',{'sequence_count':len(sequences)})

"""Pure reference resolution over the supplied read view and frozen catalog."""
from copy import deepcopy
from . import canonical, ids
from .errors import ToolkitError


def pointer(value,path):
    for token in path.split('/')[1:]:
        token=token.replace('~1','/').replace('~0','~')
        value=value[int(token)] if isinstance(value,list) else value[token]
    return value


def resolve(view,reference,catalog):
    if 'literal' in reference:return deepcopy(reference['literal'])
    if 'source' in reference:
        source=next((s for s in view.goal['sources'] if s['source_id']==reference['source']),None)
        if source is None:raise ToolkitError('PLAN_REF_UNRESOLVED')
        path=(view.root/source['path']).resolve()
        if not path.is_relative_to(view.root) or ids.file_sha256(path.read_bytes())!=source['sha256']:raise ToolkitError('SOURCE_CHANGED')
        if source.get('as')=='material':return canonical.loads(path.read_bytes())
        return path
    if 'artifact' in reference:
        registered={s['path'] for s in view.goal['sources']}
        registered.update(a['run_path'] for step in view.steps() if step['completed'] and not step['superseded'] for a in step['completed']['payload']['outputs']['artifacts'])
        if reference['artifact'] not in registered:raise ToolkitError('PLAN_REF_UNRESOLVED','Artifact must have been registered.')
        return view.root/reference['artifact']
    step=next((s for s in view.steps() if s['definition']['step_id']==reference.get('step')),None)
    if step is None or step['completed'] is None or step['superseded']:raise ToolkitError('PLAN_REF_UNRESOLVED','Output is unavailable or superseded.')
    payload=step['completed']['payload'];port=reference['port'];outputs=payload['outputs'];index=reference.get('index',0)
    if port in outputs['materials']:
        declaration=next(r['declaration'] for r in catalog['capabilities'] if r['declaration']['id']==step['definition']['use'].split('@')[0])
        kind=next(p['type'] for p in declaration['outputs'] if p['name']==port)
        result=[view.material(identity) for identity in outputs['materials'][port]] if kind=='materials' and 'index' not in reference else view.material(outputs['materials'][port][index])
    elif port in outputs['documents']:result=view.document(outputs['documents'][port][index])
    elif port in payload['values']:result=deepcopy(payload['values'][port])
    else:
        declaration=next(r['declaration'] for r in catalog['capabilities'] if r['declaration']['id']==step['definition']['use'].split('@')[0])
        ports=[p['name'] for p in declaration['outputs'] if p['type']=='artifact']
        if port not in ports:raise ToolkitError('PLAN_REF_UNRESOLVED')
        result=view.root/outputs['artifacts'][ports.index(port)]['run_path']
    return pointer(result,reference['pointer']) if 'pointer' in reference else result

"""Material outputs and explicit root-input ancestry for per-finding comparisons."""
from dna_design_core.kernel.public import ToolkitError,loads,file_sha256,material_id,normalize_material
from dna_design_core.biology.public import rotate_material

READERS={'format.read_genbank','format.read_fasta','format.read_dna'}


def material_rows(view):
    for step in view.steps():
        if not step['completed'] or step['superseded']:continue
        for port,identities in step['completed']['payload']['outputs']['materials'].items():
            for index,identity in enumerate(identities):
                yield {'step_id':step['definition']['step_id'],'port':port,'index':index,'material_id':identity,'material':view.material(identity)}


def root_materials(view,step_id):
    steps={s['definition']['step_id']:s for s in view.steps()}
    sources={s['source_id']:s for s in view.goal['sources']}
    calls=view.events('call.recorded');found={};complete=True
    def visit(identity,seen):
        nonlocal complete
        if identity in seen:complete=False;return
        step=steps[identity]
        for reference in step['definition']['inputs'].values():
            if 'step' in reference:visit(reference['step'],seen|{identity});continue
            source=sources.get(reference.get('source'))
            if 'artifact' in reference:
                source=next((s for s in sources.values() if s['path']==reference['artifact']),None)
                if source is None:
                    producer=next((s for s in steps.values() if s['completed'] and any(a['run_path']==reference['artifact'] for a in s['completed']['payload']['outputs']['artifacts'])),None)
                    if producer:visit(producer['definition']['step_id'],seen|{identity});continue
            if source is None:continue
            path=(view.root/source['path']).resolve()
            if not path.is_relative_to(view.root) or file_sha256(path.read_bytes())!=source['sha256']:raise ToolkitError('SOURCE_CHANGED')
            values=[]
            if source.get('as')=='material':values=[normalize_material(loads(path.read_bytes()))]
            else:
                if step['definition']['use'].split('@')[0] in READERS and step['completed']:
                    values.extend(view.material(i) for ids in step['completed']['payload']['outputs']['materials'].values() for i in ids)
                for event in calls:
                    payload=event['payload']
                    if payload['parent']==identity and payload['capability']['id'] in READERS and source['sha256'] in payload['input_ids'].values() and 'outputs' in payload:
                        values.extend(view.material(i) for ids in payload['outputs']['materials'].values() for i in ids)
            if not values:complete=False
            for value in values:
                key=(source['source_id'],material_id(value));found[key]={'source_id':key[0],'material_id':key[1],'material':value}
    visit(step_id,set())
    return list(found.values()),complete


def _covered(value,feature):
    parts=feature.get('parts') or [feature];size=len(value['sequence'])
    if not isinstance(parts,list) or any(not isinstance(p,dict) or any(type(p.get(k)) is not int for k in ['start','end']) or not 0<=p['start']<=p['end']<=size for p in parts):return None
    return [value['sequence'][p['start']:p['end']] for p in parts]


def finding_origin(output,finding,sources,complete,analyze):
    """PROVISIONAL(C4): exact per-feature copy or unique whole-circle rotation."""
    feature=output['features'][finding['feature_index']];matches=[];uncertain=False
    for source in sources:
        value=source['material'];diagnostics=analyze(value)
        bad_indices={r['feature_index'] for r in diagnostics if r['code']==finding['code']}
        for index in bad_indices:
            original=value['features'][index]
            before,after=_covered(value,original),_covered(output,feature)
            if original==feature and ((before is not None and before==after) or value['sequence']==output['sequence']):
                matches.append({'source_id':source['source_id'],'source_material_id':source['material_id'],'source_feature_index':index,'mode':'EXACT_COPY'});continue
            # Matching affected bases under an unsupported coordinate/edit
            # mapping do not prove that the pipeline introduced the finding.
            if before is not None and before==after:uncertain=True
            if value.get('topology')=='circular' and output.get('topology')=='circular' and len(value['sequence'])==len(output['sequence']):
                doubled=value['sequence']+value['sequence'];origin=doubled.find(output['sequence'])
                if not 0<=origin<len(value['sequence']):continue
                if 0<=doubled.find(output['sequence'],origin+1)<len(value['sequence']):uncertain=True;continue
                try:rotated=rotate_material({**value,'features':[original]},origin)
                except (ValueError,TypeError,KeyError):uncertain=True;continue
                if rotated['features']==[feature]:
                    matches.append({'source_id':source['source_id'],'source_material_id':source['material_id'],'source_feature_index':index,'mode':'CIRCULAR_ROTATION','origin':origin})
    if len(matches)==1:return 'INHERITED',matches[0]
    if matches or not complete or uncertain:return 'UNDETERMINED',{'matching_witnesses':len(matches)}
    return 'INTRODUCED',{'matching_witnesses':0}

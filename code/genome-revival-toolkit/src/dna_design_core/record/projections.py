"""Read-only event projections. Links require an explicit origin, never proximity."""
from dna_design_core.kernel import ids
from dna_design_core.kernel.redact import safe


FOOTER='This record shows what ran and what was checked. It does not prove that a conclusion is true.'


def project(events,snapshot,label_set,not_verified):
    nodes={};links=[];produced={};artifact_paths={};steps={};checked=[];declared=[];not_done=list(not_verified)
    declarations={r['declaration']['id']:r['declaration'] for r in snapshot['capabilities']}
    plan=None;goal=None;revisions=0
    for event in events:
        payload=event['payload'];kind=event['type']
        if kind=='input.registered':
            key='source:'+payload['source_id'];nodes[key]={'id':key,'lane':0,'label':payload['source_id']+' ('+payload['input_origin']+')','hash':payload['file_sha256']}
        elif kind=='goal.declared':goal=payload['document']
        elif kind=='goal.amended':
            revisions+=1
            for op in payload['diff']:
                if op['op']=='replace':goal={**goal,op['path'][1:]:op['value']}
        elif kind in {'pipeline.declared','pipeline.revised'}:
            plan=payload['document']
            if kind=='pipeline.revised':revisions+=1
        elif kind=='step.started':
            step=payload['step_id'];steps[step]=payload
            nodes['step:'+step]={'id':'step:'+step,'lane':1,'label':step+' · '+payload['capability']['id'],'hash':event['hash']}
        elif kind=='step.completed':
            step=payload['step_id'];outputs=payload['outputs'];decl=declarations[steps[step]['capability']['id']]
            rows=[]
            for port,identities in {**outputs['documents'],**outputs['materials']}.items():
                for index,identity in enumerate(identities):rows.append((port,index,identity,None,True))
            for port,value in payload['values'].items():rows.append((port,0,ids.document_id(value),None,False))
            ports=[p['name'] for p in decl['outputs'] if p['type']=='artifact']
            rows.extend((ports[i],0,r['sha256'],r['run_path'],True) for i,r in enumerate(outputs['artifacts']))
            for port,index,identity,path,eligible in rows:
                key='output:'+step+'.'+port+'.'+str(index)
                nodes[key]={'id':key,'lane':2,'label':step+'.'+port+'['+str(index)+']','hash':identity}
                produced[(step,port,index)]={'node':key,'hash':identity,'eligible':eligible}
                if path:artifact_paths.setdefault(path,[]).append(produced[(step,port,index)])
                links.append({'source':'step:'+step,'target':key,'basis':None})
            not_done.extend(payload['unverified'])
        elif kind=='step.failed':
            not_done.append(payload['step_id']+' failed: '+payload['failure']['code']+' (retained in history).')
        elif kind=='declaration.recorded':declared.append(payload['origin']+': '+payload['text'])
    nodes['host']={'id':'host','lane':0,'label':'Host-reported goal and reasons','hash':''}
    if goal:
        declared.insert(0,'Host-reported original request: '+goal['original_request'])
        declared.extend(c['id']+' ['+c['origin']+']: '+c['source_quote'] for c in goal['constraints'])
        declared.extend(c['text'] for c in goal['declared_context'])
    for event in events:
        payload=event['payload']
        if event['type']=='step.started':
            for row in payload['inputs'].values():
                origin=row['origin'];source=None
                if origin['kind']=='step':
                    ref=origin['ref'];source=produced.get((ref['step_id'],ref['port'],ref.get('index',0)))
                elif origin['kind']=='artifact':
                    matches=artifact_paths.get(origin['ref'],[])
                    if len(matches)==1:source=matches[0]
                if source:
                    links.append({'source':source['node'],'target':'step:'+payload['step_id'],
                                  'basis':'hash_equal' if source['eligible'] and source['hash']==row['id'] else None})
                elif origin['kind']=='source' and 'source:'+origin['ref'] in nodes:
                    links.append({'source':'source:'+origin['ref'],'target':'step:'+payload['step_id'],'basis':None})
        elif event['type']=='declaration.recorded' and payload['about']['kind']=='step' and 'step:'+payload['about']['id'] in nodes:
            links.append({'source':'host','target':'step:'+payload['about']['id'],'basis':'declared'})
    judges=[e for e in events if e['type']=='judge.finished'];latest=set(judges[-1]['payload']['verdict_ids']) if judges else set()
    for event in events:
        if event['type']!='verdict.issued':continue
        verdict=event['payload']['verdict'];text=verdict['check']['id']+' ['+verdict['scope']+']: '+verdict['outcome']+' · '+verdict['summary']
        if verdict['issuer']!='check_capability' or verdict['moment']!='final':declared.append(verdict['issuer']+': '+text)
        elif not latest or event['hash'] in latest:
            if verdict['outcome'] in {'PASS','FAIL'}:checked.append(text)
            else:not_done.append(text)
    if plan:checked.insert(0,'Pipeline admitted after static validation.')
    not_done.extend(label_set.values());not_done.append('Revisions recorded: '+str(revisions))
    return safe({'nodes':list(nodes.values()),'links':links,'checked':checked,'declared':declared,'not_done':sorted(set(not_done)),
                 'cutoff':events[-1]['seq'] if events else 0,'head':events[-1]['hash'] if events else '',
                 'timeline':[{'seq':e['seq'],'type':e['type'],'actor':e['actor']['kind'],'hash':e['hash'],
                              **({'verdict':e['payload']['verdict']} if e['type']=='verdict.issued' else {})} for e in events],
                 'footer':FOOTER})

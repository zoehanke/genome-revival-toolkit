"""Single source of labels and unverified statements for receipts and cards."""


def collect(events,snapshot,*,sealed=False,verdicts=()):
    labels={}
    if not sealed:labels['UNSEALED']='Unsealed'
    if any(e['type']=='goal.amended' and e['payload']['amended_after_start'] for e in events):labels['AMENDED_AFTER_START']='Goal amended after execution started'
    if any(k['origin']=='external' for k in snapshot['kits']):labels['EXTERNAL_KIT']='External Kit code was loaded'
    if any(f.get('origin')=='INHERITED' for v in verdicts for f in v['evidence'].get('findings',[])):
        labels['INHERITED_FINDINGS']='Inherited input findings remain'
    counts={key:sum(row['review'].get(key,0) for row in snapshot['knowledge']) for key in ['reviewed','stale','none']}
    labels['review']=f"reviewed {counts['reviewed']} / stale {counts['stale']} / none {counts['none']}"
    return labels


def not_verified(events,snapshot,goal,verdicts):
    names={e['payload']['capability']['id'] for e in events if e['type'] in {'step.started','call.recorded'}}
    names.update(v['check']['id'] for v in verdicts)
    statements={text for row in snapshot['capabilities'] if row['declaration']['id'] in names for text in row['declaration']['does_not_establish']}
    statements.update(i['text'] for i in goal['intents'] if not i['binds'])
    statements.update('Dropped constraint '+c['id']+': '+c['drop_reason'] for c in goal['constraints'] if c['status']=='dropped')
    statements.update(text for e in events if e['type']=='step.completed' for text in e['payload']['unverified'])
    statements.update(text for v in verdicts for text in v['does_not_establish'])
    statements.update(v['applicability']['reason'] for v in verdicts if v['outcome']=='NOT_APPLICABLE')
    return sorted(statements)

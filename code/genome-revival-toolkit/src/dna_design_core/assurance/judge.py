"""Run every obligation through the injected Invoker; never trust old verdicts."""
from dna_design_core.kernel import ids
from dna_design_core.kernel.public import make, core_version
from dna_design_core.kernel.errors import ToolkitError, problem


def run(invoker, view_factory, journal, candidate, required, *, record=True, offline=False):
    verdicts=[];unsatisfied=[];not_rerun=[]
    declarations={r['declaration']['id']:r['declaration'] for r in candidate['catalog']['capabilities']}
    for obligation in required:
        name=obligation['check'];declaration=declarations.get(name);version=obligation['version'] or core_version()
        if offline and declaration is not None and not declaration.get('offline',False):
            not_rerun.append(name);continue
        view=view_factory({**candidate,'constraint':obligation['constraint'] or {},'moment':'final','issuer':'check_capability'})
        try:
            if declaration is None or declaration['role']!='CHECK':raise ToolkitError('CHECK_UNAVAILABLE',details={'check':name})
            result=invoker.invoke(name+'@'+version,{},obligation['params'],parent='final',view=view)
            if not result.verdicts:raise ToolkitError('CHECK_UNAVAILABLE','Check returned no verdict.')
            values=result.verdicts
            if any(v['issuer']!='check_capability' or v['moment']!='final' or v['check']!={'id':name,'version':version} or v['scope']!=obligation['scope'] for v in values):
                raise ToolkitError('CAPABILITY_OUTPUT_INVALID','Check returned a verdict outside its declared scope or identity.')
            values=[make(**{**{k:v for k,v in item.items() if k!='schema'},'constraint_id':(obligation['constraint'] or {}).get('id')}) for item in values]
        except ToolkitError as error:
            failure=problem('CHECK_UNAVAILABLE',details={'check':name,'failure':error.problem.as_dict()}).as_dict()
            values=[make(check={'id':name,'version':version},scope=obligation['scope'],moment='final',
                         issuer='check_capability',subject={'kind':'run','id':view.events()[0]['run_id']},
                         constraint_id=(obligation['constraint'] or {}).get('id'),outcome='UNKNOWN',
                         summary='Required check could not be completed.',evidence={'failure':failure},
                         does_not_establish=['The required obligation.'])]
        for verdict in values:
            event=journal.append('verdict.issued',{'verdict':verdict},writer='assurance') if record else None
            verdict_id=event['hash'] if event else None
            verdicts.append({'verdict':verdict,'event':verdict_id,'obligation_id':obligation['id']})
            if verdict['outcome'] not in {'PASS','NOT_APPLICABLE'}:
                unsatisfied.append({'check':name,'outcome':verdict['outcome'],'verdict_id':verdict_id,
                                    'recovery':'Inspect the verdict evidence; correct the input or add and supersede a step, then judge again.'})
    result={'candidate_digest':ids.document_id(candidate['files']),'obligation_ids':[r['id'] for r in required],
            'verdict_ids':[v['event'] for v in verdicts if v['event']],'unsatisfied':unsatisfied}
    if record:journal.append('judge.finished',result,writer='assurance')
    return {**result,'verdicts':verdicts,'not_rerun':not_rerun}

"""Execution owns step facts and performs no final scientific qualification."""
from copy import deepcopy
from pathlib import Path
import time
from dna_design_core.kernel import canonical, ids
from dna_design_core.kernel.public import make
from dna_design_core.kernel.errors import ToolkitError
from dna_design_core.storage.lock import RunLock
from .invoker import input_ids
from .view import ReadView, resolve, pointer
from . import goal


def persist(session,result,declaration):
    outputs={'materials':{},'documents':{},'artifacts':[]}
    for port in declaration['outputs']:
        name=port['name'];kind=port['type']
        if kind in {'material','materials'}:
            data=result.products[name];items=data if kind=='materials' else [data]
            outputs['materials'][name]=[session.store.put('materials',item) for item in items]
        elif kind=='document':outputs['documents'][name]=[session.store.put('documents',result.documents[name])]
        elif kind=='artifact':
            path=Path(result.artifacts[name]).resolve()
            outputs['artifacts'].append({'run_path':path.relative_to(session.root).as_posix(),'sha256':ids.file_sha256(path.read_bytes()),'role':port['output_role'] or 'artifact','media_type':'application/json' if path.suffix=='.json' else 'text/plain'})
    return {'outputs':outputs,'values':deepcopy(result.values),'unverified':list(result.unverified)}


def arguments(view,definition):
    inputs={name:resolve(view,ref) for name,ref in definition['inputs'].items()}
    params={key:resolve(view,value) if isinstance(value,dict) and set(value)&{'source','step','artifact','literal'} else deepcopy(value) for key,value in definition['params'].items()}
    return inputs,params


def expected(actual,op,wanted):
    if op=='equals':return actual==wanted
    if op=='gte':return actual>=wanted
    if op=='lte':return actual<=wanted
    if op=='between':return wanted[0]<=actual<=wanted[1]
    if op=='contains':return wanted in actual
    if op=='length_equals':return len(actual)==wanted
    return False


def execute(session,invoker,until=None):
    with RunLock(session.root):
        session.journal.recover();session.editable()
        plan=session.current_pipeline()
        if plan is None:raise ToolkitError('PLAN_SCHEMA_INVALID','Submit a pipeline before execution.')
        if plan['goal_digest']!=goal.digest(session.current_goal()):raise ToolkitError('PLAN_GOAL_BINDING_INVALID','Revise pipeline to bind the current goal.')
        for name,row in session.steps().items():
            if row['state']=='RUNNING':
                failure=ToolkitError('STEP_INTERRUPTED').problem.as_dict()
                session.journal.append('step.failed',{'step_id':name,'failure':failure,'retained_outputs':{'outputs':{'materials':{},'documents':{},'artifacts':[]},'values':{},'unverified':['Interrupted before result registration.']},'superseded_by':None},writer='engine')
                session.journal.append('run.halted',{'reason':'step_failed','step_id':name},writer='engine')
        if session.state()=='HALTED':
            failed=next(r for r in session.steps().values() if r['failure'] and not r['superseded_by'])
            return {'state':'HALTED','failure':failed['failure']['payload']['failure']}
        if session.state()=='COMPLETED':return {'state':'COMPLETED'}
        for definition in plan['steps']:
            row=session.steps()[definition['step_id']]
            if row['superseded_by'] or row['state']=='COMPLETED':continue
            name=definition['use'].split('@')[0];entry=session.declarations()[name];declaration=entry['declaration']
            view=ReadView(session.root,session.events(),session.snapshot())
            inputs,params=arguments(view,definition);identities=input_ids(declaration,inputs)
            origins={}
            for key,ref in definition['inputs'].items():
                if 'literal' in ref:origin={'kind':'literal','ref':None}
                elif 'source' in ref:origin={'kind':'source','ref':ref['source']}
                elif 'artifact' in ref:origin={'kind':'artifact','ref':ref['artifact']}
                else:origin={'kind':'step','ref':{'step_id':ref['step'],'port':ref['port'],**({'index':ref['index']} if 'index' in ref else {})}}
                origins[key]={'id':identities[key],'origin':origin}
            session.journal.append('step.started',{'step_id':definition['step_id'],'capability':{'id':name,'version':declaration['version'],'declaration_digest':entry['declaration_digest'],'code_digest':entry['code_digest']},'inputs':origins,'params':params,'params_digest':ids.document_id(params)},writer='engine')
            started=time.perf_counter();retained={'outputs':{'materials':{},'documents':{},'artifacts':[]},'values':{},'unverified':[]};verdict_ids=[]
            try:
                result=invoker.invoke(definition['use'],inputs,params,parent=definition['step_id'])
                retained=persist(session,result,declaration)
                for draft in result.verdicts:
                    draft=make(**{**{k:v for k,v in draft.items() if k!='schema'},'moment':'step','issuer':'tool_self_report'})
                    verdict_ids.append(session.journal.append('verdict.issued',{'verdict':draft},writer='engine')['hash'])
                step_view=ReadView(session.root,session.events(),session.snapshot(),{'step_outputs':retained,'step_id':definition['step_id'],'moment':'step','issuer':'tool_self_report'})
                for check_id in declaration['step_checks']:
                    checked=invoker.invoke(check_id,{}, {},parent=definition['step_id'],view=step_view)
                    for draft in checked.verdicts:verdict_ids.append(session.journal.append('verdict.issued',{'verdict':draft},writer='engine')['hash'])
                if 'expects' in definition:
                    assertion=definition['expects'];ref=assertion['on']
                    if ref.get('step')==definition['step_id']:
                        key=ref['port']
                        actual=result.documents.get(key,result.values.get(key,result.products.get(key)))
                        if 'index' in ref and isinstance(actual,list):actual=actual[ref['index']]
                        if 'pointer' in ref:actual=pointer(actual,ref['pointer'])
                    else:actual=resolve(view,ref)
                    try:passed=expected(actual,assertion['op'],assertion['value'])
                    except (TypeError,KeyError,IndexError):passed=False
                    draft=make(check={'id':'check.goal.output_present','version':declaration['version']},scope='user_goal',moment='step',subject={'kind':'step','id':definition['step_id']},outcome='PASS' if passed else 'FAIL',issuer='host_expectation',summary='Host expectation satisfied.' if passed else 'Host expectation failed.',evidence={'operator':assertion['op']},does_not_establish=['Final qualification.'])
                    verdict_ids.append(session.journal.append('verdict.issued',{'verdict':draft},writer='engine')['hash'])
                    if not passed:raise ToolkitError('STEP_EXPECTATION_FAILED')
                session.journal.append('step.completed',{'step_id':definition['step_id'],**retained,'verdict_ids':verdict_ids,'duration_ms':int((time.perf_counter()-started)*1000)},writer='engine')
            except ToolkitError as error:
                session.journal.append('step.failed',{'step_id':definition['step_id'],'failure':error.problem.as_dict(),'retained_outputs':retained,'superseded_by':None},writer='engine')
                session.journal.append('run.halted',{'reason':'step_failed','step_id':definition['step_id']},writer='engine')
                return {'state':'HALTED','failure':error.problem.as_dict()}
            if until==definition['step_id']:break
        rows=session.steps()
        if all(r['state']=='COMPLETED' or r['superseded_by'] for r in rows.values()):
            session.journal.append('run.completed',{'pipeline_digest':ids.document_id(plan),'executed_steps':[k for k,r in rows.items() if r['state']=='COMPLETED']},writer='engine')
        return {'state':session.state()}

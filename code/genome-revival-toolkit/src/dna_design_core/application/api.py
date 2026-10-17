"""Public API and receipt envelope shared with the grt command."""
import json
from pathlib import Path
from dna_design_core.kernel import schemas
from dna_design_core.kernel.errors import ToolkitError
from dna_design_core.storage.lock import RunLock
from dna_design_core.storage import chain
from dna_design_core.engine.session import HOST
from dna_design_core.engine.executor import execute
from .run_service import RunService
from .describe import doctor as _doctor,describe as _describe


def _problem(value):
    return {k:value[k] for k in ['code','category','message','recovery']}|{'location':value.get('details',{}).get('location','')}


def call(verb,*,root=None,request=None,kit_dirs=(),config_path=None,**options):
    service=None;before=0;result={};problems=[]
    try:
        service=RunService(root,kit_dirs=kit_dirs,config_path=config_path,overrides={'lang':options.get('lang')})
        if service.session:
            before=len(chain.inspect(service.session.journal.path.read_bytes())[0]) if verb=='run execute' else len(service.session.events())
        if verb in {'goal declare','goal amend','pipeline submit','pipeline revise','declare','template instantiate','review sign'} and not isinstance(request,dict):
            recovery='Correct the request against goal-v1 and submit the goal again.' if verb in {'goal declare','goal amend'} else None
            raise ToolkitError('PLAN_SCHEMA_INVALID','The request file must contain a JSON object.',recovery=recovery)
        if verb=='describe':result=_describe(service.catalog,options.get('kind','capabilities'),options.get('name'))
        elif verb=='doctor':result=_doctor()
        elif verb=='run create':result=service.create(options['directory'],request)
        elif verb=='template instantiate':result=service.instantiate(options['name'],request)
        elif verb=='verify':result=service.verify(options.get('directory') or root)
        else:
            session=service.require_run()
            if verb not in {'status','record render'} and (service.root/'manifest.json').exists():raise ToolkitError('SEAL_RUN_NOT_COMPLETED','Sealed packages are immutable.')
            if verb=='goal declare':result=session.set_goal(request)
            elif verb=='goal amend':
                request=dict(request);reason=request.pop('reason',options.get('reason'))
                if not reason:raise ToolkitError('PLAN_WHY_MISSING','Goal amendment requires a reason.')
                result=session.set_goal(request,reason)
            elif verb=='pipeline submit':result=session.submit(request)
            elif verb=='pipeline revise':result=session.revise(request)
            elif verb=='run execute':
                result=execute(session,service.invoker,options.get('until'))
                if result.get('failure'):problems.append(_problem(result['failure']))
            elif verb=='status':result=service.status()
            elif verb=='judge':result=service.assess(options.get('also',()))
            elif verb=='seal':result=service.assess(options.get('also',()),publish=True)
            elif verb=='record render':result=service.render()
            elif verb=='declare':
                if not isinstance(request,dict) or set(request)-{'text','origin','about','basis_refs'}:raise ToolkitError('PLAN_PARAM_INVALID','A host declaration cannot select its actor.')
                with RunLock(service.root):
                    session.editable();event=session.declare(**request);result={'event':event['hash']}
            elif verb=='run abandon':
                result=session.abandon(options.get('reason') or 'Host abandoned this run.')
            elif verb=='review sign':raise ToolkitError('CHECK_UNAVAILABLE','Interactive human review signing is deferred beyond S1; no review has been signed.')
            else:raise ToolkitError('PLAN_PARAM_INVALID','Unknown command. Use describe.')
    except ToolkitError as error:
        problems.append(_problem(error.problem.as_dict()));result={'failure':error.problem.as_dict()}
    session=service.session if service else None
    try:count=len(session.events()) if session else 0;state=session.state() if session else None;label_set=service.label_values() if session else []
    except ToolkitError:count=before;state=None;label_set=[]
    receipt={'run_id':session.info['run_id'] if session else None,'state':state,'event_range':{'from_seq':before+1,'to_seq':count} if count>before else None,
             'result':result,'problems':problems,'next':[],'labels':label_set}
    return schemas.require('receipt-v1',receipt)


def _operation(verb):
    def operation(**arguments):return call(verb,**arguments)
    operation.__name__=verb.replace(' ','_')
    operation.__doc__='Receipt-returning API for grt '+verb+'.'
    return operation


# Python identifiers use underscores for the CLI's spaces, with no extra verbs.
__all__=[verb.replace(' ','_') for verb in json.loads(Path(__file__).with_name('verbs.json').read_text(encoding='utf-8'))]
for _name in __all__:globals()[_name]=_operation(_name.replace('_',' '))

"""A run is reconstructed from its immutable facts on each command."""
from copy import deepcopy
from pathlib import Path
from dna_design_core.kernel import canonical, ids, schemas
from dna_design_core.kernel.errors import ToolkitError
from dna_design_core.storage.journal import Journal
from dna_design_core.storage.store import Store
from dna_design_core.storage.lock import RunLock
from . import goal, normalize, admission

HOST={'kind':'ai_host','name':'host','version':'unknown'}


class Session:
    def __init__(self,root,catalog,config=None,*,journal_name='journal.ndjson'):
        self.root=Path(root).resolve();self.catalog=catalog;self.config=config or {}
        self.info=canonical.loads((self.root/'run.json').read_bytes())
        self.journal=Journal(self.root,self.info['run_id']);self.store=Store(self.root)
        self.journal.path=self.root/journal_name

    def events(self):return self.journal.events()

    def snapshot(self):
        created=next(e for e in self.events() if e['type']=='run.created')
        return self.store.get('documents',created['payload']['catalog_id'])

    def declarations(self):return {r['declaration']['id']:r for r in self.snapshot()['capabilities']}

    def current_goal(self):return goal.current(self.events())

    def current_pipeline(self):
        rows=[e['payload']['document'] for e in self.events() if e['type'] in {'pipeline.declared','pipeline.revised'}]
        return deepcopy(rows[-1]) if rows else None

    def steps(self):
        plan=self.current_pipeline() or {'steps':[]}
        result={s['step_id']:{'definition':s,'state':'PENDING','superseded_by':None,'started':None,'completed':None,'failure':None} for s in plan['steps']}
        for event in self.events():
            payload=event['payload'];name=payload.get('step_id')
            if name in result:
                if event['type']=='step.started':result[name].update(state='RUNNING',started=event)
                elif event['type']=='step.completed':result[name].update(state='COMPLETED',completed=event)
                elif event['type']=='step.failed':result[name].update(state='FAILED',failure=event)
            if event['type']=='pipeline.revised':
                for op in payload['operations']:
                    if op['op']=='supersede_step':result[op['step_id']]['superseded_by']=op['by']
        return result

    def state(self):
        events=self.events()
        if any(e['type']=='run.abandoned' for e in events):return 'ABANDONED'
        if self.current_pipeline() is None:return None
        latest_plan=max(e['seq'] for e in events if e['type'] in {'pipeline.declared','pipeline.revised'})
        if any(e['type']=='run.completed' and e['seq']>latest_plan for e in events):return 'COMPLETED'
        rows=self.steps().values()
        if any(r['state']=='FAILED' and not r['superseded_by'] for r in rows):return 'HALTED'
        return 'RUNNING' if any(r['started'] for r in rows) else 'PLANNED'

    def editable(self):
        if self.state()=='ABANDONED' or any(e['type']=='seal.created' for e in self.events()):
            raise ToolkitError('SEAL_RUN_NOT_COMPLETED','Run is abandoned or sealed; create a new run to continue.')

    def declare(self,text,origin='original_statement',about=None,basis_refs=()):
        payload={'text':text,'origin':origin,'actor':{'kind':'ai_host','name':'host'},'about':about or {'kind':'run','id':self.info['run_id']},'basis_refs':list(basis_refs)}
        return self.journal.append('declaration.recorded',payload,writer='engine',actor=HOST)

    def abandon(self,reason):
        with RunLock(self.root):
            self.editable()
            event=self.journal.append('run.abandoned',{'reason':reason,'by':HOST},writer='engine',actor=HOST)
            return {'event':event['hash']}

    def set_goal(self,document,reason=None):
        with RunLock(self.root):
            self.editable();previous=self.current_goal()
            if previous is not None and reason is None:raise ToolkitError('PLAN_GOAL_BINDING_INVALID','Use goal amend for a new version.')
            value=deepcopy(document)
            registered={e['payload']['source_id']:e['payload'] for e in self.events() if e['type']=='input.registered'}
            registrations=[]
            for source in value.get('sources',[]):
                if not isinstance(source,dict) or not isinstance(source.get('from'),str) or not source['from'] or 'path' in source or 'sha256' in source:
                    raise ToolkitError('PLAN_INPUT_UNBOUND','Request sources require from instead of path and sha256.')
                if not isinstance(source.get('source_id'),str) or not source['source_id']:
                    raise ToolkitError('PLAN_ID_INVALID','Each source needs a nonempty source_id.')
                supplied=Path(source.pop('from'))
                try:data=supplied.read_bytes()
                except OSError:
                    # The original pathname is request-only, including on failure.
                    raise ToolkitError('PLAN_INPUT_UNBOUND','Source file cannot be read.',{'source_id':source['source_id']}) from None
                checksum=ids.file_sha256(data)
                prior=registered.get(source['source_id'])
                if prior is not None and prior['file_sha256']!=checksum:
                    raise ToolkitError('PLAN_INPUT_UNBOUND','A registered source_id cannot identify different file content.',{'source_id':source['source_id']})
                relative=Path(prior['run_path']) if prior is not None else Path('inputs')/source['source_id']/supplied.name
                destination=(self.root/relative).resolve()
                if not destination.is_relative_to(self.root/'inputs'):raise ToolkitError('PLAN_INPUT_UNBOUND')
                if destination.exists() and destination.read_bytes()!=data:raise ToolkitError('SOURCE_CHANGED','Registered input copy cannot be replaced.')
                source.update(path=relative.as_posix(),sha256=checksum)
                registrations.append((source,data,destination,relative.as_posix()))
            # Validate the complete stored shape before copying or emitting facts.
            value=goal.prepare(value,previous,declarations=self.declarations())
            if previous is not None:
                payload=goal.amend_payload(previous,value,reason,HOST,any(e['type']=='step.started' for e in self.events()))
            for source,data,destination,relative in registrations:
                destination.parent.mkdir(parents=True,exist_ok=True)
                if not destination.exists():
                    with destination.open('xb') as stream:stream.write(data)
                if source['source_id'] not in registered:
                    self.journal.append('input.registered',{'source_id':source['source_id'],'file_sha256':source['sha256'],'size':len(data),'run_path':relative,'input_origin':source['input_origin'],'declared_by':HOST},writer='engine')
            self.store.put('documents',value)
            if previous is None:
                payload={'goal_digest':goal.digest(value),'version':value['version'],'document':value};kind='goal.declared'
            else:
                kind='goal.amended'
            self.journal.append(kind,payload,writer='engine',actor=HOST)
            return {'goal_digest':payload['goal_digest'],'version':value['version']}

    def admit(self,document):
        current=self.current_goal()
        if current is None:raise ToolkitError('PLAN_GOAL_BINDING_INVALID','Declare a goal before a pipeline.')
        declarations=self.declarations()
        plan=normalize.pipeline(document,declarations,{s['source_id'] for s in current['sources']})
        unavailable=[name for name in declarations if name not in self.catalog.entries or not self.catalog.available(name)]
        errors=admission.check(plan,current,declarations,self.steps(),unavailable)
        if plan.get('goal_digest')!=goal.digest(current):
            errors.append(ToolkitError('PLAN_GOAL_BINDING_INVALID','Pipeline uses a different goal.').problem.as_dict())
        if errors:raise ToolkitError('PLAN_SCHEMA_INVALID','Pipeline admission rejected.',{'problems':errors})
        return plan

    def submit(self,document):
        with RunLock(self.root):
            self.editable()
            if self.current_pipeline() is not None:raise ToolkitError('PLAN_SCHEMA_INVALID','Use pipeline revise after submission.')
            plan=self.admit(document)
            if plan['version']!=1:raise ToolkitError('PLAN_SCHEMA_INVALID','Initial pipeline must be version 1.')
            identity=ids.document_id(plan)
            self.journal.append('pipeline.declared',{'pipeline_digest':identity,'version':1,'document':plan,'goal_digest':plan['goal_digest'],'library_ref':plan.get('library_ref'),'unbound_targets':[t['id'] for t in self.current_goal()['targets'] if t['id'] not in {o['target'] for o in plan['outputs']}]},writer='engine',actor=HOST)
            for step in plan['steps']:self.declare(step['why'],'plan_declared',{'kind':'step','id':step['step_id']})
            return {'pipeline_digest':identity,'version':1}

    def revise(self,request):
        with RunLock(self.root):
            self.editable()
            request=normalize.revision(request,self.declarations(),{s['source_id'] for s in self.current_goal()['sources']})
            schemas.require('pipeline-revision-v1',request)
            old=self.current_pipeline()
            if old is None or request['expected_digest']!=ids.document_id(old):raise ToolkitError('PLAN_SCHEMA_INVALID','Revision expected_digest differs.')
            if not request['reason'].strip():raise ToolkitError('PLAN_WHY_MISSING')
            trigger=request['trigger'];events={e['hash']:e for e in self.events()}
            if trigger['kind'] in {'step_failed','check_failed'}:
                references=[events.get(key) for key in trigger['event_refs']]
                expected='step.failed' if trigger['kind']=='step_failed' else 'verdict.issued'
                if not references or any(e is None or e['type']!=expected for e in references):raise ToolkitError('PLAN_REF_UNRESOLVED','Revision trigger does not match evidence.')
                if expected=='verdict.issued' and any(e['payload']['verdict']['outcome'] not in {'FAIL','UNKNOWN'} for e in references):raise ToolkitError('PLAN_REF_UNRESOLVED')
                if expected=='step.failed' and any(e['payload']['step_id']!=trigger.get('step_id') or e['payload']['failure']['code']!=trigger.get('failure_code') for e in references):raise ToolkitError('PLAN_REF_UNRESOLVED')
            plan=deepcopy(old);states=self.steps();started={k for k,v in states.items() if v['started']}
            added={o['step']['step_id'] for o in request['operations'] if o['op']=='add_step'}
            for op in request['operations']:
                if op['op']=='add_step':
                    positions={s['step_id']:i for i,s in enumerate(plan['steps'])}
                    after=positions.get(op['after'])
                    if after is None or any(positions[k]>after for k in started):raise ToolkitError('PLAN_SCHEMA_INVALID','Cannot insert before an already started step.')
                    plan['steps'].insert(after+1,deepcopy(op['step']))
                elif op['op']=='supersede_step':
                    state=states.get(op['step_id'])
                    if state is None or state['state'] not in {'FAILED','PENDING'} or op['by'] not in added or op['by']==op['step_id']:raise ToolkitError('PLAN_SCHEMA_INVALID','Only failed or pending steps can be superseded by a new step.')
                    state['superseded_by']=op['by']
                else:plan['outputs']=deepcopy(op['outputs'])
            plan['version']+=1;plan['goal_digest']=goal.digest(self.current_goal())
            normalized=normalize.pipeline(plan,self.declarations(),{s['source_id'] for s in self.current_goal()['sources']})
            unavailable=[name for name in self.declarations() if name not in self.catalog.entries or not self.catalog.available(name)]
            errors=admission.check(normalized,self.current_goal(),self.declarations(),states,unavailable)
            if errors:raise ToolkitError('PLAN_SCHEMA_INVALID','Revision admission rejected.',{'problems':errors})
            identity=ids.document_id(normalized)
            reason_event=self.declare(request['reason'],'plan_declared',{'kind':'pipeline','id':identity},trigger['event_refs'])
            self.journal.append('pipeline.revised',{'pipeline_digest':identity,'version':normalized['version'],'previous_digest':ids.document_id(old),'document':normalized,'operations':request['operations'],'trigger':trigger,'reason_event':reason_event['hash']},writer='engine',actor=HOST)
            return {'pipeline_digest':identity,'version':normalized['version']}

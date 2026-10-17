"""Single capability execution boundary, including nested calls and replay."""
from copy import deepcopy
import inspect
import re
from pathlib import Path
import subprocess
import tempfile
import time
from dna_design_core.kernel import canonical, ids, material, schemas
from dna_design_core.kernel.public import Outcome
from dna_design_core.kernel.errors import ToolkitError
from dna_design_core.kernel.redact import safe,long_sequence_literal
from .view import ReadView
from .loading import Loader
from .file_effects import FileEffects,broker_io


def external_fingerprint(name,executable,timeout):
    """Local metadata probe before a run exists; no capability or sequence input."""
    path=Path(executable).resolve()
    try:data=path.read_bytes()
    except OSError:return None
    identity=ids.file_sha256(data);version='UNKNOWN'
    try:
        result=subprocess.run([str(path),'--about'],cwd=path.parent,capture_output=True,text=True,
            encoding='utf-8',errors='replace',timeout=timeout,check=False)
        match=re.search(r'release\s+(\d+\.\d+\.\d+)',result.stdout+result.stderr)
        if result.returncode==0 and match:version=match.group(1)
    except (OSError,subprocess.TimeoutExpired):pass
    if ids.file_sha256(path.read_bytes())!=identity:raise ToolkitError('SOURCE_CHANGED','Configured executable changed during its version probe.')
    return {'name':name,'version':version,'sha256':identity}


def output_ids(result):
    return {'materials':{k:[ids.material_id(v) for v in (data if isinstance(data,list) else [data])] for k,data in result.products.items()},
            'documents':{k:[ids.document_id(v)] for k,v in result.documents.items()},
            'artifacts':{k:ids.file_sha256(Path(v).read_bytes()) for k,v in result.artifacts.items()},
            'values':deepcopy(result.values)}


def input_ids(declaration,inputs):
    return {p['name']:(ids.file_sha256(Path(inputs[p['name']]).read_bytes()) if p['type']=='artifact' else ids.material_id(inputs[p['name']]) if p['type']=='material' else ids.document_id(inputs[p['name']])) for p in declaration['inputs'] if p['name'] in inputs}


class Context:
    def __init__(self,invoker,declaration,parent,workdir,view,replay):
        self._invoker=invoker;self._declaration=declaration;self._parent=parent;self._replay=replay
        self.workdir=Path(workdir);self.view=view;self.config=deepcopy(invoker.session.config)

    def knowledge(self,pack):
        owner=self._declaration['owner']
        if not isinstance(pack,str) or pack.split('/',1)[0]!=owner:
            raise ToolkitError('KNOWLEDGE_SOURCE_INVALID','Capability may only read its own owner\'s knowledge packages.')
        row=next((r for r in self._invoker.session.snapshot()['knowledge'] if r['pack']==pack),None)
        if row is None:raise ToolkitError('KNOWLEDGE_SOURCE_INVALID','Knowledge package is absent from the frozen catalog.')
        # Store.get rehashes the frozen bytes and returns a fresh parsed object.
        return self._invoker.session.store.get('documents',row['digest'])

    def call(self,use,*,inputs,params):
        if self._declaration['granularity']=='atomic':raise ToolkitError('CAPABILITY_OUTPUT_INVALID','Atomic capability cannot call another capability.')
        replay=self._replay or self._declaration['id'] in {'check.replay','check.model_agreement','check.reaction_chain','check.pcr_product','check.assembly_product'}
        if self._declaration['role']=='CHECK' and not replay:raise ToolkitError('CAPABILITY_OUTPUT_INVALID','This check has no replay-call authority.')
        with broker_io():
            return self._invoker._invoke(use,inputs,params,parent=self._parent,view=self.view,replay=replay,nested=True)

    def run_external(self,argv):
        if 'external_process' not in self._declaration['effects'] or self._declaration['role']=='CHECK':raise ToolkitError('CAPABILITY_OUTPUT_INVALID','External process is not declared.')
        if not isinstance(argv,list) or not argv or not all(isinstance(v,str) for v in argv):raise ToolkitError('PLAN_PARAM_INVALID','External command must be an argv array.')
        return subprocess.run(argv,cwd=self.workdir,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=self.config.get('external_timeout_s',300),check=True)


class Invoker:
    def __init__(self,session):self.session=session;self.calls=0;self._loader=Loader();self._temporary=[]

    def _load(self,entry):
        return self._loader.load(entry)

    def invoke(self,use,inputs,params,*,parent,view=None):
        if self.session.current_pipeline() is None:raise ToolkitError('PLAN_SCHEMA_INVALID','An admitted pipeline is required.')
        declaration=self.session.catalog.declaration(use)
        if declaration['role']=='ACTION' and not (view and view.candidate.get('stage_export')):
            step=next((s for s in self.session.current_pipeline()['steps'] if s['step_id']==parent),None)
            if step is None or step['use'].split('@')[0]!=declaration['id']:
                raise ToolkitError('PLAN_CAPABILITY_UNKNOWN','Action is not bound to the admitted parent step.')
        if view is not None:view=ReadView(view.root,view.events(),view._catalog,view.candidate)
        try:return self._invoke(use,inputs,params,parent=parent,view=view,replay=False,nested=False)
        finally:
            for directory in reversed(self._temporary):directory.cleanup()
            self._temporary=[]

    def _invoke(self,use,inputs,params,*,parent,view,replay,nested):
        self.calls+=1;name=use.split('@')[0];recorded=self.session.declarations().get(name)
        if recorded is None:raise ToolkitError('CAPABILITY_UNKNOWN',details={'id':name})
        declaration=self.session.catalog.declaration(use);entry=self.session.catalog.entries[name]
        if not self.session.catalog.available(use):raise ToolkitError('CHECK_UNAVAILABLE','Declared runtime dependency is unavailable.',{'capability':name})
        if (entry['code_digest'],entry['declaration_digest'])!=(recorded['code_digest'],recorded['declaration_digest']):raise ToolkitError('CAPABILITY_VERSION_MISMATCH',details={'id':name})
        schemas.require(declaration['params'],params,'PLAN_PARAM_INVALID')
        if long_sequence_literal(params):raise ToolkitError('PLAN_PARAM_INVALID','Sequences longer than 200 nt require a file.')
        expected={p['name']:p for p in declaration['inputs']}
        if inputs.keys()-expected.keys() or any(p['required'] and p['name'] not in inputs for p in expected.values()):raise ToolkitError('PLAN_INPUT_UNBOUND')
        for key,value in inputs.items():
            port=expected[key]
            if port['type']=='artifact' and not Path(value).is_file():raise ToolkitError('PLAN_INPUT_UNBOUND')
            if port['type']=='material':material.normalize(value)
            if port['type']=='materials':
                if not isinstance(value,list):raise ToolkitError('PLAN_INPUT_UNBOUND','materials input requires a list from an earlier materials output.')
                for item in value:material.normalize(item)
            if port['type']=='document':schemas.require(port.get('schema',port.get('schema_ref')),value,'PLAN_INPUT_UNBOUND')
            if port['type']=='value' and port['constraints']:schemas.require(port['constraints'],value,'PLAN_PARAM_INVALID')
        if nested and not replay:
            for key,value in inputs.items():
                kind=expected[key]['type']
                if kind=='artifact':self.session.store.put_file(Path(value).read_bytes())
                elif kind=='materials':
                    for item in value:self.session.store.put('materials',item)
                    self.session.store.put('documents',value)
                else:self.session.store.put('materials' if kind=='material' else 'documents',value)
        temporary=tempfile.TemporaryDirectory(prefix='grt_replay_') if replay or declaration['role']=='CHECK' else None
        if temporary:self._temporary.append(temporary)
        stage=bool(view and view.candidate.get('stage_export'))
        workdir=Path(temporary.name) if temporary else Path(view.candidate['root']) if stage else self.session.root/'work'/parent
        workdir.mkdir(parents=True,exist_ok=True)
        observer=FileEffects(self.session.root,workdir,'writes_files' in declaration['effects'],
            candidate=view.candidate['root'] if view and view.candidate.get('root') and declaration['role']=='CHECK' else None,
            artifacts=[value for key,value in inputs.items() if expected[key]['type']=='artifact'])
        started=time.perf_counter();result=None;failure=None
        try:
            with observer:
                function=self._load(entry);arguments={**deepcopy(inputs),**deepcopy(params)}
                inspect.signature(function).bind(Context(self,declaration,parent,workdir,view,replay),**arguments)
                result=function(Context(self,declaration,parent,workdir,view,replay),**arguments)
                result=deepcopy(result)
            if not isinstance(result,Outcome):raise ToolkitError('CAPABILITY_OUTPUT_INVALID','Capability must return Outcome.')
            if declaration['role']=='CHECK':
                if result.products or result.documents or result.artifacts or result.values or result.unverified:raise ToolkitError('CAPABILITY_OUTPUT_INVALID','CHECK Outcome may only contain verdicts.')
                for value in result.verdicts:schemas.require('verdict-v1',value,'CAPABILITY_OUTPUT_INVALID')
            else:
                emitted=set(result.products)|set(result.documents)|set(result.artifacts)|set(result.values)
                if emitted!={p['name'] for p in declaration['outputs']}:raise ToolkitError('CAPABILITY_OUTPUT_INVALID','Output ports differ from declaration.')
                for port in declaration['outputs']:
                    key=port['name'];kind=port['type']
                    if kind in {'material','materials'}:
                        data=result.products.get(key);items=data if kind=='materials' else [data]
                        if not isinstance(items,list):raise ToolkitError('CAPABILITY_OUTPUT_INVALID')
                        for item in items:material.normalize(item)
                    elif kind=='document':schemas.require(port.get('schema',port.get('schema_ref')),result.documents.get(key),'CAPABILITY_OUTPUT_INVALID')
                    elif kind=='artifact':
                        path=Path(result.artifacts.get(key,'')).resolve()
                        if not path.is_file() or not path.is_relative_to(workdir.resolve()) or 'writes_files' not in declaration['effects']:raise ToolkitError('CAPABILITY_OUTPUT_INVALID','Artifact is outside declared work directory.')
                    else:
                        canonical.dumps(result.values[key])
                        if safe(result.values[key])!=result.values[key]:raise ToolkitError('CAPABILITY_OUTPUT_INVALID','Return sequence content through a document or material port, not journal values.')
        except ToolkitError as error:failure=error
        except Exception as error:
            failure=ToolkitError('CAPABILITY_INTERNAL','Capability raised an undeclared exception.',{'type':type(error).__name__})
        if observer.violations:
            prior=' Body failure: '+failure.problem.code+'.' if failure else ''
            failure=ToolkitError('CAPABILITY_OUTPUT_INVALID','Out-of-scope file write or protected file change detected after capability execution.'+prior)
        if (nested or stage) and not replay and declaration['role']=='ACTION':
            payload={'parent':parent,'capability':{'id':name,'version':declaration['version'],'declaration_digest':recorded['declaration_digest'],'code_digest':recorded['code_digest']},
                     'input_ids':input_ids(declaration,inputs),'params':deepcopy(params),'params_digest':ids.document_id(params),
                     'duration_ms':int((time.perf_counter()-started)*1000)}
            if failure:payload['failure']=failure.problem.as_dict()
            else:
                for data in result.products.values():
                    for item in (data if isinstance(data,list) else [data]):self.session.store.put('materials',item)
                for data in result.documents.values():self.session.store.put('documents',data)
                for path in result.artifacts.values():self.session.store.put_file(Path(path).read_bytes())
                payload['outputs']=output_ids(result)
            self.session.journal.append('call.recorded',payload,writer='engine')
        if failure:raise failure
        return result

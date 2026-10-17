"""Composition root: the only layer assembling engine, assurance and record."""
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
import platform
import secrets
from importlib import metadata
from dna_design_core.kernel import canonical,ids,schemas
from dna_design_core.kernel.release import versions,core_version,release_id
from dna_design_core.kernel.errors import ToolkitError
from dna_design_core.storage.journal import Journal
from dna_design_core.storage.store import Store
from dna_design_core.storage.lock import RunLock
from dna_design_core.catalog.registry import Catalog
from dna_design_core.engine.session import Session,HOST
from dna_design_core.engine.invoker import Invoker,external_fingerprint
from dna_design_core.engine.view import ReadView
from dna_design_core.engine.executor import execute
from dna_design_core.assurance import stage,obligations,judge,seal,verify,labels
from dna_design_core.record.render.runcard import render
from . import config,describe


def _commit():
    # Read Git metadata only. No executable, checkout, or original input path is recorded.
    for ancestor in Path(__file__).resolve().parents:
        folder=ancestor/'.git'
        if folder.is_file():
            text=folder.read_text(encoding='utf-8').strip()
            if text.startswith('gitdir: '):folder=(ancestor/text[8:]).resolve()
        if not folder.is_dir():continue
        head=(folder/'HEAD').read_text(encoding='utf-8').strip()
        if head.startswith('ref: '):
            ref=folder/head[5:]
            if ref.exists():head=ref.read_text(encoding='utf-8').strip()
            else:
                packed=folder/'packed-refs'
                lines=packed.read_text(encoding='utf-8').splitlines() if packed.exists() else []
                head=next((line.split(' ')[0] for line in lines if line.endswith(' '+head[5:])), '')
        return head if len(head)==40 and set(head)<=set('0123456789abcdef') else None
    return None


class RunService:
    def __init__(self,root=None,*,kit_dirs=(),config_path=None,overrides=None):
        self.root=Path(root).resolve() if root is not None else None
        self.catalog=Catalog(kit_dirs);self.config=config.load(config_path,overrides)
        self.session=None
        if self.root is not None and (self.root/'run.json').exists():
            name='journal-until-seal.ndjson' if (self.root/'manifest.json').exists() else 'journal.ndjson'
            self.session=Session(self.root,self.catalog,self.config,journal_name=name)
        self.invoker=Invoker(self.session) if self.session else None

    def require_run(self):
        if self.session is None:raise ToolkitError('PLAN_INPUT_UNBOUND','Select an existing run directory.')
        return self.session

    def view(self,candidate=None):
        session=self.require_run()
        return ReadView(self.root,session.events(),session.snapshot(),candidate)

    def create(self,root,request=None):
        release=release_id()
        self.root=Path(root).resolve()
        if self.root.exists() and any(self.root.iterdir()):raise ToolkitError('PLAN_INPUT_UNBOUND','Run creation requires an empty directory.')
        self.root.mkdir(parents=True,exist_ok=True)
        tools=[];notices=list(self.catalog.notices)
        if self.config.get('primer3_core'):
            fingerprint=external_fingerprint('primer3_core',self.config['primer3_core'],self.config['external_timeout_s'])
            # PROVISIONAL(C2): unreadable binaries have no invented hash; report
            # unavailability while retaining local workflows that do not use them.
            if fingerprint:
                tools.append(fingerprint)
                if fingerprint['version']=='UNKNOWN':notices.append('Configured primer3_core version is unavailable; executable hash was recorded.')
            else:notices.append('Configured primer3_core is unavailable; no executable fingerprint could be recorded.')
        now=datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00','Z')
        identity=ids.run_id(now,secrets.token_hex(16))
        info={'run_id':identity,'created_at':now,'release_id':release}
        (self.root/'run.json').write_bytes(canonical.dumps(info))
        store=Store(self.root);snapshot=self.catalog.snapshot(release)
        for rule in self.catalog.knowledge.values():store.put('documents',rule)
        catalog_id=store.put('documents',snapshot)
        payload={'release_id':release,'schema_versions':versions()['schemas'],'created_by':HOST,
                 'environment':{'python':platform.python_version(),'platform':platform.system(),
                                'packages':{name:metadata.version(name) for name in ['rfc8785','jsonschema']},
                                'external_tools':tools,'config_digest':ids.document_id(self.config)},
                 'catalog_id':catalog_id,'catalog_ref':'store/documents/'+catalog_id+'.json','kits':self.catalog.kit_receipts}
        commit=_commit()
        if commit:payload['git_commit']=commit
        if request:
            if set(request)!={'derived_from'}:raise ToolkitError('PLAN_PARAM_INVALID')
            payload['derived_from']=request['derived_from']
        Journal(self.root,identity).append('run.created',payload,writer='application')
        self.session=Session(self.root,self.catalog,self.config);self.invoker=Invoker(self.session)
        return {'created':True,'release_id':release,'kit_diagnostics':self.catalog.problems,'notices':notices}

    def status(self):
        session=self.require_run();rows=session.steps()
        return {'steps':[{k:v for k,v in row.items() if k in {'state','superseded_by'}}|{'step_id':name} for name,row in rows.items()],
                'latest_verdicts':[e['payload']['verdict'] for e in session.events() if e['type']=='verdict.issued'],
                'sealed':any(e['type']=='seal.created' for e in session.events())}

    def label_values(self):
        if self.session is None:return []
        events=self.session.events();snapshot=self.session.snapshot()
        return list(labels.collect(events,snapshot,sealed=(self.root/'manifest.json').exists() or any(e['type']=='seal.created' for e in events),
                                   verdicts=[e['payload']['verdict'] for e in events if e['type']=='verdict.issued']).values())

    def assess(self,also=(),*,publish=False):
        session=self.require_run()
        with RunLock(self.root):
            existing=[e for e in session.events() if e['type']=='seal.created']
            if publish and existing:
                directory=self.root/'sealed'/existing[-1]['payload']['seal_id'];manifest,_=verify.inspect(directory)
                if not set(also)<={v['check'] for v in manifest['verdicts']}:raise ToolkitError('SEAL_RUN_NOT_COMPLETED','Create a new run to add requirements after sealing.')
                return {'sealed':True,'seal_id':directory.name,'manifest':str(directory/'manifest.json'),
                        'present_files':[str(directory/r['path']) for r in manifest['files'] if r['role']!='record']+
                                        [str(directory/'views/runcard.html'),str(directory/'views/report.md')],'labels':manifest['labels']}
            session.editable()
            if publish:seal.preconditions(session.state(),self.view())
            if session.current_pipeline() is None:raise ToolkitError('PLAN_SCHEMA_INVALID')
            candidate=stage.create(self.root,self.view(),session.snapshot(),self.invoker,self.view)
            required=obligations.derive(session.snapshot(),session.current_goal(),session.current_pipeline(),session.events(),also)
            result=judge.run(self.invoker,self.view,session.journal,candidate,required)
            if not publish:return result
            return seal.create(self.root,session.journal,candidate,result,required,session.snapshot(),session.current_goal(),session.current_pipeline(),
                               lambda events,label_set,not_done:render(events,session.snapshot(),label_set,not_done))

    def verify(self,directory):
        installed_release=release_id()
        root=Path(directory).resolve();original=None
        if not (root/'manifest.json').exists():
            original=Session(root,self.catalog,self.config)
            self.session=original;self.root=root
            events=original.events();sealed=[e for e in events if e['type']=='seal.created']
            if not sealed:raise ToolkitError('SEAL_RUN_NOT_COMPLETED','This run has no sealed package.')
            root=root/'sealed'/sealed[-1]['payload']['seal_id']
        manifest,events=verify.inspect(root)
        if manifest['release_id']!='dev-tree' and installed_release!='dev-tree' and manifest['release_id']!=installed_release:
            raise ToolkitError('SOURCE_CHANGED','Sealed release_id differs from the currently installed release manifest.',
                               {'recorded':manifest['release_id'],'installed':installed_release},
                               recovery='Verify with the matching installed release; do not change the sealed record.')
        session=Session(root,self.catalog,self.config,journal_name='journal-until-seal.ndjson');invoker=Invoker(session)
        if original is None:self.session=session;self.root=root
        view=lambda candidate:ReadView(root,events,session.snapshot(),candidate)
        result=verify.run(root,invoker,view,manifest,events,session.snapshot())
        if original:
            # Recorded by assurance, at its existing final-verdict seam.
            with RunLock(original.root):verify.record_result(original.journal,result)
        return result

    def render(self):
        session=self.require_run()
        if (self.root/'manifest.json').exists():raise ToolkitError('PLAN_INPUT_UNBOUND','A sealed package is immutable; use its existing views.')
        events=session.events();snapshot=session.snapshot();goal=session.current_goal() or {'intents':[],'constraints':[]}
        verdicts=[e['payload']['verdict'] for e in events if e['type']=='verdict.issued']
        label_set=labels.collect(events,snapshot,sealed=any(e['type']=='seal.created' for e in events),verdicts=verdicts)
        texts=render(events,snapshot,label_set,labels.not_verified(events,snapshot,goal,verdicts))
        directory=self.root/'views';directory.mkdir(exist_ok=True)
        for name,key in [('runcard.html','html'),('report.md','markdown')]:
            (directory/name).write_text(texts[key],encoding='utf-8',newline='\n')
        return {'files':[str(directory/'runcard.html'),str(directory/'report.md')],'language':'en','through_event':len(events)}

    def instantiate(self,name,request):
        template=self.catalog.describe('template',name);schemas.require(template['params_schema'],request,'PLAN_PARAM_INVALID')
        def replace(value):
            if isinstance(value,str) and value.startswith('{{') and value.endswith('}}'):return deepcopy(request[value[2:-2]])
            if isinstance(value,list):return [replace(v) for v in value]
            if isinstance(value,dict):return {k:replace(v) for k,v in value.items()}
            return value
        draft=replace({k:v for k,v in template.items() if k not in {'params_schema','authorship'}})
        draft['schema']='pipeline-v1'
        owner=next((kit for kit in self.catalog.kit_receipts if name.startswith(kit['name']+'.')),None)
        draft['library_ref']={'name':name,'version':owner['version'] if owner else core_version(),'template_digest':ids.document_id(template)}
        return {'draft':draft}

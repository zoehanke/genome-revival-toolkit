"""One capability registry and immutable-by-copy catalog snapshots."""
from copy import deepcopy
from importlib import metadata
from pathlib import Path
from dna_design_core.kernel import canonical, ids, schemas
from dna_design_core.kernel.errors import ToolkitError
from dna_design_core.kernel.vocab import RESOURCES, values
from . import kits

_PACKAGE=Path(__file__).resolve().parents[1]
BUNDLED=_PACKAGE/'kits' if (_PACKAGE/'kits').is_dir() else Path(__file__).resolve().parents[3]/'kits'


def _validate_declaration(declaration):
    schemas.require('capability-v1',declaration,'KIT_MANIFEST_INVALID')
    schemas.require_valid(declaration['params'])
    for port in declaration['inputs']+declaration['outputs']:
        if 'schema' in port:schemas.require_valid(port['schema'])


class Catalog:
    def __init__(self,kit_dirs=()):
        self.entries={};self.kit_receipts=[];self.problems=[];self.notices=[];self.templates={};self.knowledge={}
        blocked=set();disabled=set()
        for path in sorted((RESOURCES/'capabilities').glob('*.json')):
            declaration=canonical.loads(path.read_bytes())
            self._register(declaration,None,blocked,disabled)
        directories=[(path.parent,'bundled') for path in sorted(BUNDLED.glob('*/kit.json'))]+[(Path(path),'external') for path in kit_dirs]
        seen=set()
        for root,origin in directories:
            root=root.resolve()
            if root in seen:continue
            seen.add(root)
            try:
                manifest=kits.read(root)
                rows=[canonical.loads((root/name).read_bytes()) for name in manifest['contributes']['capabilities']]
                for row in rows:
                    _validate_declaration(row)
                    if row['owner']!='kit:'+manifest['name']:raise ToolkitError('KIT_MANIFEST_INVALID','Contribution owner differs from Kit.')
                    kits.code_path(row,root)
                knowledge=[]
                for name in manifest['contributes']['knowledge']:
                    value=canonical.loads((root/name).read_bytes());schemas.require('rule-v1',value,'KNOWLEDGE_SOURCE_INVALID');knowledge.append((name,value))
                templates=[]
                for name in manifest['contributes']['templates']:
                    value=canonical.loads((root/name).read_bytes());schemas.require('pipeline-template-v1',value,'KIT_MANIFEST_INVALID');templates.append((name,value))
                for row in rows:self._register(row,root,blocked,disabled)
                owner='kit:'+manifest['name']
                if owner in disabled:continue
                self.knowledge.update({owner+'/'+name:value for name,value in knowledge})
                self.templates.update({manifest['name']+'.'+Path(name).stem:value for name,value in templates})
                receipt={'name':manifest['name'],'version':manifest['version'],'manifest_sha256':ids.file_sha256((root/'kit.json').read_bytes()),
                         'code_digest':ids.document_id({name:ids.file_sha256((root/name).read_bytes()) for name in sorted(p.relative_to(root).as_posix() for p in (root/'capabilities').rglob('*.py'))}),
                         'origin':origin,'source':'explicit Kit directory' if origin=='external' else 'bundled Kit directory'}
                self.kit_receipts.append(receipt)
                if origin=='external':self.notices.append('External Kit '+manifest['name']+' will run code with your permissions; this version has no sandbox.')
            except (ToolkitError,OSError,ValueError) as error:
                failure=error if isinstance(error,ToolkitError) else ToolkitError('KIT_MANIFEST_INVALID','Cannot read Kit metadata.')
                self.problems.append(failure.problem.as_dict())
        self._validate_models(disabled)
        self.entries={k:v for k,v in self.entries.items() if v['declaration']['owner'] not in disabled}
        self.kit_receipts=[r for r in self.kit_receipts if 'kit:'+r['name'] not in disabled]
        self.knowledge={k:v for k,v in self.knowledge.items() if k.split('/',1)[0] not in disabled}
        self.templates={k:v for k,v in self.templates.items() if not any(k.startswith(owner.removeprefix('kit:')+'.') for owner in disabled)}

    def _register(self,declaration,root,blocked,disabled):
        _validate_declaration(declaration)
        path,module,function=kits.code_path(declaration,root)
        entry={'declaration':deepcopy(declaration),'declaration_digest':ids.document_id(declaration),'code_digest':ids.file_sha256(path.read_bytes()),
               'path':path,'root':root,'module':module,'function':function}
        name=declaration['id'];previous=self.entries.get(name)
        if name in blocked or previous and (previous['declaration_digest'],previous['code_digest'])!=(entry['declaration_digest'],entry['code_digest']):
            if declaration['owner']!='core':disabled.add(declaration['owner'])
            if previous and previous['declaration']['owner']!='core':disabled.add(previous['declaration']['owner']);self.entries.pop(name,None)
            blocked.add(name)
            self.problems.append(ToolkitError('KIT_NAME_CONFLICT',details={'id':name}).problem.as_dict())
            return
        if previous is None:self.entries[name]=entry

    def _validate_models(self,disabled):
        # Cross-declaration checks run after discovery, without importing code.
        while True:
            newly_disabled=set()
            for entry in self.entries.values():
                original=entry['declaration'];model_id=original.get('model')
                if not model_id or original['owner'] in disabled:continue
                model=self.entries.get(model_id,{}).get('declaration')
                reason=None
                if model is None or model['owner'] in disabled or model['role']!='ACTION':reason='model ACTION is unavailable'
                elif original['role']!='ACTION':reason='only an ACTION can declare a model'
                elif not {p['name'] for p in model['inputs']}<={p['name'] for p in original['inputs']}:reason='model input name is absent from original capability'
                elif not set(model['params'].get('properties',{}) if isinstance(model['params'],dict) else {})<=set(original['params'].get('properties',{}) if isinstance(original['params'],dict) else {}):reason='model parameter name is absent from original capability'
                elif any(not any(p['name']=='product' and p['type']=='material' for p in d['outputs']) for d in [original,model]):reason='model and original require a material product output'
                if reason:
                    error=ToolkitError('KIT_MANIFEST_INVALID',reason,{'capability':original['id'],'model':model_id})
                    if original['owner']=='core':raise error
                    self.problems.append(error.problem.as_dict());newly_disabled.add(original['owner'])
            if not newly_disabled:break
            disabled.update(newly_disabled)

    def declaration(self,use):
        name,_,version=use.partition('@')
        if name not in self.entries:raise ToolkitError('CAPABILITY_UNKNOWN',details={'id':name})
        value=self.entries[name]['declaration']
        if version and version!=value['version']:raise ToolkitError('CAPABILITY_VERSION_MISMATCH',details={'id':name})
        return deepcopy(value)

    def available(self,use):
        declaration=self.declaration(use)
        for runtime in declaration['requires_runtime']:
            if runtime['kind']=='python_package':
                try:metadata.version(runtime['name'])
                except metadata.PackageNotFoundError:return False
            elif not Path(runtime['name']).is_file():return False
        return True

    def snapshot(self,release_id):
        profiles=canonical.loads((RESOURCES/'profiles.json').read_bytes())
        value={'schema':'catalog-v1','release_id':release_id,
               'capabilities':[{'declaration':deepcopy(e['declaration']),'declaration_digest':e['declaration_digest'],'code_digest':e['code_digest'],'owner':e['declaration']['owner']} for _,e in sorted(self.entries.items())],
               'knowledge':[{'pack':name,'digest':ids.document_id(rule),'review':{'none':1,'draft':0,'reviewed':0,'stale':0}} for name,rule in sorted(self.knowledge.items())],
               'kits':[{k:v for k,v in item.items() if k!='source'} for item in self.kit_receipts],
               'profiles':profiles,'profiles_digest':ids.document_id(profiles),'vocab_digest':ids.document_id(canonical.loads((RESOURCES/'vocab.json').read_bytes()))}
        return schemas.require('catalog-v1',value)

    def describe(self,kind,name=None):
        if kind=='capability':return self.declaration(name)
        if kind=='kits':return deepcopy(self.kit_receipts)
        if kind=='vocab':return canonical.loads((RESOURCES/'vocab.json').read_bytes())
        if kind=='templates':return deepcopy(self.templates)
        if kind=='template':
            if name not in self.templates:raise ToolkitError('PLAN_REF_UNRESOLVED','Template is not registered.')
            return deepcopy(self.templates[name])
        rows=[self.declaration(key) for key in sorted(self.entries)]
        if kind=='checks':return [row for row in rows if row['role']=='CHECK']
        if kind=='goal-kinds':return [row for row in rows if row.get('evaluates_constraint')]
        return rows

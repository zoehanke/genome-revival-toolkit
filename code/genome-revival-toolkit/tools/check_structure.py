"""S0 static scanner. Reads a supplied tree; never imports runtime or Kit code."""
import argparse
import ast
import json
import re
import tomllib
from pathlib import Path

from check_schemas import check as check_schemas, load_schemas, validator_for
from jsonschema import Draft202012Validator, FormatChecker


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def module_name(path, source):
    parts = list(path.relative_to(source).with_suffix('').parts)
    if parts[-1] == '__init__':
        parts.pop()
    return '.'.join(parts)


def imported_names(tree, module, is_package):
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ''
            if node.level:
                parts = module.split('.') if is_package else module.split('.')[:-1]
                base = '.'.join(parts[:len(parts) - node.level + 1] + ([base] if base else []))
            names.extend(base + ('.' + alias.name if alias.name != '*' else '') for alias in node.names)
    return names


def aliases(tree):
    result = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                result[alias.asname or alias.name.split('.')[0]] = alias.name if alias.asname else alias.name.split('.')[0]
        elif isinstance(node, ast.ImportFrom) and not node.level:
            for alias in node.names:
                result[alias.asname or alias.name] = (node.module or '') + '.' + alias.name
    return result


def dotted(node, alias_map):
    if isinstance(node, ast.Name):
        return alias_map.get(node.id, node.id)
    if isinstance(node, ast.Attribute):
        return dotted(node.value, alias_map) + '.' + node.attr
    return ''


def walk_properties(schema):
    if isinstance(schema, dict):
        for key, value in schema.get('properties', {}).items():
            yield key
            yield from walk_properties(value)
        for key, value in schema.items():
            if key != 'properties':
                yield from walk_properties(value)
    elif isinstance(schema, list):
        for value in schema:
            yield from walk_properties(value)


def scan(root, spec_path=None):
    findings = []
    def report(code, path, message):
        name = path.relative_to(root).as_posix() if isinstance(path, Path) else path
        findings.append({'id':code, 'file':name, 'message':message})
    core = root/'src/dna_design_core'
    resources = core/'resources'
    contract = tomllib.loads((root/'contracts.toml').read_text(encoding='utf-8'))
    vocab = {k:{e['value'] for e in values} for k,values in read_json(resources/'vocab.json').items()}
    codes = {e['code'] for e in read_json(resources/'errors.json')}
    spec_path = spec_path or Path(__file__).resolve().parents[3]/'spec/SPEC.md'
    spec = spec_path.read_text(encoding='utf-8')
    excerpt = tomllib.loads(re.search(r'```toml\n(.*?)\n```',spec,re.S).group(1))
    for section, values in excerpt.items():
        for key,value in values.items():
            if contract.get(section,{}).get(key)!=value:
                report('CONTRACT',root/'contracts.toml',f'D1 mismatch: {section}.{key}')
    if contract['allow'].get('kernel')!=[] or contract['forbid_patterns'].get('except Exception')!=['engine/invoker.py','application/cli.py']:
        report('CONTRACT',root/'contracts.toml','DEP-1 or DEP-13 mismatch')
    glossary=spec.split('## 1. 词表',1)[1].split('**可信度的三个问题',1)[0]
    aliases_keys={'Run 状态':'run_state','Step 状态':'step_state','退出码':'exit_code','关系依据':'relation_basis','实验室状态标签':'laboratory_label','错误类别':'error_category'}
    for line in glossary.splitlines():
        if not line.startswith('| '): continue
        cells=line.split('|')
        label=cells[1].strip()
        key_match=re.search(r'`([a-z_]+)`',label)
        key=key_match.group(1) if key_match else aliases_keys.get(label)
        if key in vocab:
            expected=set(re.findall(r'`([A-Za-z_]+|\d+)`',re.sub(r'（[^）]*）','',cells[2])))
            if key=='exit_code': expected={int(x) for x in expected}
            if vocab[key]!=expected: report('VOCAB',resources/'vocab.json',f'Glossary mismatch: {key}')
    expected_codes=set(re.findall(r'\b(?:PLAN|CAPABILITY|SOURCE|STEP|JOURNAL|RUN|STORE|CHECK|KIT|KNOWLEDGE|SEAL)_[A-Z_]+\b',spec)) - {'CAPABILITY_FAILURE'}
    if codes!=expected_codes: report('ERRORS',resources/'errors.json','Error code set differs from current spec')
    defined=set(re.findall(r'^\| (INV-[A-Z]+\d+) \|',spec,re.M))
    covered=set(read_json(root/'tests/IMPLEMENTED_INV.json')['ids'])
    pending_rows=read_json(root/'tests/PENDING_INV.json')
    pending={row['id'] for row in pending_rows}
    if covered & pending or covered | pending != defined or len(pending)!=len(pending_rows) or any(not row.get('reason') or not row.get('stage') for row in pending_rows):
        report('INVENTORY',root/'tests/PENDING_INV.json','Invariant coverage partition is incomplete or ambiguous')
    profile=read_json(resources/'profiles.json')
    table=spec.split('基础档位（`profiles.json`，底盘数据，Kit 不能增改）：',1)[1].split('输出角色**',1)[0]
    for label,actual in [('任何封存包',profile['always']),('输出里含',profile['on_material_output']),('角色 `construct`',profile['roles']['construct']),('角色 `primer_set`',profile['roles']['primer_set'])]:
        row=next(line for line in table.splitlines() if line.startswith('| ') and label in line)
        if actual!=re.findall(r'`(check\.[a-z_.]+)`',row): report('PROFILES',resources/'profiles.json',f'D7 mismatch: {label}')
    if profile['roles']['component'] or profile['roles']['analysis']: report('PROFILES',resources/'profiles.json','Unexpected component/analysis additions')
    modules = {module_name(p,root/'src'):p for p in core.rglob('*.py')}
    edges = {key:set() for key in modules}
    for path in sorted(list(core.rglob('*.py')) + list((root/'kits').rglob('*.py'))):
        body = path.read_text(encoding='utf-8')
        tree = ast.parse(body, filename=path.name)
        is_core = path.is_relative_to(core)
        rel = path.relative_to(core).as_posix() if is_core else path.relative_to(root/'kits').as_posix()
        layer = rel.split('/')[0] if is_core else None
        kit = rel.split('/')[0] if not is_core else None
        module = module_name(path,root/'src') if is_core else rel.removesuffix('.py').replace('/','.')
        names = imported_names(tree,module,path.name=='__init__.py')
        amap = aliases(tree)
        for name in names:
            if name.startswith('dna_design_core.'):
                target = name.removeprefix('dna_design_core.')
                if is_core:
                    allowed = contract['allow'].get(layer,[]) + [layer]
                    if not any(target==a or target.startswith(a+'.') for a in allowed if a):
                        report('INV-L1',path,f'{module} cannot import {name}')
                    for candidate in modules:
                        if name==candidate or name.startswith(candidate+'.'):
                            # Select longest matching actual module, rather than package prefixes.
                            match=max((m for m in modules if name==m or name.startswith(m+'.')),key=len)
                            edges[module].add(match)
                            break
                else:
                    if not any(name==a or name.startswith(a+'.') for a in contract['kit_allow']['*']):
                        report('INV-L2',path,f'Kit cannot import {name}')
                        report('INV-K2',path,f'Kit cannot import {name}')
                if is_core and layer=='record' and not (target.startswith('kernel.') or target=='kernel' or target.startswith('storage.read') or target.startswith('record.')):
                    report('INV-T1',path,'Record import is not read-only surface')
            elif not is_core:
                other = name.split('.')[0]
                kit_names = {p.name.replace('-','_') for p in (root/'kits').iterdir() if p.is_dir()}
                if other in kit_names and other != kit.replace('-','_'):
                    report('INV-K6',path,'Cross-Kit import')
                    report('INV-L2',path,'Cross-Kit import')
                    report('INV-K2',path,'Cross-Kit import')
            if name=='hashlib' or name.startswith('hashlib.'):
                if not is_core or rel!='kernel/ids.py': report('INV-I1',path,'Hash implementation outside kernel/ids.py')
            if name.split('.')[0] in {'pip','urllib','requests','socket'} or name.startswith('http.client'):
                report('INV-X3',path,'Network import in runtime')
        if not is_core:
            if '/capabilities/' not in '/'+rel or 'argparse' in names:
                report('INV-K1',path,'Kit Python must be a capability, without separate CLI')
        for node in ast.walk(tree):
            if isinstance(node,(ast.Name,ast.Attribute)):
                name=dotted(node,amap)
                if name in {'os.environ','os.getenv','os.putenv'} and (not is_core or rel!='application/config.py'):
                    report('INV-X1',path,'Environment access outside application/config.py')
                if is_core and 'snapgene' in name.lower() and not rel.startswith('biology/formats/'):
                    report('INV-F4',path,'Format trademark identifier outside format adapter')
            if isinstance(node,ast.Call):
                name=dotted(node.func,amap)
                if name=='print' and (not is_core or rel!='application/cli.py'):
                    report('DEP-12',path,'print outside CLI')
                if any(k.arg=='shell' and isinstance(k.value,ast.Constant) and k.value.value is True for k in node.keywords):
                    report('INV-X4',path,'shell=True')
                if is_core and layer=='record' and name.split('.')[-1] in {'append_event','write_event','emit_event'}:
                    report('INV-T1',path,'Record attempts to write journal')
                if not is_core and name.split('.')[-1] in {'render_report','render_card','main'}:
                    report('INV-K1',path,'Kit has CLI/report entry')
            if isinstance(node,ast.ExceptHandler) and (node.type is None or dotted(node.type,amap) in {'Exception','BaseException'}):
                if not is_core or rel not in {'engine/invoker.py','application/cli.py'}:
                    report('DEP-13',path,'Broad exception catch outside boundary')
            if isinstance(node,ast.ClassDef):
                if node.name.startswith('GATE_'): report('INV-D5',path,'Retired gate exception')
                if any(dotted(b,amap).split('.')[-1] in {'Exception','BaseException','ToolkitError','CapabilityError'} for b in node.bases):
                    if node.name not in {'ToolkitError','CapabilityError'}:
                        report('INV-V3',path,'Unregistered exception class')
            if isinstance(node,ast.Raise) and isinstance(node.exc,ast.Call):
                candidates=[k.value for k in node.exc.keywords if k.arg=='code'] + node.exc.args[:1]
                for arg in candidates:
                    if isinstance(arg,ast.Constant) and isinstance(arg.value,str) and re.fullmatch('[A-Z][A-Z0-9_]+',arg.value) and arg.value not in codes:
                        report('INV-V2',path,'Raised error code absent from errors.json')
            if isinstance(node,ast.Constant) and isinstance(node.value,str):
                if node.value.startswith('GATE_'): report('INV-D5',path,'Retired gate error code')
                if re.fullmatch(r'\d+\.\d+\.\d+(?:[-+][\w.-]+)?',node.value):
                    report('INV-W1',path,'Handwritten runtime version literal')
            pairs=[]
            if isinstance(node,ast.Dict):
                pairs=[(k.value,v) for k,v in zip(node.keys,node.values) if isinstance(k,ast.Constant) and isinstance(k.value,str)]
            elif isinstance(node,ast.Call): pairs=[(k.arg,k.value) for k in node.keywords]
            elif isinstance(node,ast.Assign): pairs=[(t.id,node.value) for t in node.targets if isinstance(t,ast.Name)]
            for key,value in pairs:
                allowed = vocab.get(key) if key in {'outcome','scope','moment','issuer'} else vocab['run_state']|vocab['step_state'] if key=='state' else None
                # A14 permits state=null before a plan or before any run exists.
                if allowed is not None and isinstance(value,ast.Constant) and value.value not in allowed and not (key=='state' and value.value is None):
                    report('INV-V1',path,f'Unknown {key} literal')
    visiting,done=set(),set()
    def visit(key):
        if key in visiting:
            report('INV-L3',modules[key],'Import cycle'); return
        if key in done: return
        visiting.add(key)
        for child in sorted(edges[key]): visit(child)
        visiting.remove(key); done.add(key)
    for key in sorted(edges): visit(key)
    schema_findings,_=check_schemas(root)
    for finding in schema_findings: report('SCHEMA', 'tests/fixtures/schemas',finding)
    schemas,registry=load_schemas(root)
    for kind,banned in [('pipeline-v1',{'checks','gates','required_scopes','deliver_as','status','result'}),('kit-v1',{'profiles','roles','gates','required_scopes','deliver_as','admission','delivery_classes'})]:
        schema=schemas['urn:grt:schema:'+kind]
        if schema.get('additionalProperties') is not False or set(walk_properties(schema)) & banned:
            report('INV-P2' if kind=='pipeline-v1' else 'INV-K7',resources/'schemas'/f'{kind}.json','Forbidden fields or open root')
    for path in (resources/'schemas').glob('*.json'):
        if path.stem in {'check-v1','assessor-v1','gate-v1'}: report('INV-C6',path,'Parallel callable declaration')
    for path in core.rglob('*.py'):
        if path.stem in {'check_registry','assessor_registry','gate_registry'}: report('INV-C6',path,'Parallel callable registry')
    declarations=list((resources/'capabilities').glob('*.json'))+list((root/'kits').glob('*/capabilities/*.json'))
    seen={}
    for path in declarations:
        value=read_json(path)
        if value.get('schema')!='capability-v1': report('INV-C6',path,'Not the single callable declaration shape'); continue
        if not value.get('does_not_establish') or len(value.get('summary',''))>200: report('INV-C2',path,'Missing limitation or long summary')
        name=value.get('id','')
        if name in seen and value!=seen[name]: report('INV-C5',path,'Conflicting duplicate capability id')
        seen[name]=value
        check=bool(re.match(r'^(check\.|[a-z][a-z0-9_]*\.check_)',name))
        if check!=(value.get('role')=='CHECK'): report('INV-C8',path,'CHECK/ACTION id prefix does not match role')
        if 'writes_files' not in value.get('effects',[]):
            # INV-C4 is deliberately a direct-call heuristic, paired with the
            # Invoker's post-call observer. It is not an OS sandbox or a proof
            # about arbitrary helper/native code.
            module,_,function=value.get('source',{}).get('implemented_in','').partition(':')
            base=core if module.startswith('dna_design_core.') else path.parents[1]
            source=base.joinpath(*module.split('.')[1:]).with_suffix('.py')
            if not source.is_file():source=base.joinpath(*module.split('.')[1:])/'__init__.py'
            if source.is_file():
                tree=ast.parse(source.read_text(encoding='utf-8'))
                body=next((n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==function),None)
                if body is not None:
                    # Loading the module also executes its top-level statements.
                    top=ast.Module(body=[n for n in tree.body if not isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))],type_ignores=[])
                    for call in (n for part in (body,top) for n in ast.walk(part) if isinstance(n,ast.Call)):
                        method=call.func.attr if isinstance(call.func,ast.Attribute) else call.func.id if isinstance(call.func,ast.Name) else ''
                        mode=next((k.value for k in call.keywords if k.arg=='mode'),call.args[1] if len(call.args)>1 else None)
                        writes=method in {'write_text','write_bytes','mkdir','unlink','rmdir','rename'} or method=='open' and isinstance(mode,ast.Constant) and isinstance(mode.value,str) and any(c in mode.value for c in 'wax+')
                        if writes:report('INV-C4',source,'Direct filesystem write without writes_files declaration')
        for key in ('params',):
            try: Draft202012Validator.check_schema(value[key])
            except Exception as exc: report('SCHEMA',path,f'Invalid embedded {key}: {type(exc).__name__}')
    rule_paths=list((core/'knowledge/packs').rglob('*.json'))+list((root/'kits').glob('*/knowledge/*.json'))
    validator=validator_for(schemas['urn:grt:schema:rule-v1'],registry)
    for path in rule_paths:
        value=read_json(path)
        if isinstance(value,dict) and value.get('schema')=='rule-v1' and not validator.is_valid(value): report('INV-N1',path,'Rule has missing/invalid source or contract')
    for path in (root/'tests/fixtures').rglob('*.json'):
        if path.name=='MANIFEST.json': continue
        fixture=read_json(path)
        if not isinstance(fixture,dict) or fixture.get('oracle',{}).get('kind') not in {'construction','hand','published','independent_program'}:
            report('INV-Q3',path,'Fixture requires independent oracle category')
    project=tomllib.loads((root/'pyproject.toml').read_text(encoding='utf-8'))
    if 'version' in project['project'] or 'version' not in project['project'].get('dynamic',[]) or project.get('tool',{}).get('setuptools',{}).get('dynamic',{}).get('version',{}).get('attr')!='tools.build_release.VERSION':
        report('INV-W2',root/'pyproject.toml','Version must come from VERSIONS via build provider')
    ignored=(root/'.gitignore').read_text(encoding='utf-8')
    for entry in ['__pycache__/','build/','dist/','probes/runs/','spikes/runs/']:
        if entry not in ignored: report('INV-F5',root/'.gitignore',f'Missing generated-artifact exclusion: {entry}')
    skips=read_json(root/'tests/SKIPS.json')
    for item in skips:
        if not all(item.get(k) for k in ['test','reason','condition','expires']): report('INV-Q4',root/'tests/SKIPS.json','Incomplete skip record')
        else:
            from datetime import date
            if item['expires']<date.today().isoformat(): report('INV-Q4',root/'tests/SKIPS.json','Expired skip record')
    for path in (root/'tests').rglob('*.py'):
        tree=ast.parse(path.read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if isinstance(node,ast.Call) and dotted(node.func,{}).split('.')[-1] in {'skip','skipIf','skipUnless','skipTest'} and not skips:
                report('INV-Q4',path,'Skip without a registered reason')
    return findings


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--spec',type=Path)
    args=parser.parse_args()
    findings=scan(args.root,args.spec)
    print(json.dumps({'findings':findings},ensure_ascii=False,indent=2))
    return bool(findings)


if __name__=='__main__':
    raise SystemExit(main())

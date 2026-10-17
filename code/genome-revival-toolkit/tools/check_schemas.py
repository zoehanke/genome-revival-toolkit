"""Development-only, offline Draft 2020-12 schema/fixture checker."""
import argparse
import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker, RefResolver
from jsonschema.exceptions import SchemaError, ValidationError


def load_schemas(root):
    schemas = {}
    for path in (root / 'src/dna_design_core/resources/schemas').rglob('*.json'):
        value = json.loads(path.read_text(encoding='utf-8'))
        Draft202012Validator.check_schema(value)
        schemas[value['$id']] = value
    return schemas, schemas


def validator_for(schema,registry):
    def unavailable(uri):raise ValueError('Schema reference is not present in the local set.')
    resolver=RefResolver.from_schema(schema,store=registry,handlers={key:unavailable for key in ['http','https','file','urn']})
    return Draft202012Validator(schema,resolver=resolver,format_checker=FormatChecker())


def template_errors(template):
    """A14 cross-field checks only; no substitution or capability execution."""
    definitions=template.get('params_schema',{})
    parameters=definitions.get('properties',{}) if isinstance(definitions,dict) else {}
    def walk(value):
        if isinstance(value,dict):
            for key,item in value.items():
                if '{{' in key or '}}' in key:
                    yield ValidationError('A14 placeholders are values, not object keys.')
                yield from walk(item)
        elif isinstance(value,list):
            for item in value: yield from walk(item)
        elif isinstance(value,str) and ('{{' in value or '}}' in value):
            match=re.fullmatch(r'\{\{([a-z][a-z0-9_]{0,31})\}\}',value)
            if not match:
                yield ValidationError('A14 requires a whole-string placeholder with a valid lowercase name.')
                return
            definition=parameters.get(match.group(1))
            if not isinstance(definition,dict) or 'type' not in definition:
                yield ValidationError('A14 placeholder must name a parameter with an explicit type.')
            if not isinstance(definition,dict) or not isinstance(definition.get('description'),str) or not definition['description'].strip():
                yield ValidationError('A14 placeholder parameter must have a description.')
    # Parameter declarations and authorship describe the template; they are not
    # values to substitute in the instantiated pipeline.
    yield from walk({k:v for k,v in template.items() if k not in {'params_schema','authorship'}})


def check(root):
    schemas, registry = load_schemas(root)
    counts, findings = {}, []
    for path in sorted((root / 'tests/fixtures/schemas').glob('*.json')):
        fixture = json.loads(path.read_text(encoding='utf-8'))
        key = 'urn:grt:schema:' + fixture['schema_id']
        validator = validator_for(schemas[key],registry)
        errors = list(validator.iter_errors(fixture['data']))
        declarations=[]
        if fixture['schema_id']=='capability-v1': declarations=[(fixture['data'],'params')]
        elif fixture['schema_id']=='pipeline-template-v1': declarations=[(fixture['data'],'params_schema')]
        elif fixture['schema_id']=='catalog-v1': declarations=[(v.get('declaration',{}),'params') for v in fixture['data'].get('capabilities',[]) if isinstance(v,dict)]
        for declaration,field in declarations:
            if field in declaration:
                try: Draft202012Validator.check_schema(declaration[field])
                except SchemaError as error: errors.append(error)
            if field=='params':
                for port in declaration.get('inputs',[])+declaration.get('outputs',[]):
                    if 'schema' in port:
                        try: Draft202012Validator.check_schema(port['schema'])
                        except SchemaError as error: errors.append(error)
        if fixture['schema_id']=='pipeline-template-v1':
            errors.extend(template_errors(fixture['data']))
        actual = not errors
        if actual != fixture['expected_valid']:
            findings.append(f'{path.name}: expected {fixture["expected_valid"]}, got {actual}: ' + '; '.join(e.message[:160] for e in errors[:3]))
        if fixture.get('oracle', {}).get('kind') not in {'construction','hand','published','independent_program'}:
            findings.append(f'{path.name}: missing oracle')
        counter = counts.setdefault(key, [0, 0])
        counter[0 if fixture['expected_valid'] else 1] += 1
    for key, schema in schemas.items():
        if not schema.get('x-spec-ref'):
            findings.append(f'{key}: missing x-spec-ref')
        good, bad = counts.get(key, [0, 0])
        if good < 1 or bad < 2:
            findings.append(f'{key}: needs >=1 valid and >=2 invalid fixture')
    return findings, {'schemas': len(schemas), 'fixtures': sum(sum(v) for v in counts.values())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    findings, counts = check(args.root)
    print(json.dumps({'counts': counts, 'findings': findings}, ensure_ascii=False, indent=2))
    return bool(findings)


if __name__ == '__main__':
    raise SystemExit(main())

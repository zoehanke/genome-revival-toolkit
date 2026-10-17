"""Offline JSON Schema validation through the allowed jsonschema dependency."""
from copy import deepcopy
from functools import lru_cache
import json
import re
from jsonschema import Draft202012Validator, FormatChecker, RefResolver
from jsonschema.exceptions import RefResolutionError, SchemaError
from .vocab import RESOURCES
from .errors import ToolkitError


@lru_cache(maxsize=1)
def _documents():
    return {s['$id']:s for s in (json.loads(p.read_text(encoding='utf-8')) for p in (RESOURCES/'schemas').rglob('*.json'))}


def document(name):
    return deepcopy(_documents()['urn:grt:schema:'+name])


def _unavailable(uri):
    raise ToolkitError('PLAN_SCHEMA_INVALID','Schema reference is not in the local schema set.')


def validator(schema):
    resolver=RefResolver.from_schema(schema,store=_documents(),handlers={k:_unavailable for k in ['http','https','file','urn']})
    return Draft202012Validator(schema,resolver=resolver,format_checker=FormatChecker())


@lru_cache(maxsize=64)
def _named_validator(name):
    schema=document(name) if not name.startswith('urn:') else {'$ref':name}
    Draft202012Validator.check_schema(schema)
    return validator(schema)


def _findings(compiled,value):
    findings=[];seen=set()
    for error in compiled.iter_errors(value):
        paths=[list(error.absolute_path)]
        if error.validator=='required' and isinstance(error.instance,dict):
            paths=[[*error.absolute_path,key] for key in error.validator_value if key not in error.instance]
        elif error.validator=='additionalProperties' and error.validator_value is False and isinstance(error.instance,dict):
            extras=[key for key in error.instance if key not in error.schema.get('properties',{}) and not any(re.search(pattern,key) for pattern in error.schema.get('patternProperties',{}))]
            if extras:paths=[[*error.absolute_path,key] for key in sorted(extras)]
        # Describe the failed constraint without echoing a submitted value/sequence.
        reason={'required':'Required field is missing.',
                'additionalProperties':'Field is not allowed by this document shape.',
                'type':'Value has the wrong JSON type.',
                'enum':'Value is outside the allowed choices.',
                'const':'Value differs from the required constant.'}.get(error.validator,
                    'Value does not satisfy the '+str(error.validator)+' constraint.')
        for path in paths:
            location='/'+ '/'.join(str(part).replace('~','~0').replace('/','~1') for part in path)
            key=(location,error.validator)
            if key not in seen:
                findings.append({'location':location,'rule':error.validator,'reason':reason});seen.add(key)
    return findings


def issues(name,value):
    try:
        if isinstance(name,str):
            return _findings(_named_validator(name),value)
        schema=name
        Draft202012Validator.check_schema(schema)
        return _findings(validator(schema),value)
    except (RefResolutionError,SchemaError):
        return [{'location':'','rule':'schema_reference','reason':'Schema reference or schema definition is invalid.'}]


def require(name,value,code='PLAN_SCHEMA_INVALID',*,recovery=None):
    findings=issues(name,value)
    if findings:raise ToolkitError(code,'Document violates its declared schema: '+findings[0]['location']+': '+findings[0]['reason'],{'findings':findings},recovery=recovery)
    return value


def require_valid(schema,code='KIT_MANIFEST_INVALID'):
    try:Draft202012Validator.check_schema(schema)
    except SchemaError as error:
        raise ToolkitError(code,'Embedded JSON Schema is invalid.') from error

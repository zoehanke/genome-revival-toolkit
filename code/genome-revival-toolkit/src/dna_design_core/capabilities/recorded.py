"""Read actual invocation parameters and immutable input values through public views."""
from copy import deepcopy
from dna_design_core.kernel.public import ToolkitError,document_id,file_sha256


def catalog(view):
    value=view.candidate.get('catalog')
    return value if value is not None else view.document(view.events('run.created')[0]['payload']['catalog_id'])


def parameters(payload):
    if 'params' not in payload or 'params_digest' not in payload:
        raise ToolkitError('CHECK_UNAVAILABLE','Recorded invocation has no actual parameter values.')
    if document_id(payload['params'])!=payload['params_digest']:
        raise ToolkitError('STORE_CORRUPT','Recorded invocation parameter digest differs.')
    return deepcopy(payload['params'])


def nested_inputs(view,declaration,payload):
    result={}
    for port in declaration['inputs']:
        name=port['name']
        if name not in payload['input_ids']:continue
        identity=payload['input_ids'][name]
        if port['type']=='material':value=view.material(identity)
        elif port['type']=='artifact':
            value=view.root/'store/artifacts'/identity
            if not value.is_file() or file_sha256(value.read_bytes())!=identity:raise ToolkitError('STORE_CORRUPT','Recorded artifact input differs.')
        else:value=view.document(identity)
        result[name]=value
    return result

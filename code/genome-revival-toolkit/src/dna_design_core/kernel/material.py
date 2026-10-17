"""Content-only material normalization. Display metadata and lineage are excluded."""
from copy import deepcopy
from .errors import ToolkitError


def normalize(value):
    if not isinstance(value,dict) or not isinstance(value.get('sequence'),str):
        raise ToolkitError('CAPABILITY_OUTPUT_INVALID','Material requires a sequence string.')
    sequence=value['sequence'].upper()
    if any(base not in 'ACGTRYSWKMBDHVN' for base in sequence):
        raise ToolkitError('CAPABILITY_OUTPUT_INVALID','Material contains an invalid DNA symbol.')
    features=deepcopy(value.get('features',[]))
    if not isinstance(features,list):raise ToolkitError('CAPABILITY_OUTPUT_INVALID','Features must be an array.')
    for feature in features:
        if not isinstance(feature,dict) or not all(k in feature for k in ['start','end','type','label']):
            raise ToolkitError('CAPABILITY_OUTPUT_INVALID','Feature requires start, end, type and label.')
        if type(feature['start']) is not int or type(feature['end']) is not int or not 0<=feature['start']<=feature['end']<=len(sequence):
            raise ToolkitError('CAPABILITY_OUTPUT_INVALID','Feature interval is outside material.')
    features.sort(key=lambda f:(f['start'],f['end'],f['type'],f['label']))
    return {'sequence':sequence,'topology':value.get('topology'),'strandedness':value.get('strandedness'),
            'ends':deepcopy(value.get('ends')),'features':features}

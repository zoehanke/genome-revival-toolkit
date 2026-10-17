"""Read and validate an event chain without changing any bytes."""
from dna_design_core.kernel import canonical, ids, schemas
from dna_design_core.kernel.errors import ToolkitError


def inspect(data):
    events=[];offset=0;previous=ids.GENESIS
    lines=data.splitlines(keepends=True)
    for index,line in enumerate(lines):
        try:
            value=canonical.loads(line)
            schemas.require('event-v1',value)
            if value['seq']!=index+1 or value['prev']!=previous or value['hash']!=ids.event_hash(value):
                raise ToolkitError('JOURNAL_CHAIN_BROKEN')
        except (ToolkitError,KeyError,TypeError,ValueError):
            if index!=len(lines)-1:
                raise ToolkitError('JOURNAL_CHAIN_BROKEN','Non-tail journal corruption.',{'seq':index+1})
            return events,offset,len(data)-offset
        events.append(value);previous=value['hash'];offset+=len(line)
    return events,offset,0


def read(path):
    if not path.exists():return []
    events,_,discarded=inspect(path.read_bytes())
    if discarded:raise ToolkitError('JOURNAL_CHAIN_BROKEN','Journal has an invalid final event; execute may recover the tail.',{'discarded_bytes':discarded})
    return events

"""One append implementation. Callers are constrained by the Appendix E matrix."""
from datetime import datetime, timezone
from pathlib import Path
import os
from dna_design_core.kernel import canonical, ids, schemas
from dna_design_core.kernel.errors import ToolkitError
from dna_design_core.kernel.release import core_version
from . import chain

ENGINE={'goal.declared','goal.amended','input.registered','pipeline.declared','pipeline.revised',
        'declaration.recorded','step.started','step.completed','step.failed','call.recorded',
        'run.halted','run.completed','run.abandoned'}


def owner(kind,payload):
    if kind in ENGINE:return 'engine'
    if kind=='run.created':return 'application'
    if kind=='journal.recovered':return 'storage'
    if kind=='verdict.issued':return 'engine' if payload['verdict']['moment']=='step' else 'assurance'
    if kind in {'judge.finished','seal.rejected','seal.created'}:return 'assurance'
    return None


class Journal:
    def __init__(self,root,run_id):
        self.path=Path(root)/'journal.ndjson'
        self.run_id=run_id

    def events(self):return chain.read(self.path)

    def append(self,kind,payload,*,writer,actor=None):
        if owner(kind,payload)!=writer:raise ToolkitError('CAPABILITY_INTERNAL','Event writer violates Appendix E.')
        history=self.events()
        event={'seq':len(history)+1,'time':datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00','Z'),
               'run_id':self.run_id,'type':kind,'actor':actor or {'kind':'program','name':'grt','version':core_version()},
               'payload':payload,'refs':[],'prev':history[-1]['hash'] if history else ids.GENESIS}
        event['hash']=ids.event_hash(event)
        schemas.require('event-v1',event,'CAPABILITY_OUTPUT_INVALID')
        data=canonical.dumps(event)+b'\n'
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.path.open('ab') as stream:
            if stream.write(data)!=len(data):raise OSError('Short journal write')
            stream.flush();os.fsync(stream.fileno())
        return canonical.loads(canonical.dumps(event))

    def recover(self):
        if not self.path.exists():return
        _,offset,discarded=chain.inspect(self.path.read_bytes())
        if discarded:
            with self.path.open('r+b') as stream:
                stream.truncate(offset);stream.flush();os.fsync(stream.fileno())
            self.append('journal.recovered',{'discarded_bytes':discarded,'reason':'Invalid or incomplete last event.'},writer='storage')

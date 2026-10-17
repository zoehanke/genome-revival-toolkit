"""Read projections passed to CHECKs, without exposing a journal writer."""
from copy import deepcopy
from pathlib import Path
from dna_design_core.kernel.references import resolve as resolve_reference, pointer
from dna_design_core.storage.store import Store
from dna_design_core.storage import read
from . import goal


class ReadView:
    def __init__(self,root,events,catalog,candidate=None):
        self.root=Path(root);self._events=deepcopy(events);self._catalog=deepcopy(catalog);self._candidate=deepcopy(candidate or {})
        self._store=Store(self.root)
        self.goal=goal.current(self._events)
        plans=[e['payload']['document'] for e in self._events if e['type'] in {'pipeline.declared','pipeline.revised'}]
        self.pipeline=deepcopy(plans[-1]) if plans else None

    @property
    def candidate(self):return deepcopy(self._candidate)

    def events(self,filter=None):return deepcopy([e for e in self._events if filter is None or e['type']==filter])

    def steps(self):
        superseded={op['step_id'] for e in self._events if e['type']=='pipeline.revised' for op in e['payload']['operations'] if op['op']=='supersede_step'}
        result=[]
        for step in (self.pipeline or {'steps':[]})['steps']:
            started=[e for e in self._events if e['type']=='step.started' and e['payload']['step_id']==step['step_id']]
            completed=[e for e in self._events if e['type']=='step.completed' and e['payload']['step_id']==step['step_id']]
            failures=[e for e in self._events if e['type']=='step.failed' and e['payload']['step_id']==step['step_id']]
            result.append({'definition':deepcopy(step),'started':deepcopy(started[-1]) if started else None,'completed':deepcopy(completed[-1]) if completed else None,'failure':deepcopy(failures[-1]) if failures else None,'superseded':step['step_id'] in superseded})
        return result

    def document(self,identity):return self._store.get('documents',identity)
    def material(self,identity):return self._store.get('materials',identity)


def resolve(view,reference):
    return resolve_reference(view,reference,view._catalog)

"""Public capability boundary. Implementations do not import engine or assurance."""
from copy import deepcopy
from dataclasses import dataclass, field
from .errors import ToolkitError, CapabilityError, Problem
from .ids import document_id, material_id, file_sha256, event_hash, GENESIS
from .canonical import dumps, loads
from .schemas import require as require_schema
from .material import normalize as normalize_material
from .ports import Invoker, View
from .references import resolve as resolve_reference
from .verdict import make
from .release import core_version


@dataclass
class Outcome:
    products: dict=field(default_factory=dict)
    documents: dict=field(default_factory=dict)
    artifacts: dict=field(default_factory=dict)
    values: dict=field(default_factory=dict)
    verdicts: list=field(default_factory=list)
    unverified: list=field(default_factory=list)


def capability(declaration):
    """Attach exportable metadata; discovery reads generated JSON, never this code."""
    def decorate(function):
        function.declaration=deepcopy(declaration)
        return function
    return decorate


__all__=['ToolkitError','CapabilityError','Problem','Outcome','Invoker','View','make',
         'document_id','material_id','file_sha256','event_hash','GENESIS','dumps','loads','require_schema',
         'normalize_material','core_version','capability','resolve_reference']

"""Read-only surface for record projections."""
from pathlib import Path
from .chain import read as read_chain
from .store import Store
from dna_design_core.kernel import canonical


def events(root):
    root=Path(root)
    return read_chain(root/('journal-until-seal.ndjson' if (root/'manifest.json').exists() else 'journal.ndjson'))


def document(root,identity):return Store(root).get('documents',identity)


def material(root,identity):return Store(root).get('materials',identity)


def json_document(path):return canonical.loads(Path(path).read_bytes())

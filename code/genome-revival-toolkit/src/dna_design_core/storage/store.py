"""Content-addressed JSON and raw bytes; existing objects are never replaced."""
from pathlib import Path
import re
from dna_design_core.kernel import canonical, ids, material
from dna_design_core.kernel.errors import ToolkitError


class Store:
    def __init__(self,root):self.root=Path(root)/'store'

    def path(self,kind,identity):
        if kind not in {'materials','documents','artifacts'} or not re.fullmatch('[0-9a-f]{64}',identity):
            raise ToolkitError('STORE_CORRUPT','Invalid content reference.')
        return self.root/kind/(identity+('' if kind=='artifacts' else '.json'))

    def put_file(self,value):
        identity=ids.file_sha256(value);path=self.path('artifacts',identity)
        path.parent.mkdir(parents=True,exist_ok=True)
        if path.exists():self.get_file(identity);return identity
        try:
            with path.open('xb') as stream:stream.write(value)
        except FileExistsError:self.get_file(identity)
        return identity

    def get_file(self,identity):
        try:value=self.path('artifacts',identity).read_bytes()
        except OSError as error:raise ToolkitError('STORE_CORRUPT','Stored file cannot be read.',{'id':identity}) from error
        if ids.file_sha256(value)!=identity:raise ToolkitError('STORE_CORRUPT','Stored file identity differs.',{'id':identity})
        return value

    def put(self,kind,value):
        value=material.normalize(value) if kind=='materials' else value
        identity=ids.material_id(value) if kind=='materials' else ids.document_id(value)
        path=self.path(kind,identity);path.parent.mkdir(parents=True,exist_ok=True)
        if path.exists():self.get(kind,identity);return identity
        try:
            with path.open('xb') as stream:stream.write(canonical.dumps(value))
        except FileExistsError:self.get(kind,identity)
        return identity

    def get(self,kind,identity):
        path=self.path(kind,identity)
        try:
            value=canonical.loads(path.read_bytes())
            actual=ids.material_id(value) if kind=='materials' else ids.document_id(value)
        except (OSError,ToolkitError) as error:
            raise ToolkitError('STORE_CORRUPT','Stored object cannot be read.',{'id':identity}) from error
        if actual!=identity:raise ToolkitError('STORE_CORRUPT','Stored object identity differs.',{'expected':identity,'actual':actual})
        return value

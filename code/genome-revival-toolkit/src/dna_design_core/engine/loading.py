"""Implementation loading shared by execution and contract/export probes."""
import importlib
import importlib.util
from pathlib import Path
import sys
import types
from dna_design_core.kernel import ids
from dna_design_core.kernel.errors import ToolkitError


class Loader:
    def __init__(self):self._modules={}

    def load(self,entry):
        if ids.file_sha256(entry['path'].read_bytes())!=entry['code_digest']:
            raise ToolkitError('CAPABILITY_VERSION_MISMATCH','Implementation content changed.')
        key=(entry['module'],str(entry['root']),entry['code_digest'])
        if key not in self._modules:
            if entry['root'] is None:module=importlib.import_module(entry['module'])
            else:
                root=Path(entry['root']).resolve();namespace='_grt_'+ids.document_id({'root':str(root),'code':entry['code_digest']})[:16]
                parts=entry['module'].split('.')[1:]
                for depth in range(len(parts)):
                    name='.'.join([namespace]+parts[:depth]);folder=root.joinpath(*parts[:depth])
                    if name not in sys.modules:
                        package=types.ModuleType(name);package.__path__=[str(folder)];sys.modules[name]=package
                name='.'.join([namespace]+parts);spec=importlib.util.spec_from_file_location(name,entry['path'])
                module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
            self._modules[key]=module
        return getattr(self._modules[key],entry['function'])

"""Metadata-only host descriptions and local dependency guidance."""
from importlib import metadata
import platform
from pathlib import Path


def doctor():
    packages={}
    package=Path(__file__).resolve().parents[1]
    lock=package/'requirements.lock' if (package/'requirements.lock').is_file() else Path(__file__).resolve().parents[3]/'requirements.lock'
    for name,required in (line.split('==') for line in lock.read_text(encoding='utf-8').splitlines() if line.strip()):
        try:installed=metadata.version(name)
        except metadata.PackageNotFoundError:installed=None
        packages[name]={'installed':installed,'required':required,'available':installed==required}
    return {'python':platform.python_version(),'packages':packages,
            'guidance':'Use the project development environment with requirements.lock. This command does not install software.',
            'external_tools':'S1 examples require no external scientific program.'}


def describe(catalog,kind,name=None):
    return {'description':catalog.describe(kind,name),'kit_diagnostics':catalog.problems,'notices':catalog.notices,
            'unavailable':[{'id':key,'reason':'A declared local runtime dependency is unavailable.','requires_runtime':entry['declaration']['requires_runtime']}
                           for key,entry in catalog.entries.items() if not catalog.available(key)]}

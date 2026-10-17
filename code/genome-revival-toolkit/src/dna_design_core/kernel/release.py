"""One version source and the installed, hash-checked D16 release identity."""
import base64
from functools import lru_cache
from importlib import metadata
import json
from pathlib import Path
from . import canonical, ids
from .errors import ToolkitError
from .vocab import RESOURCES


def versions():
    bundled=RESOURCES/'VERSIONS.json'
    source=Path(__file__).resolve().parents[3]/'VERSIONS.json'
    return json.loads((bundled if bundled.exists() else source).read_text(encoding='utf-8'))


def core_version():
    return versions()['core']


@lru_cache(maxsize=1)
def release_id():
    """Check the installed payload once per process; absent development metadata is explicit."""
    package = Path(__file__).resolve().parents[1]
    source = Path(__file__).resolve().parents[3]
    if (source / 'pyproject.toml').is_file() and (source / 'src/dna_design_core').resolve() == package:
        # Building a source tree may leave .egg-info visible to importlib.metadata.
        # That does not turn the source modules into an installed wheel.
        return 'dev-tree'
    try:
        distribution = metadata.distribution('genome-revival-toolkit')
    except metadata.PackageNotFoundError:
        return 'dev-tree'
    if Path(distribution.locate_file('dna_design_core')).resolve() != package:
        return 'dev-tree'
    try:
        manifest_path = package / 'release-manifest.json'
        data = manifest_path.read_bytes()
        record = next(row for row in distribution.files or []
                      if str(row).replace('\\', '/') == 'dna_design_core/release-manifest.json')
        actual = base64.urlsafe_b64encode(bytes.fromhex(ids.file_sha256(data))).decode().rstrip('=')
        if record.hash is None or record.hash.mode != 'sha256' or record.hash.value != actual:
            raise ValueError('Installed release manifest differs from its wheel RECORD.')
        manifest = canonical.loads(data)
        if canonical.dumps(manifest) != data:
            raise ValueError('Installed release manifest is not canonical JSON.')
        for row in manifest['files']:
            # The source manifest paths are preserved across ZIP -> wheel installation.
            name = row['path'].removeprefix('src/dna_design_core/')
            path = package / name
            if not path.resolve().is_relative_to(package):
                raise ValueError('Installed release manifest contains a nonlocal file.')
            content = path.read_bytes()
            if len(content) != row['bytes'] or ids.file_sha256(content) != row['sha256']:
                raise ValueError('Installed release file differs: ' + row['path'])
        return ids.file_sha256(data)
    except (OSError, ValueError, KeyError, TypeError, StopIteration) as error:
        raise ToolkitError('SOURCE_CHANGED', 'Installed release manifest validation failed: ' + str(error),
                           recovery='Reinstall the unchanged wheel and retry; no development-tree fallback was used.') from error

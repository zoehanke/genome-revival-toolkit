"""Kit discovery reads metadata and files, never imports executable modules."""
from pathlib import Path
from dna_design_core.kernel import canonical, ids, schemas
from dna_design_core.kernel.errors import ToolkitError
from dna_design_core.kernel.release import core_version


def version_key(value):
    main,_,prerelease=value.split('+',1)[0].partition('-')
    return (*map(int,main.split('.')),not bool(prerelease),tuple((0,int(x)) if x.isdigit() else (1,x) for x in prerelease.split('.')) if prerelease else ())


def read(root):
    root=Path(root).resolve()
    try:manifest=canonical.loads((root/'kit.json').read_bytes())
    except (OSError,ToolkitError) as error:raise ToolkitError('KIT_MANIFEST_INVALID') from error
    schemas.require('kit-v1',manifest,'KIT_MANIFEST_INVALID')
    bounds=manifest['requires_core'];version=version_key(core_version())
    if not version_key(bounds['minimum'])<=version<version_key(bounds['maximum_exclusive']):
        raise ToolkitError('KIT_CORE_INCOMPATIBLE')
    for paths in manifest['contributes'].values():
        for path in paths:
            target=(root/path).resolve()
            if not target.is_relative_to(root) or not target.is_file():
                raise ToolkitError('KIT_MANIFEST_INVALID','Declared contribution is missing or outside Kit.')
    return manifest


def code_path(declaration,root=None):
    module,separator,function=declaration['source']['implemented_in'].partition(':')
    if not separator:raise ToolkitError('KIT_MANIFEST_INVALID','Implementation must use module:function.')
    parts=module.split('.')
    base=Path(__file__).resolve().parents[2] if root is None else Path(root)
    parts=parts if root is None else parts[1:]
    path=base.joinpath(*parts).with_suffix('.py')
    if not path.exists():path=base.joinpath(*parts)/'__init__.py'
    if not path.is_file() or not path.resolve().is_relative_to(base.resolve()):
        raise ToolkitError('KIT_MANIFEST_INVALID','Implementation file is missing.')
    return path,module,function

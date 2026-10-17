"""The only reader of configuration files and environment variables."""
import os
from pathlib import Path
import shutil
from dna_design_core.kernel import canonical, schemas
from dna_design_core.kernel.errors import ToolkitError


def load(path=None,overrides=None):
    values={'lang':'en','external_timeout_s':300}
    selected=Path(path) if path else Path.cwd()/'grt.config.json'
    if selected.exists():values.update(canonical.loads(selected.read_bytes()))
    elif path:raise ToolkitError('PLAN_PARAM_INVALID','Configuration file does not exist.')
    for variable,key in [('GRT_PRIMER3_CORE','primer3_core'),('GRT_LANG','lang'),('GRT_EXTERNAL_TIMEOUT','external_timeout_s')]:
        if variable in os.environ:
            try:values[key]=int(os.environ[variable]) if key=='external_timeout_s' else os.environ[variable]
            except ValueError:raise ToolkitError('PLAN_PARAM_INVALID','External timeout must be an integer.') from None
    if 'primer3_core' not in values:
        found=shutil.which('primer3_core')
        if found:values['primer3_core']=found
    values.update({key:value for key,value in (overrides or {}).items() if value is not None})
    return schemas.require('config-v1',values,'PLAN_PARAM_INVALID')

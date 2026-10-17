"""Canonical JSON and unchanged file-byte exporters; no biological encoding."""
from pathlib import Path
from dna_design_core.kernel.public import Outcome, capability, dumps
from ..declaration import action


@capability(action('format.write_json','Write a canonical UTF-8 JSON document.',
    'dna_design_core.capabilities.builtin.format_json:write_json',
    [{'name':'data','type':'value','required':True,'constraints':{},'description':'JSON content to export.'}],
    [{'name':'file','type':'artifact','output_role':None}],effects=('writes_files',),
    params={'type':'object','properties':{'name':{'type':'string','pattern':'^[a-zA-Z0-9][a-zA-Z0-9._-]*$'}},'required':['name'],'additionalProperties':False}))
def write_json(ctx,data, name: str) -> Outcome:
    path=ctx.workdir/name;path.write_bytes(dumps(data))
    return Outcome(artifacts={'file':path})


@capability(action('format.write_file','Copy an existing artifact without changing its bytes.',
    'dna_design_core.capabilities.builtin.format_json:write_file',
    [{'name':'file','type':'artifact','required':True,'constraints':{},'description':'Existing file bytes to export unchanged.'}],
    [{'name':'file','type':'artifact','output_role':None}],effects=('reads_files','writes_files'),
    params={'type':'object','properties':{'name':{'type':'string','pattern':'^[a-zA-Z0-9][a-zA-Z0-9._-]*$'}},'required':['name'],'additionalProperties':False}))
def write_file(ctx,file: Path,name: str) -> Outcome:
    path=ctx.workdir/name;path.write_bytes(Path(file).read_bytes())
    return Outcome(artifacts={'file':path})

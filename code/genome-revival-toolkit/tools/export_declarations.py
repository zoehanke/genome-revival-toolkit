"""Export Core decorator metadata; development command, never used by discovery."""
import importlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))


def export():
    paths=[]
    for name in ['builtin.checks','builtin.format_json','builtin.seq.reverse_complement','model_agreement',
                 'builtin.format.operations','builtin.seq.operations','builtin.primer.operations','builtin.primer.backend',
                 'builtin.pcr.operations','builtin.restriction.operations','builtin.assembly.operations','builtin.check.biology','builtin.check.goal',
                 'builtin.check.content','builtin.check.preparation']:
        module=importlib.import_module('dna_design_core.capabilities.'+name)
        for item in vars(module).values():
            declaration=getattr(item,'declaration',None)
            if declaration:
                path=ROOT/'src/dna_design_core/resources/capabilities'/(declaration['id']+'.json')
                path.write_text(json.dumps(declaration,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
                paths.append(path)
    return paths


if __name__=='__main__':export()

"""B1: return a DNA-valued document, without asserting a physical molecule."""
from dna_design_core.kernel.public import Outcome,capability
from dna_design_core.biology.public import reverse_complement
from ...declaration import action


@capability(action('seq.reverse_complement','Compute the IUPAC DNA reverse complement as a document.',
    'dna_design_core.capabilities.builtin.seq.reverse_complement:run',
    [{'name':'sequence','type':'value','required':True,'description':'DNA literal, at most 200 bases.',
      'constraints':{'type':'string','minLength':1,'maxLength':200,'pattern':'^[ACGTRYSWKMBDHVNacgtryswkmbdhvn]+$'}}],
    [{'name':'result','type':'document','schema_ref':'urn:grt:schema:goal-v1#/$defs/value','output_role':'analysis'}],
    final_checks=('check.replay','check.lineage','check.dna_value_valid')))
def run(ctx,sequence: str) -> Outcome:
    return Outcome(documents={'result':{'sequence':reverse_complement(sequence)}},
                   unverified=['Computed sequence only; no physical molecule was prepared.'])

"""Mandatory preparation checks use recorded inputs, never candidate construction."""
from dna_design_core.kernel.public import Outcome,capability
from .._biology import declaration
from ...reactions import run
from ...primers import primer_documents,primer_uses
from .content import verdict

REACTION=declaration('check.reaction_chain','Recompute recorded direct/nested reactions before comparing delivered material.',
    __name__,'reaction_chain',[],[],scope='preparation_model',effects=('reads_files',))
REACTION['granularity']='composite'
REACTION['fixtures']={kind:'tests/fixtures/s1c/check.reaction_chain.'+kind+'.json' for kind in ['pass','fail']}
REACTION['source']['algorithm_refs']=['SPEC D7 preparation_model; D8','Existing pcr.simulate, assembly and seq.rotate capability contracts']
REACTION['does_not_establish']=['Laboratory reactions actually occurred.','DpnI removal, phosphorylation, ligation yield, transformation or biological function.',
    'Independence or correctness of the shared simulation algorithms.']


@capability(REACTION)
def reaction_chain(ctx) -> Outcome:
    return run(ctx,'check.reaction_chain')


# PROVISIONAL(C7): existing primer-set-v1 is the planned order, not a vendor receipt.
ORDER=declaration('check.order_table','Compare complete planned-order primer sequences, including tails, with recorded primer uses.',
    __name__,'order_table',[],[],scope='preparation_model',effects=('reads_files',))
ORDER['fixtures']={kind:'tests/fixtures/s1c/check.order_table.'+kind+'.json' for kind in ['pass','fail']}
ORDER['source']['algorithm_refs']=['SPEC D7 order_table','S1c C7: existing primer-set-v1 complete-sequence fields']
ORDER['does_not_establish']=['Primers were ordered, synthesized, purified or delivered by a supplier.',
    'Thermodynamic suitability, efficiency or actual laboratory PCR.']


@capability(ORDER)
def order_table(ctx) -> Outcome:
    documents=primer_documents(ctx.view);differences=[];unknown=[];checked=[]
    if not documents:
        return verdict(ctx,'check.order_table','NOT_APPLICABLE','No marked primer output document exists.',{'checked':[],'differences':[]},scope='preparation_model')
    for item in documents:
        if item.get('invalid'):unknown.append({'parent':item['parent'],'reason':item['invalid']});continue
        rows=item['document']['primers'];uses=primer_uses(ctx.view,item['parent'])
        if not uses:
            unknown.append({'parent':item['parent'],'reason':'No independently recorded complete primer use is available.'});continue
        actual={row['material']['sequence'] for row in uses};declared=set();ids=set()
        for primer in rows:
            if not isinstance(primer,dict) or not isinstance(primer.get('id'),str) or not isinstance(primer.get('sequence'),str):
                differences.append({'parent':item['parent'],'fields':['order_row_shape']});continue
            name=primer['id'];sequence=primer['sequence'].upper();declared.add(sequence)
            if name in ids:differences.append({'parent':item['parent'],'primer_id':name,'fields':['duplicate_primer_id']})
            ids.add(name)
            matches=sequence in actual
            checked.append({'parent':item['parent'],'document_id':item['document_id'],'primer_id':name,'full_length':len(sequence),'matches_recorded_use':matches})
            if not matches:differences.append({'parent':item['parent'],'primer_id':name,'fields':['full_sequence']})
        if actual-declared:differences.append({'parent':item['parent'],'fields':['missing_used_primers']})
    return verdict(ctx,'check.order_table','FAIL' if differences else 'UNKNOWN' if unknown else 'PASS',
        'Full planned-order sequences compared with actual recorded oligos.',{'checked':checked,'differences':differences,'not_checked':unknown},scope='preparation_model')

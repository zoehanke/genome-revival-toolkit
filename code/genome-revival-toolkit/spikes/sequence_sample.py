# ported-from: snapgene-dna-design/scripts/design_guides.py@750bf4849b818be00f28684513ef19c01d901bcb
"""Linear ACGT-only algorithm sample, not a complete guide design capability."""
from Bio.Seq import Seq

IUPAC={'A':'A','C':'C','G':'G','T':'T','N':'ACGT','V':'ACG','B':'CGT','D':'AGT','H':'ACT','W':'AT','S':'CG','M':'AC','K':'GT','R':'AG','Y':'CT'}


def reverse_complement(sequence: str) -> str:
    sequence=sequence.upper()
    if any(base not in 'ACGT' for base in sequence): raise ValueError('Sample accepts unambiguous DNA only')
    return str(Seq(sequence).reverse_complement())


def scan_linear_pam(sequence: str, pattern: str, spacer_length: int) -> list[dict]:
    dna=sequence.upper(); pattern=pattern.upper()
    if any(base not in 'ACGT' for base in dna): raise ValueError('Sample accepts unambiguous DNA only')
    if not pattern or any(base not in IUPAC for base in pattern): raise ValueError('Unknown PAM pattern')
    if spacer_length<1: raise ValueError('Positive spacer length required')
    size=len(dna); width=len(pattern); hits=[]
    for strand,scan in ((1,dna),(-1,reverse_complement(dna))):
        for anchor in range(spacer_length,size-width+1):
            pam=scan[anchor:anchor+width]
            if not all(base in IUPAC[code] for base,code in zip(pam,pattern)): continue
            start=anchor-spacer_length; end=anchor
            if strand==1: reference=(start,end,anchor,anchor+width)
            else: reference=(size-end,size-start,size-anchor-width,size-anchor)
            hits.append({'strand':strand,'start':reference[0],'end':reference[1],'pam_start':reference[2],'pam_end':reference[3],'spacer':scan[start:end],'pam':pam})
    return hits

# ported-from: snapgene-dna-design/scripts/validation_crosscheck.py@750bf4849b818be00f28684513ef19c01d901bcb
"""Pure NN Tm sample with explicit parameters, not a primer quality decision."""
from Bio.SeqUtils import MeltingTemp


def tm_nn(sequence: str, *, sodium_mm: float, primer_nm: float) -> float:
    sequence=sequence.upper()
    if len(sequence)<2 or any(base not in 'ACGT' for base in sequence):
        raise ValueError('Sample requires at least two unambiguous bases')
    if sodium_mm<=0 or primer_nm<=0: raise ValueError('Positive concentration required')
    return MeltingTemp.Tm_NN(sequence,nn_table=MeltingTemp.DNA_NN3,
        dnac1=primer_nm,dnac2=0,Na=sodium_mm,K=0,Tris=0,Mg=0,dNTPs=0,
        saltcorr=5,selfcomp=False)

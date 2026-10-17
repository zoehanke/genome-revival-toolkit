# ported-from: snapgene-dna-design/core/tools/amplification.py@750bf4849b818be00f28684513ef19c01d901bcb
"""Nearest-neighbor Tm with explicit, serializable thermodynamic assumptions."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation

from Bio.Seq import Seq
from Bio.SeqUtils.MeltingTemp import DNA_NN3, Tm_NN

from ..sequence.operations import normalize_dna


@dataclass(frozen=True)
class TmParameters:
    """Concentrations in mM, except total strand concentration in nM.

    For a non-self-complementary duplex, dnac1=dnac2=total/2, giving
    effective concentration total/4. Self-complementarity uses total and
    the table's symmetry entropy correction. Salt method 5 is explicit.
    """
    sodium_mM: str = "50"
    magnesium_mM: str = "0"
    dntp_mM: str = "0"
    total_oligo_nM: str = "50"

    def concentrations(self) -> dict[str, float]:
        values = {}
        for key, text in asdict(self).items():
            if not isinstance(text, str):
                raise TypeError("concentrations must be decimal strings")
            try:
                value = Decimal(text)
            except InvalidOperation as exc:
                raise ValueError("invalid decimal concentration") from exc
            if not value.is_finite() or value < 0:
                raise ValueError("concentrations must be finite and nonnegative")
            values[key] = float(value)
        if values["sodium_mM"] <= 0 or values["total_oligo_nM"] <= 0:
            raise ValueError("positive sodium and total oligo concentrations required")
        return values


def calculate_tm(sequence: str, parameters: TmParameters = TmParameters()) -> dict:
    """Perfect-match DNA/DNA NN Tm; table DNA_NN3, salt correction method 5.

    DNA_NN3 is Allawi/SantaLucia 1997, not the DNA_NN4 2004 table. No mismatches,
    dangling ends, cosolvents or laboratory reaction efficiency are predicted.
    """
    sequence = normalize_dna(sequence)
    if len(sequence) < 2:
        raise ValueError("nearest-neighbor Tm requires at least two bases")
    values = parameters.concentrations()
    self_complementary = sequence == str(Seq(sequence).reverse_complement())
    strand_concentration = values["total_oligo_nM"] / (1 if self_complementary else 2)
    tm = Tm_NN(
        sequence, nn_table=DNA_NN3, check=False, strict=True,
        dnac1=strand_concentration, dnac2=strand_concentration,
        selfcomp=self_complementary, Na=values["sodium_mM"],
        Mg=values["magnesium_mM"], dNTPs=values["dntp_mM"], saltcorr=5,
    )
    return {
        "tm": format(tm, ".8f"), "unit": "degC", "length": len(sequence),
        "parameters": {
            **asdict(parameters), "nn_table": "DNA_NN3",
            "salt_correction_method": 5, "self_complementary": self_complementary,
            "dnac1_nM": format(strand_concentration, ".12g"),
            "dnac2_nM": format(strand_concentration, ".12g"),
            "gas_constant_cal_per_K_mol": "1.987",
        },
    }


def calculate_tm_explicit(sequence: str, parameters: dict) -> dict:
    """DNA_NN3/method-5 calculation with both strand concentrations supplied.

    No conversion from a total-strand convention and no implicit salt defaults.
    Only the currently declared NN table/correction is supported.
    """
    if parameters['nn_table'] != 'DNA_NN3' or parameters['saltcorr'] != 5 or type(parameters['selfcomp']) is not bool:
        raise ValueError('Unsupported explicit NN method')
    sequence = normalize_dna(sequence)
    if len(sequence) < 2 or set(sequence) - set('ACGT'):
        raise ValueError('Perfect-match NN calculation requires concrete DNA')
    numeric = {}
    for key in ('dnac1_nM','dnac2_nM','Na_mM','K_mM','Tris_mM','Mg_mM','dNTPs_mM'):
        value = Decimal(parameters[key])
        if not value.is_finite() or value < 0:
            raise ValueError('Concentrations must be finite and nonnegative')
        numeric[key] = float(value)
    if numeric['dnac1_nM'] <= numeric['dnac2_nM'] / 2 or not any(numeric[key] for key in ('Na_mM','K_mM','Tris_mM','Mg_mM')):
        raise ValueError('Positive effective strand concentration and salt required')
    tm = Tm_NN(sequence, nn_table=DNA_NN3, check=False, strict=True,
               dnac1=numeric['dnac1_nM'], dnac2=numeric['dnac2_nM'],
               Na=numeric['Na_mM'], K=numeric['K_mM'], Tris=numeric['Tris_mM'],
               Mg=numeric['Mg_mM'], dNTPs=numeric['dNTPs_mM'],
               saltcorr=parameters['saltcorr'], selfcomp=parameters['selfcomp'])
    return {'tm':str(tm),'unit':'degC','parameters':dict(parameters)}

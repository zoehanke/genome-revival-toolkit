# ported-from: snapgene-dna-design/core/tools/amplification.py@750bf4849b818be00f28684513ef19c01d901bcb
# ported-from: snapgene-dna-design/core/tools/primer3_backend.py@750bf4849b818be00f28684513ef19c01d901bcb
# ported-from: snapgene-dna-design/scripts/primer_qc.py@750bf4849b818be00f28684513ef19c01d901bcb
"""Exact complementarity metrics, not thermodynamic structure predictions."""
from __future__ import annotations

from itertools import groupby

from Bio.Seq import Seq

from ..sequence.operations import normalize_dna


def dimer_metrics(first: str, second: str) -> dict[str, int]:
    """Longest contiguous antiparallel match, including either 3-prime terminus."""
    first = normalize_dna(first)
    second = normalize_dna(second)
    reversed_second = str(Seq(second).reverse_complement())
    maximum = terminal = 0
    for shift in range(1 - len(second), len(first)):
        run = 0
        run_touches_second_3prime = False
        for index, base in enumerate(first):
            other = index - shift
            if 0 <= other < len(second) and base == reversed_second[other]:
                run += 1
                if other == 0:
                    run_touches_second_3prime = True
                maximum = max(maximum, run)
                if index == len(first) - 1 or run_touches_second_3prime:
                    terminal = max(terminal, run)
            else:
                run = 0
                run_touches_second_3prime = False
    return {"max_contiguous_bp": maximum, "max_3prime_bp": terminal}


def hairpin_metrics(sequence: str, *, min_loop: int = 3) -> dict[str, int]:
    """Longest exact ungapped intramolecular stem with a declared minimum loop."""
    sequence = normalize_dna(sequence)
    if type(min_loop) is not int or min_loop < 0:
        raise ValueError("minimum hairpin loop must be a nonnegative integer")
    complement = str(Seq(sequence).complement())
    maximum = terminal = 0
    for left in range(len(sequence)):
        for right in range(left + min_loop + 1, len(sequence)):
            stem = 0
            while right - left - 2 * stem - 1 >= min_loop:
                if sequence[left + stem] != complement[right - stem]:
                    break
                stem += 1
                maximum = max(maximum, stem)
                if right == len(sequence) - 1:
                    terminal = max(terminal, stem)
    return {"max_stem_bp": maximum, "max_3prime_stem_bp": terminal, "min_loop_nt": min_loop}


def primer_quality(sequence: str, *, partner: str | None = None, min_loop: int = 3) -> dict:
    """Report full-oligo GC, runs and structural metrics without hidden thresholds."""
    sequence = normalize_dna(sequence)
    runs = [(base, sum(1 for _ in values)) for base, values in groupby(sequence)]
    return {
        "length": len(sequence),
        "gc_percent": format(100 * (sequence.count("G") + sequence.count("C")) / len(sequence), ".8f"),
        "longest_run_nt": max(length for _, length in runs),
        "longest_T_run_nt": max((length for base, length in runs if base == "T"), default=0),
        "gc_in_last_5nt": sum(base in "GC" for base in sequence[-5:]),
        "homodimer": dimer_metrics(sequence, sequence),
        "heterodimer": None if partner is None else dimer_metrics(sequence, partner),
        "hairpin": hairpin_metrics(sequence, min_loop=min_loop),
        "method": "exact_ungapped_complementarity",
    }


def evaluate_primer_quality(metrics: dict, limits: dict) -> dict:
    """Apply caller-supplied limits; no literature-free hardcoded quality rules.

    limits must specify length_min/max, gc_min/max (decimal strings),
    max_T_run, max_3prime_dimer and max_hairpin_stem. This is a domain result,
    never a kernel verdict. A CHECK adapter must use kernel.verdict.make.
    """
    from decimal import Decimal, InvalidOperation

    required = {
        "length_min", "length_max", "gc_min", "gc_max", "max_T_run",
        "max_3prime_dimer", "max_hairpin_stem",
    }
    if set(limits) != required:
        raise ValueError("quality limits must explicitly specify the supported parameters")
    for key in required - {"gc_min", "gc_max"}:
        if type(limits[key]) is not int or limits[key] < 0:
            raise ValueError("quality count limits must be nonnegative integers")
    if not isinstance(limits["gc_min"], str) or not isinstance(limits["gc_max"], str):
        raise TypeError("GC limits must be decimal strings")
    try:
        gc_min, gc_max = Decimal(limits["gc_min"]), Decimal(limits["gc_max"])
    except InvalidOperation as error:
        raise ValueError("GC limits must be decimal strings") from error
    if not gc_min.is_finite() or not gc_max.is_finite() or not 0 <= gc_min <= gc_max <= 100:
        raise ValueError("GC limits must be ordered between 0 and 100")
    if limits["length_min"] > limits["length_max"]:
        raise ValueError("length limits must be ordered")
    checks = {
        "length": limits["length_min"] <= metrics["length"] <= limits["length_max"],
        "gc": gc_min <= Decimal(metrics["gc_percent"]) <= gc_max,
        "poly_T": metrics["longest_T_run_nt"] <= limits["max_T_run"],
        "homodimer": metrics["homodimer"]["max_3prime_bp"] <= limits["max_3prime_dimer"],
        "hairpin": metrics["hairpin"]["max_stem_bp"] <= limits["max_hairpin_stem"],
    }
    if metrics["heterodimer"] is not None:
        checks["heterodimer"] = metrics["heterodimer"]["max_3prime_bp"] <= limits["max_3prime_dimer"]
    return {"violations": [name for name, satisfied in checks.items() if not satisfied],
            "checks": checks, "limits": dict(limits)}

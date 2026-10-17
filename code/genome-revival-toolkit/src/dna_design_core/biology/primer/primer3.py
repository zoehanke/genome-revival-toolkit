# ported-from: snapgene-dna-design/core/tools/primer3_backend.py@750bf4849b818be00f28684513ef19c01d901bcb
"""Pure Boulder-IO codec. Process launch belongs to the injected runtime.

No discovery, environment access, installation, hashing or subprocess launch.
The process adapter lives in capabilities/builtin/primer/backend.py and uses
ctx.run_external; these codecs retain no process or configuration state.
"""
from __future__ import annotations

import re

from ..sequence.operations import normalize_dna
from .thermodynamics import TmParameters


def encode_boulder(tags: dict[str, str | int]) -> str:
    """Encode exactly one record, rejecting newlines and invalid tag names."""
    if not tags:
        raise ValueError("Boulder record cannot be empty")
    lines = []
    for key, value in tags.items():
        if not isinstance(key, str) or not re.fullmatch(r"[A-Z][A-Z0-9_]*", key):
            raise ValueError("invalid Boulder tag")
        if type(value) not in (str, int) or any(char in str(value) for char in "\r\n"):
            raise ValueError("Boulder values must be single-line strings or integers")
        lines.append(f"{key}={value}")
    return "\n".join([*lines, "=", ""])


def parse_boulder(text: str) -> dict[str, str]:
    """Parse one record, retaining Primer3's multiline *_STUCT alignment output."""
    if not isinstance(text, str):
        raise TypeError("Boulder input must be text")
    result = {}
    terminated = False
    previous_key = ""
    for line in text.splitlines():
        if not line:
            continue
        if terminated:
            raise ValueError("only one Boulder record is supported")
        if line == "=":
            terminated = True
            continue
        key, separator, value = line.partition("=")
        if not separator and previous_key.endswith("_STUCT") and line.startswith(("SEQ\t", "STR\t")):
            result[previous_key] += "\n" + line
            continue
        if not separator or not re.fullmatch(r"[A-Z][A-Z0-9_]*", key) or key in result:
            raise ValueError("malformed or duplicate Boulder tag")
        result[key] = value
        previous_key = key
    if not terminated or not result:
        raise ValueError("Boulder record must be nonempty and terminated by =")
    return result


def primer3_check_request(
    forward: str, *, reverse: str | None = None,
    parameters: TmParameters = TmParameters(), thermodynamic_path: str,
) -> str:
    """Check complete supplied oligos, including their entire 5-prime tails.

    Backend size limit is exposed: 2..36 nt here. Longer oligos are refused,
    never truncated. Parameters match calculate_tm's total-strand convention.
    """
    forward = normalize_dna(forward)
    reverse = None if reverse is None else normalize_dna(reverse)
    lengths = [len(forward)] + ([] if reverse is None else [len(reverse)])
    if min(lengths) < 2 or max(lengths) > 36:
        raise ValueError("this Primer3 request supports complete oligos of 2..36 nt")
    parameters.concentrations()
    if not isinstance(thermodynamic_path, str) or not thermodynamic_path:
        raise ValueError("explicit Primer3 thermodynamic data path required")
    tags = {
        "SEQUENCE_ID": "synthetic_oligo_check", "PRIMER_TASK": "check_primers",
        "PRIMER_PICK_ANYWAY": 1, "SEQUENCE_PRIMER": forward,
        "PRIMER_PICK_LEFT_PRIMER": 1, "PRIMER_PICK_RIGHT_PRIMER": int(reverse is not None),
        "PRIMER_MIN_SIZE": min(lengths), "PRIMER_OPT_SIZE": len(forward),
        "PRIMER_MAX_SIZE": max(lengths), "PRIMER_TM_FORMULA": 1,
        "PRIMER_SALT_CORRECTIONS": 1,
        "PRIMER_SALT_MONOVALENT": parameters.sodium_mM,
        "PRIMER_SALT_DIVALENT": parameters.magnesium_mM,
        "PRIMER_DNTP_CONC": parameters.dntp_mM,
        "PRIMER_DNA_CONC": parameters.total_oligo_nM,
        "PRIMER_THERMODYNAMIC_OLIGO_ALIGNMENT": 1,
        "PRIMER_SECONDARY_STRUCTURE_ALIGNMENT": 1,
        "PRIMER_THERMODYNAMIC_PARAMETERS_PATH": thermodynamic_path,
        "PRIMER_EXPLAIN_FLAG": 1,
    }
    if reverse is not None:
        tags["SEQUENCE_PRIMER_REVCOMP"] = reverse
    return encode_boulder(tags)

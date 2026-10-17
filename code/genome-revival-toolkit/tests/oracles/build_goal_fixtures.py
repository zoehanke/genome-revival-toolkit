"""D2 independent literal constructions; no constraint implementation is imported."""
import json
from pathlib import Path

from dna_design_core.kernel.public import material_id

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "tests/fixtures/goal_checks"


def material(sequence, topology="linear", features=None):
    return {"sequence": sequence, "topology": topology, "strandedness": "double", "ends": None, "features": features or []}


def build():
    reference = material("AAACCCGGGTTT")
    regions = [{"source_start": 0, "source_end": 3, "target_start": 0, "target_end": 3},
               {"source_start": 6, "source_end": 12, "target_start": 5, "target_end": 11}]
    fixtures = {
        "topology": ({"topology": "circular"}, material("AAACCC", "circular"), material("AAACCC", "linear"),
                     "Topology is fixed by the synthetic construction: circular versus linear, never by a declaration or filename."),
        "exact_sequence": ({"sequence": "AGTCAGAA"}, material("AGTCAGAA"), material("AGTCAGAT"),
                           "The hand-written last base is A versus T; no rotation equivalence or code-generated answer."),
        "components_present": ({"components": [{"name": "wanted", "sequence": "CCCG"}]}, material("AAACCCGGGTTT"),
                               material("AAAATTTT", features=[{"start": 0, "end": 3, "type": "misc_feature", "label": "wanted", "strand": 1}]),
                               "CCCG occupies [3,7) in the positive. The negative has only A/T but an intentionally misleading annotation."),
        "components_absent": ({"components": [{"name": "forbidden", "sequence": "CCCG"}]}, material("AAAATTTT"), material("AAACCCGGGTTT"),
                              "Only A/T in the positive cannot contain CCCG; the negative contains literal CCCG at [3,7)."),
        "regions_unchanged": ({"reference_material_id": material_id(reference), "regions": regions},
                              material("AAAATGGGTTT"), material("AGAATGGGTTT"),
                              "CCC [3,6) is replaced by AT. AAA maps [0,3) to [0,3), GGGTTT maps [6,12) to [5,11); the negative changes the protected second base."),
        "claim_reported": ({"claim": "functional_revival"},
                           {"claims": [{"claim": "functional_revival", "status": "INSUFFICIENT"}]},
                           {"claims": [{"claim": "functional_revival"}], "notes": "A status named only in free text is insufficient."},
                           "A named structured claim with INSUFFICIENT is reported; the negative deliberately omits its status. No biological success is implied."),
    }
    DEST.mkdir(parents=True, exist_ok=True)
    for name, (params, positive, negative, reason) in fixtures.items():
        for variant, value in (("pass", positive), ("fail", negative)):
            row = {"check": "check.goal." + name, "variant": variant, "expected": "PASS" if variant == "pass" else "FAIL",
                   "params": params, "kind": "artifact" if name == "claim_reported" else "material", "value": value,
                   "oracle": {"kind": "construction", "reason": reason}}
            if name == "regions_unchanged":
                row["reference"] = reference
            (DEST / (name + "." + variant + ".json")).write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return len(fixtures) * 2


if __name__ == "__main__":
    print(json.dumps({"independent_goal_fixtures": build()}))

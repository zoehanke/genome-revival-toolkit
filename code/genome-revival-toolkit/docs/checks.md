# Checks

Generated from exported capability declarations.

## check.annotation_integrity

Validate annotation locations and classify findings against explicit input ancestry.

- Version: 0.0.0
- Effects: reads_files
- Scope: content_model
- Offline: true
- Does not establish: Biological correctness of feature names or strand/function claims.; Experimental function or correct transcription.

```json
{
  "inputs": [],
  "params": {
    "type": "object",
    "properties": {},
    "additionalProperties": false
  },
  "outputs": [],
  "final_checks": []
}
```

## check.assembly_product

Recompute direct and nested digest, ligation, overlap and inverse-PCR products.

- Version: 0.0.0
- Effects: reads_files
- Scope: preparation_model
- Offline: true
- Does not establish: Wet-laboratory success, biological function or reaction efficiency.; Genome-wide safety or thermodynamic structure quality unless explicitly measured.

```json
{
  "inputs": [],
  "params": {
    "type": "object",
    "properties": {},
    "required": [],
    "additionalProperties": false
  },
  "outputs": [],
  "final_checks": []
}
```

## check.biological_sanity

Check nonempty DNA symbols and consistency of declared topology, strands and ends.

- Version: 0.0.0
- Effects: reads_files
- Scope: content_model
- Offline: true
- Does not establish: Experimental viability, function, efficiency or host-specific performance.; Unknown physical properties or ambiguous base identities.; Empirical thresholds not supplied by sourced rule data.

```json
{
  "inputs": [],
  "params": {
    "type": "object",
    "properties": {},
    "additionalProperties": false
  },
  "outputs": [],
  "final_checks": []
}
```

## check.cds_validity

Check annotated coding frames, starts/stops and internal stops with inherited-finding witnesses.

- Version: 0.0.0
- Effects: reads_files
- Scope: content_model
- Offline: true
- Does not establish: Gene expression, protein activity, selectable phenotype or wet-laboratory function.; Complete-CDS start/stop validation of explicitly partial or pseudogene annotations.; Programmed frameshifts, recoding or unannotated strain-specific genetic code differences.

```json
{
  "inputs": [],
  "params": {
    "type": "object",
    "properties": {},
    "additionalProperties": false
  },
  "outputs": [],
  "final_checks": []
}
```

## check.dna_value_valid

Check DNA-valued document outputs against the IUPAC DNA alphabet.

- Version: 0.0.0
- Effects: reads_files
- Scope: content_model
- Offline: true
- Does not establish: Wet-laboratory performance or biological function.

```json
{
  "inputs": [],
  "params": {
    "type": "object",
    "properties": {},
    "additionalProperties": false
  },
  "outputs": [],
  "final_checks": []
}
```

## check.format_roundtrip

Read actual exported DNA files and compare complete kernel material identities.

- Version: 0.0.0
- Effects: reads_files
- Scope: file
- Offline: false
- Does not establish: Wet-laboratory success, biological function or reaction efficiency.; Genome-wide safety or thermodynamic structure quality unless explicitly measured.

```json
{
  "inputs": [],
  "params": {
    "type": "object",
    "properties": {},
    "required": [],
    "additionalProperties": false
  },
  "outputs": [],
  "final_checks": []
}
```

## check.goal.claim_reported

Require a unique explicitly named claim with a nonempty status in target JSON reports.

- Version: 0.0.0
- Effects: reads_files
- Scope: user_goal
- Offline: true
- Does not establish: Experimental performance, functional identity or truth of a reported claim.; Constraint meaning beyond the explicit sequences, coordinates and report topic.

```json
{
  "inputs": [],
  "params": {
    "type": "object",
    "properties": {
      "claim": {
        "type": "string",
        "minLength": 1,
        "pattern": "\\S"
      },
      "pointer": {
        "type": "string",
        "pattern": "^(?:/(?:[^~/]|~[01])*)*$"
      }
    },
    "required": [
      "claim"
    ],
    "additionalProperties": false
  },
  "outputs": [],
  "final_checks": []
}
```

## check.goal.components_absent

Require every explicit component sequence to be absent from every target material.

- Version: 0.0.0
- Effects: reads_files
- Scope: user_goal
- Offline: true
- Does not establish: Experimental performance, functional identity or truth of a reported claim.; Constraint meaning beyond the explicit sequences, coordinates and report topic.

```json
{
  "inputs": [],
  "params": {
    "type": "object",
    "properties": {
      "components": {
        "type": "array",
        "minItems": 1,
        "items": {
          "type": "object",
          "properties": {
            "name": {
              "type": "string",
              "minLength": 1,
              "pattern": "\\S"
            },
            "sequence": {
              "type": "string",
              "minLength": 1,
              "pattern": "^[ACGTacgt]+$"
            },
            "strand": {
              "enum": [
                1,
                -1
              ]
            }
          },
          "required": [
            "name",
            "sequence"
          ],
          "additionalProperties": false
        }
      }
    },
    "required": [
      "components"
    ],
    "additionalProperties": false
  },
  "outputs": [],
  "final_checks": []
}
```

## check.goal.components_present

Require every explicit component sequence in every target material.

- Version: 0.0.0
- Effects: reads_files
- Scope: user_goal
- Offline: true
- Does not establish: Experimental performance, functional identity or truth of a reported claim.; Constraint meaning beyond the explicit sequences, coordinates and report topic.

```json
{
  "inputs": [],
  "params": {
    "type": "object",
    "properties": {
      "components": {
        "type": "array",
        "minItems": 1,
        "items": {
          "type": "object",
          "properties": {
            "name": {
              "type": "string",
              "minLength": 1,
              "pattern": "\\S"
            },
            "sequence": {
              "type": "string",
              "minLength": 1,
              "pattern": "^[ACGTacgt]+$"
            },
            "strand": {
              "enum": [
                1,
                -1
              ]
            }
          },
          "required": [
            "name",
            "sequence"
          ],
          "additionalProperties": false
        }
      }
    },
    "required": [
      "components"
    ],
    "additionalProperties": false
  },
  "outputs": [],
  "final_checks": []
}
```

## check.goal.exact_sequence

Compare complete target sequences literally at their declared origin and orientation.

- Version: 0.0.0
- Effects: reads_files
- Scope: user_goal
- Offline: true
- Does not establish: Experimental performance, functional identity or truth of a reported claim.; Constraint meaning beyond the explicit sequences, coordinates and report topic.

```json
{
  "inputs": [],
  "params": {
    "type": "object",
    "properties": {
      "sequence": {
        "type": "string",
        "minLength": 1,
        "pattern": "^[ACGTRYSWKMBDHVNacgtryswkmbdhvn]+$"
      }
    },
    "required": [
      "sequence"
    ],
    "additionalProperties": false
  },
  "outputs": [],
  "final_checks": []
}
```

## check.goal.nonempty

Require at least one active, computable goal constraint.

- Version: 0.0.0
- Effects: reads_files
- Scope: user_goal
- Offline: true
- Does not establish: Wet-laboratory performance or biological function.

```json
{
  "inputs": [],
  "params": {
    "type": "object",
    "properties": {},
    "additionalProperties": false
  },
  "outputs": [],
  "final_checks": []
}
```

## check.goal.output_present

Check that the constrained target has a retained output.

- Version: 0.0.0
- Effects: reads_files
- Scope: user_goal
- Offline: true
- Does not establish: Wet-laboratory performance or biological function.

```json
{
  "inputs": [],
  "params": {
    "type": "object",
    "properties": {
      "fields": {
        "type": "array",
        "items": {
          "type": "string"
        }
      }
    },
    "additionalProperties": false
  },
  "outputs": [],
  "final_checks": []
}
```

## check.goal.regions_unchanged

Compare explicit nonwrapping reference/target intervals in retained materials.

- Version: 0.0.0
- Effects: reads_files
- Scope: user_goal
- Offline: true
- Does not establish: Experimental performance, functional identity or truth of a reported claim.; Constraint meaning beyond the explicit sequences, coordinates and report topic.

```json
{
  "inputs": [],
  "params": {
    "type": "object",
    "properties": {
      "reference_material_id": {
        "type": "string",
        "pattern": "^[0-9a-f]{64}$"
      },
      "regions": {
        "type": "array",
        "minItems": 1,
        "items": {
          "type": "object",
          "properties": {
            "source_start": {
              "type": "integer",
              "minimum": 0
            },
            "source_end": {
              "type": "integer",
              "minimum": 0
            },
            "target_start": {
              "type": "integer",
              "minimum": 0
            },
            "target_end": {
              "type": "integer",
              "minimum": 0
            },
            "strand": {
              "enum": [
                1,
                -1
              ]
            }
          },
          "required": [
            "source_start",
            "source_end",
            "target_start",
            "target_end"
          ],
          "additionalProperties": false
        }
      }
    },
    "required": [
      "reference_material_id",
      "regions"
    ],
    "additionalProperties": false
  },
  "outputs": [],
  "final_checks": []
}
```

## check.goal.target_role_met

Compare required targets with producer-declared output roles.

- Version: 0.0.0
- Effects: reads_files
- Scope: user_goal
- Offline: true
- Does not establish: Wet-laboratory performance or biological function.

```json
{
  "inputs": [],
  "params": {
    "type": "object",
    "properties": {},
    "additionalProperties": false
  },
  "outputs": [],
  "final_checks": []
}
```

## check.goal.topology

Compare every target material's known topology with the requested topology.

- Version: 0.0.0
- Effects: reads_files
- Scope: user_goal
- Offline: true
- Does not establish: Experimental performance, functional identity or truth of a reported claim.; Constraint meaning beyond the explicit sequences, coordinates and report topic.

```json
{
  "inputs": [],
  "params": {
    "type": "object",
    "properties": {
      "topology": {
        "enum": [
          "linear",
          "circular"
        ]
      }
    },
    "required": [
      "topology"
    ],
    "additionalProperties": false
  },
  "outputs": [],
  "final_checks": []
}
```

## check.inputs_unchanged

Compare input copies with the registered file hashes.

- Version: 0.0.0
- Effects: reads_files
- Scope: file
- Offline: true
- Does not establish: Wet-laboratory performance or biological function.

```json
{
  "inputs": [],
  "params": {
    "type": "object",
    "properties": {},
    "additionalProperties": false
  },
  "outputs": [],
  "final_checks": []
}
```

## check.journal_chain

Validate each recorded event and its hash-chain predecessor.

- Version: 0.0.0
- Effects: reads_files
- Scope: file
- Offline: true
- Does not establish: Wet-laboratory performance or biological function.

```json
{
  "inputs": [],
  "params": {
    "type": "object",
    "properties": {},
    "additionalProperties": false
  },
  "outputs": [],
  "final_checks": []
}
```

## check.lineage

Match explicit input bindings to the recorded content identities.

- Version: 0.0.0
- Effects: reads_files
- Scope: content_model
- Offline: true
- Does not establish: Wet-laboratory performance or biological function.

```json
{
  "inputs": [],
  "params": {
    "type": "object",
    "properties": {},
    "additionalProperties": false
  },
  "outputs": [],
  "final_checks": []
}
```

## check.manifest

Compare the staged file list with actual bytes and files.

- Version: 0.0.0
- Effects: reads_files
- Scope: file
- Offline: true
- Does not establish: Wet-laboratory performance or biological function.

```json
{
  "inputs": [],
  "params": {
    "type": "object",
    "properties": {},
    "additionalProperties": false
  },
  "outputs": [],
  "final_checks": []
}
```

## check.model_agreement

Compare the recorded product with an independently declared model.

- Version: 0.0.0
- Effects: reads_files
- Scope: content_model
- Offline: true
- Does not establish: Wet-laboratory performance or biological function.

```json
{
  "inputs": [],
  "params": {
    "type": "object",
    "properties": {},
    "additionalProperties": false
  },
  "outputs": [],
  "final_checks": []
}
```

## check.order_table

Compare complete planned-order primer sequences, including tails, with recorded primer uses.

- Version: 0.0.0
- Effects: reads_files
- Scope: preparation_model
- Offline: true
- Does not establish: Primers were ordered, synthesized, purified or delivered by a supplier.; Thermodynamic suitability, efficiency or actual laboratory PCR.

```json
{
  "inputs": [],
  "params": {
    "type": "object",
    "properties": {},
    "required": [],
    "additionalProperties": false
  },
  "outputs": [],
  "final_checks": []
}
```

## check.pcr_product

Recompute direct and nested PCR from actual recorded inputs and parameters.

- Version: 0.0.0
- Effects: reads_files
- Scope: preparation_model
- Offline: true
- Does not establish: Wet-laboratory success, biological function or reaction efficiency.; Genome-wide safety or thermodynamic structure quality unless explicitly measured.

```json
{
  "inputs": [],
  "params": {
    "type": "object",
    "properties": {},
    "required": [],
    "additionalProperties": false
  },
  "outputs": [],
  "final_checks": []
}
```

## check.primer_quality

Discover marked preparation primers and assess explicit criteria; retain the explicit-limits API.

- Version: 0.0.0
- Effects: reads_files
- Scope: preparation_model
- Offline: true
- Does not establish: Wet-laboratory success, biological function or reaction efficiency.; Genome-wide safety or thermodynamic structure quality unless explicitly measured.

```json
{
  "inputs": [],
  "params": {
    "type": "object",
    "properties": {
      "material_ids": {
        "type": "array",
        "items": {
          "type": "string",
          "pattern": "^[0-9a-f]{64}$"
        },
        "minItems": 1,
        "maxItems": 2
      },
      "limits": {
        "type": [
          "object",
          "null"
        ],
        "additionalProperties": false,
        "properties": {
          "length_min": {
            "type": "integer",
            "minimum": 0
          },
          "length_max": {
            "type": "integer",
            "minimum": 0
          },
          "max_T_run": {
            "type": "integer",
            "minimum": 0
          },
          "max_3prime_dimer": {
            "type": "integer",
            "minimum": 0
          },
          "max_hairpin_stem": {
            "type": "integer",
            "minimum": 0
          },
          "gc_min": {
            "type": "string"
          },
          "gc_max": {
            "type": "string"
          }
        },
        "required": [
          "length_min",
          "length_max",
          "gc_min",
          "gc_max",
          "max_T_run",
          "max_3prime_dimer",
          "max_hairpin_stem"
        ]
      },
      "min_loop": {
        "type": "integer",
        "minimum": 0
      }
    },
    "required": [],
    "additionalProperties": false
  },
  "outputs": [],
  "final_checks": []
}
```

## check.reaction_chain

Recompute recorded direct/nested reactions before comparing delivered material.

- Version: 0.0.0
- Effects: reads_files
- Scope: preparation_model
- Offline: true
- Does not establish: Laboratory reactions actually occurred.; DpnI removal, phosphorylation, ligation yield, transformation or biological function.; Independence or correctness of the shared simulation algorithms.

```json
{
  "inputs": [],
  "params": {
    "type": "object",
    "properties": {},
    "required": [],
    "additionalProperties": false
  },
  "outputs": [],
  "final_checks": []
}
```

## check.readback

Read exported JSON or compare unchanged artifact byte identities.

- Version: 0.0.0
- Effects: reads_files
- Scope: file
- Offline: true
- Does not establish: Wet-laboratory performance or biological function.

```json
{
  "inputs": [],
  "params": {
    "type": "object",
    "properties": {},
    "additionalProperties": false
  },
  "outputs": [],
  "final_checks": []
}
```

## check.replay

Recompute deterministic steps from their recorded inputs and versions.

- Version: 0.0.0
- Effects: reads_files
- Scope: content_model
- Offline: true
- Does not establish: Wet-laboratory performance or biological function.

```json
{
  "inputs": [],
  "params": {
    "type": "object",
    "properties": {},
    "additionalProperties": false
  },
  "outputs": [],
  "final_checks": []
}
```

## check.store_hashes

Recompute stored document, material and raw artifact identities.

- Version: 0.0.0
- Effects: reads_files
- Scope: file
- Offline: true
- Does not establish: Wet-laboratory performance or biological function.

```json
{
  "inputs": [],
  "params": {
    "type": "object",
    "properties": {},
    "additionalProperties": false
  },
  "outputs": [],
  "final_checks": []
}
```

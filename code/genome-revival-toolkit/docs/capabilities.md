# Capabilities

Generated from exported capability declarations.

## assembly.gibson

Assemble two ordered duplexes using explicit exact overlap lengths.

- Version: 0.0.0
- Effects: pure
- Does not establish: Wet-laboratory success, biological function or reaction efficiency.; Genome-wide safety or thermodynamic structure quality unless explicitly measured.

```json
{
  "inputs": [
    {
      "name": "left",
      "type": "material",
      "required": true,
      "constraints": {},
      "description": "left"
    },
    {
      "name": "right",
      "type": "material",
      "required": true,
      "constraints": {},
      "description": "right"
    }
  ],
  "params": {
    "type": "object",
    "properties": {
      "overlap": {
        "type": "integer",
        "minimum": 1
      },
      "circular": {
        "type": "boolean"
      },
      "closing_overlap": {
        "type": [
          "integer",
          "null"
        ],
        "minimum": 1
      }
    },
    "required": [
      "overlap"
    ],
    "additionalProperties": false
  },
  "outputs": [
    {
      "name": "product",
      "type": "material",
      "output_role": "component"
    }
  ],
  "final_checks": [
    {
      "check": "check.assembly_product"
    }
  ]
}
```

## assembly.inverse_pcr

Simulate circular-template PCR and closure while retaining the linear intermediate.

- Version: 0.0.0
- Effects: pure
- Does not establish: Wet-laboratory success, biological function or reaction efficiency.; Genome-wide safety or thermodynamic structure quality unless explicitly measured.

```json
{
  "inputs": [
    {
      "name": "template",
      "type": "material",
      "required": true,
      "constraints": {},
      "description": "template"
    },
    {
      "name": "forward",
      "type": "material",
      "required": true,
      "constraints": {},
      "description": "forward"
    },
    {
      "name": "reverse",
      "type": "material",
      "required": true,
      "constraints": {},
      "description": "reverse"
    }
  ],
  "params": {
    "type": "object",
    "properties": {
      "forward_core_length": {
        "type": [
          "integer",
          "null"
        ],
        "minimum": 1
      },
      "reverse_core_length": {
        "type": [
          "integer",
          "null"
        ],
        "minimum": 1
      },
      "closing_overlap": {
        "type": "integer",
        "minimum": 0
      }
    },
    "required": [],
    "additionalProperties": false
  },
  "outputs": [
    {
      "name": "product",
      "type": "material",
      "output_role": "construct"
    },
    {
      "name": "intermediate",
      "type": "material",
      "output_role": "component"
    },
    {
      "name": "report",
      "type": "document",
      "output_role": "analysis",
      "schema_ref": "urn:grt:schema:goal-v1#/$defs/value"
    }
  ],
  "final_checks": [
    {
      "check": "check.assembly_product"
    }
  ]
}
```

## assembly.ligate

Ligate one or two explicit linear duplexes after checking actual strand geometry.

- Version: 0.0.0
- Effects: pure
- Does not establish: Wet-laboratory success, biological function or reaction efficiency.; Genome-wide safety or thermodynamic structure quality unless explicitly measured.

```json
{
  "inputs": [
    {
      "name": "left",
      "type": "material",
      "required": true,
      "constraints": {},
      "description": "left"
    },
    {
      "name": "right",
      "type": "material",
      "required": false,
      "constraints": {},
      "description": "right"
    }
  ],
  "params": {
    "type": "object",
    "properties": {
      "circular": {
        "type": "boolean"
      }
    },
    "required": [],
    "additionalProperties": false
  },
  "outputs": [
    {
      "name": "product",
      "type": "material",
      "output_role": "component"
    }
  ],
  "final_checks": [
    {
      "check": "check.assembly_product"
    }
  ]
}
```

## format.read_dna

Read supported native DNA fields through Biopython; no native writer.

- Version: 0.0.0
- Effects: reads_files
- Does not establish: Wet-laboratory success, biological function or reaction efficiency.; Genome-wide safety or thermodynamic structure quality unless explicitly measured.

```json
{
  "inputs": [
    {
      "name": "file",
      "type": "artifact",
      "required": true,
      "constraints": {},
      "description": "file"
    }
  ],
  "params": {
    "type": "object",
    "properties": {
      "topology": {
        "enum": [
          null,
          "linear",
          "circular"
        ]
      },
      "strandedness": {
        "enum": [
          null,
          "single",
          "double"
        ]
      }
    },
    "required": [],
    "additionalProperties": false
  },
  "outputs": [
    {
      "name": "material",
      "type": "material",
      "output_role": "component"
    }
  ],
  "final_checks": []
}
```

## format.read_fasta

Read FASTA DNA; undeclared physical properties remain unknown.

- Version: 0.0.0
- Effects: reads_files
- Does not establish: Wet-laboratory success, biological function or reaction efficiency.; Genome-wide safety or thermodynamic structure quality unless explicitly measured.

```json
{
  "inputs": [
    {
      "name": "file",
      "type": "artifact",
      "required": true,
      "constraints": {},
      "description": "file"
    }
  ],
  "params": {
    "type": "object",
    "properties": {
      "topology": {
        "enum": [
          null,
          "linear",
          "circular"
        ]
      },
      "strandedness": {
        "enum": [
          null,
          "single",
          "double"
        ]
      }
    },
    "required": [],
    "additionalProperties": false
  },
  "outputs": [
    {
      "name": "material",
      "type": "material",
      "output_role": "component"
    }
  ],
  "final_checks": []
}
```

## format.read_genbank

Read GenBank content into a kernel material.

- Version: 0.0.0
- Effects: reads_files
- Does not establish: Wet-laboratory success, biological function or reaction efficiency.; Genome-wide safety or thermodynamic structure quality unless explicitly measured.

```json
{
  "inputs": [
    {
      "name": "file",
      "type": "artifact",
      "required": true,
      "constraints": {},
      "description": "file"
    }
  ],
  "params": {
    "type": "object",
    "properties": {
      "topology": {
        "enum": [
          null,
          "linear",
          "circular"
        ]
      },
      "strandedness": {
        "enum": [
          null,
          "single",
          "double"
        ]
      }
    },
    "required": [],
    "additionalProperties": false
  },
  "outputs": [
    {
      "name": "material",
      "type": "material",
      "output_role": "component"
    }
  ],
  "final_checks": []
}
```

## format.write_fasta

Write the FASTA-representable material subset; refuse silent metadata loss.

- Version: 0.0.0
- Effects: writes_files
- Does not establish: Wet-laboratory success, biological function or reaction efficiency.; Genome-wide safety or thermodynamic structure quality unless explicitly measured.

```json
{
  "inputs": [
    {
      "name": "material",
      "type": "material",
      "required": true,
      "constraints": {},
      "description": "material"
    }
  ],
  "params": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string",
        "pattern": "^[A-Za-z0-9][A-Za-z0-9._-]*$"
      }
    },
    "required": [
      "name"
    ],
    "additionalProperties": false
  },
  "outputs": [
    {
      "name": "file",
      "type": "artifact",
      "output_role": null
    }
  ],
  "final_checks": [
    {
      "check": "check.format_roundtrip"
    }
  ]
}
```

## format.write_file

Copy an existing artifact without changing its bytes.

- Version: 0.0.0
- Effects: reads_files, writes_files
- Does not establish: Wet-laboratory performance or biological function.

```json
{
  "inputs": [
    {
      "name": "file",
      "type": "artifact",
      "required": true,
      "constraints": {},
      "description": "Existing file bytes to export unchanged."
    }
  ],
  "params": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string",
        "pattern": "^[a-zA-Z0-9][a-zA-Z0-9._-]*$"
      }
    },
    "required": [
      "name"
    ],
    "additionalProperties": false
  },
  "outputs": [
    {
      "name": "file",
      "type": "artifact",
      "output_role": null
    }
  ],
  "final_checks": []
}
```

## format.write_genbank

Write GenBank with a visible-content-bound material supplement.

- Version: 0.0.0
- Effects: writes_files
- Does not establish: Wet-laboratory success, biological function or reaction efficiency.; Genome-wide safety or thermodynamic structure quality unless explicitly measured.

```json
{
  "inputs": [
    {
      "name": "material",
      "type": "material",
      "required": true,
      "constraints": {},
      "description": "material"
    }
  ],
  "params": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string",
        "pattern": "^[A-Za-z0-9][A-Za-z0-9._-]*$"
      }
    },
    "required": [
      "name"
    ],
    "additionalProperties": false
  },
  "outputs": [
    {
      "name": "file",
      "type": "artifact",
      "output_role": null
    }
  ],
  "final_checks": [
    {
      "check": "check.format_roundtrip"
    }
  ]
}
```

## format.write_json

Write a canonical UTF-8 JSON document.

- Version: 0.0.0
- Effects: writes_files
- Does not establish: Wet-laboratory performance or biological function.

```json
{
  "inputs": [
    {
      "name": "data",
      "type": "value",
      "required": true,
      "constraints": {},
      "description": "JSON content to export."
    }
  ],
  "params": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string",
        "pattern": "^[a-zA-Z0-9][a-zA-Z0-9._-]*$"
      }
    },
    "required": [
      "name"
    ],
    "additionalProperties": false
  },
  "outputs": [
    {
      "name": "file",
      "type": "artifact",
      "output_role": null
    }
  ],
  "final_checks": []
}
```

## pcr.simulate

Predict one unique annotated PCR product; reject missing or ambiguous products.

- Version: 0.0.0
- Effects: pure
- Does not establish: Wet-laboratory success, biological function or reaction efficiency.; Genome-wide safety or thermodynamic structure quality unless explicitly measured.

```json
{
  "inputs": [
    {
      "name": "template",
      "type": "material",
      "required": true,
      "constraints": {},
      "description": "template"
    },
    {
      "name": "forward",
      "type": "material",
      "required": true,
      "constraints": {},
      "description": "forward"
    },
    {
      "name": "reverse",
      "type": "material",
      "required": true,
      "constraints": {},
      "description": "reverse"
    }
  ],
  "params": {
    "type": "object",
    "properties": {
      "forward_core_length": {
        "type": [
          "integer",
          "null"
        ],
        "minimum": 1
      },
      "reverse_core_length": {
        "type": [
          "integer",
          "null"
        ],
        "minimum": 1
      }
    },
    "required": [],
    "additionalProperties": false
  },
  "outputs": [
    {
      "name": "product",
      "type": "material",
      "output_role": "component"
    },
    {
      "name": "report",
      "type": "document",
      "output_role": "analysis",
      "schema_ref": "urn:grt:schema:goal-v1#/$defs/value"
    }
  ],
  "final_checks": [
    {
      "check": "check.pcr_product"
    }
  ]
}
```

## primer.calculate_tm

Calculate DNA_NN3 nearest-neighbor Tm and emit every concentration parameter.

- Version: 0.0.0
- Effects: pure
- Does not establish: Wet-laboratory success, biological function or reaction efficiency.; Genome-wide safety or thermodynamic structure quality unless explicitly measured.

```json
{
  "inputs": [
    {
      "name": "primer",
      "type": "material",
      "required": true,
      "constraints": {},
      "description": "primer"
    }
  ],
  "params": {
    "type": "object",
    "properties": {
      "sodium_mM": {
        "type": "string",
        "pattern": "^(?:0|[1-9][0-9]*)(?:\\.[0-9]+)?$"
      },
      "magnesium_mM": {
        "type": "string",
        "pattern": "^(?:0|[1-9][0-9]*)(?:\\.[0-9]+)?$"
      },
      "dntp_mM": {
        "type": "string",
        "pattern": "^(?:0|[1-9][0-9]*)(?:\\.[0-9]+)?$"
      },
      "total_oligo_nM": {
        "type": "string",
        "pattern": "^(?:0|[1-9][0-9]*)(?:\\.[0-9]+)?$"
      }
    },
    "required": [],
    "additionalProperties": false
  },
  "outputs": [
    {
      "name": "report",
      "type": "document",
      "output_role": "analysis",
      "schema_ref": "urn:grt:schema:goal-v1#/$defs/value"
    }
  ],
  "final_checks": []
}
```

## primer.enumerate_candidates

Enumerate explicitly bounded primer lengths; retain every exact binding site.

- Version: 0.0.0
- Effects: pure
- Does not establish: Wet-laboratory success, biological function or reaction efficiency.; Genome-wide safety or thermodynamic structure quality unless explicitly measured.

```json
{
  "inputs": [
    {
      "name": "template",
      "type": "material",
      "required": true,
      "constraints": {},
      "description": "template"
    },
    {
      "name": "tail",
      "type": "material",
      "required": false,
      "constraints": {},
      "description": "tail"
    }
  ],
  "params": {
    "type": "object",
    "properties": {
      "anchor": {
        "type": "integer",
        "minimum": 0
      },
      "strand": {
        "enum": [
          -1,
          1
        ]
      },
      "lengths": {
        "type": "array",
        "items": {
          "type": "integer",
          "minimum": 2
        },
        "minItems": 1,
        "uniqueItems": true
      },
      "sodium_mM": {
        "type": "string",
        "pattern": "^(?:0|[1-9][0-9]*)(?:\\.[0-9]+)?$"
      },
      "magnesium_mM": {
        "type": "string",
        "pattern": "^(?:0|[1-9][0-9]*)(?:\\.[0-9]+)?$"
      },
      "dntp_mM": {
        "type": "string",
        "pattern": "^(?:0|[1-9][0-9]*)(?:\\.[0-9]+)?$"
      },
      "total_oligo_nM": {
        "type": "string",
        "pattern": "^(?:0|[1-9][0-9]*)(?:\\.[0-9]+)?$"
      }
    },
    "required": [
      "anchor",
      "strand",
      "lengths"
    ],
    "additionalProperties": false
  },
  "outputs": [
    {
      "name": "report",
      "type": "document",
      "output_role": "analysis",
      "schema_ref": "urn:grt:schema:goal-v1#/$defs/value"
    }
  ],
  "final_checks": []
}
```

## primer.find_binding_sites

Find every exact declared 3-prime core on both strands, including a circular origin.

- Version: 0.0.0
- Effects: pure
- Does not establish: Wet-laboratory success, biological function or reaction efficiency.; Genome-wide safety or thermodynamic structure quality unless explicitly measured.

```json
{
  "inputs": [
    {
      "name": "template",
      "type": "material",
      "required": true,
      "constraints": {},
      "description": "template"
    },
    {
      "name": "primer",
      "type": "material",
      "required": true,
      "constraints": {},
      "description": "primer"
    }
  ],
  "params": {
    "type": "object",
    "properties": {
      "core_length": {
        "type": [
          "integer",
          "null"
        ],
        "minimum": 1
      },
      "strand": {
        "enum": [
          null,
          -1,
          1
        ]
      }
    },
    "required": [],
    "additionalProperties": false
  },
  "outputs": [
    {
      "name": "report",
      "type": "document",
      "output_role": "analysis",
      "schema_ref": "urn:grt:schema:goal-v1#/$defs/value"
    }
  ],
  "final_checks": []
}
```

## primer.inspect_quality

Measure full-oligo GC, T runs and exact ungapped dimer/hairpin metrics.

- Version: 0.0.0
- Effects: pure
- Does not establish: Wet-laboratory success, biological function or reaction efficiency.; Genome-wide safety or thermodynamic structure quality unless explicitly measured.

```json
{
  "inputs": [
    {
      "name": "primer",
      "type": "material",
      "required": true,
      "constraints": {},
      "description": "primer"
    },
    {
      "name": "partner",
      "type": "material",
      "required": false,
      "constraints": {},
      "description": "partner"
    }
  ],
  "params": {
    "type": "object",
    "properties": {
      "min_loop": {
        "type": "integer",
        "minimum": 0
      }
    },
    "required": [],
    "additionalProperties": false
  },
  "outputs": [
    {
      "name": "report",
      "type": "document",
      "output_role": "analysis",
      "schema_ref": "urn:grt:schema:goal-v1#/$defs/value"
    }
  ],
  "final_checks": []
}
```

## primer.run_primer3

Run local Primer3 on complete supplied oligos, recording executable version and hashes.

- Version: 0.0.0
- Effects: reads_files, writes_files, external_process
- Does not establish: Wet-laboratory success, biological function or reaction efficiency.; Genome-wide safety or thermodynamic structure quality unless explicitly measured.

```json
{
  "inputs": [
    {
      "name": "forward",
      "type": "material",
      "required": true,
      "constraints": {},
      "description": "forward"
    },
    {
      "name": "reverse",
      "type": "material",
      "required": false,
      "constraints": {},
      "description": "reverse"
    }
  ],
  "params": {
    "type": "object",
    "properties": {
      "sodium_mM": {
        "type": "string",
        "pattern": "^(?:0|[1-9][0-9]*)(?:\\.[0-9]+)?$"
      },
      "magnesium_mM": {
        "type": "string",
        "pattern": "^(?:0|[1-9][0-9]*)(?:\\.[0-9]+)?$"
      },
      "dntp_mM": {
        "type": "string",
        "pattern": "^(?:0|[1-9][0-9]*)(?:\\.[0-9]+)?$"
      },
      "total_oligo_nM": {
        "type": "string",
        "pattern": "^(?:0|[1-9][0-9]*)(?:\\.[0-9]+)?$"
      }
    },
    "required": [],
    "additionalProperties": false
  },
  "outputs": [
    {
      "name": "report",
      "type": "document",
      "output_role": "analysis",
      "schema_ref": "urn:grt:schema:goal-v1#/$defs/value"
    },
    {
      "name": "request",
      "type": "artifact",
      "output_role": null
    },
    {
      "name": "response",
      "type": "artifact",
      "output_role": null
    }
  ],
  "final_checks": []
}
```

## primer.sequencing_coverage

Project stated usable sequencing distances from unique complete primer sites.

- Version: 0.0.0
- Effects: pure
- Does not establish: Wet-laboratory success, biological function or reaction efficiency.; Genome-wide safety or thermodynamic structure quality unless explicitly measured.

```json
{
  "inputs": [
    {
      "name": "template",
      "type": "material",
      "required": true,
      "constraints": {},
      "description": "template"
    },
    {
      "name": "primers",
      "type": "value",
      "required": true,
      "constraints": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "minItems": 1
      },
      "description": "primers"
    }
  ],
  "params": {
    "type": "object",
    "properties": {
      "read_length": {
        "type": "integer",
        "minimum": 1
      },
      "trim": {
        "type": "integer",
        "minimum": 0
      }
    },
    "required": [
      "read_length",
      "trim"
    ],
    "additionalProperties": false
  },
  "outputs": [
    {
      "name": "report",
      "type": "document",
      "output_role": "analysis",
      "schema_ref": "urn:grt:schema:goal-v1#/$defs/value"
    }
  ],
  "final_checks": []
}
```

## restriction.digest

Produce annotated kernel fragments with actual cohesive end sequences.

- Version: 0.0.0
- Effects: pure
- Does not establish: Wet-laboratory success, biological function or reaction efficiency.; Genome-wide safety or thermodynamic structure quality unless explicitly measured.

```json
{
  "inputs": [
    {
      "name": "material",
      "type": "material",
      "required": true,
      "constraints": {},
      "description": "material"
    }
  ],
  "params": {
    "type": "object",
    "properties": {
      "enzymes": {
        "type": "array",
        "items": {
          "type": "string",
          "minLength": 1
        },
        "minItems": 1,
        "uniqueItems": true
      }
    },
    "required": [
      "enzymes"
    ],
    "additionalProperties": false
  },
  "outputs": [
    {
      "name": "fragments",
      "type": "materials",
      "output_role": "component"
    },
    {
      "name": "report",
      "type": "document",
      "output_role": "analysis",
      "schema_ref": "urn:grt:schema:goal-v1#/$defs/value"
    }
  ],
  "final_checks": [
    {
      "check": "check.assembly_product"
    }
  ]
}
```

## restriction.scan_sites

Scan both recognition orientations and report double-strand cut geometry.

- Version: 0.0.0
- Effects: pure
- Does not establish: Wet-laboratory success, biological function or reaction efficiency.; Genome-wide safety or thermodynamic structure quality unless explicitly measured.

```json
{
  "inputs": [
    {
      "name": "material",
      "type": "material",
      "required": true,
      "constraints": {},
      "description": "material"
    }
  ],
  "params": {
    "type": "object",
    "properties": {
      "enzyme": {
        "type": "string",
        "minLength": 1
      }
    },
    "required": [
      "enzyme"
    ],
    "additionalProperties": false
  },
  "outputs": [
    {
      "name": "report",
      "type": "document",
      "output_role": "analysis",
      "schema_ref": "urn:grt:schema:goal-v1#/$defs/value"
    }
  ],
  "final_checks": []
}
```

## seq.inspect_cds

Report frame, start/stop and ambiguity under an explicit genetic code.

- Version: 0.0.0
- Effects: pure
- Does not establish: Wet-laboratory success, biological function or reaction efficiency.; Genome-wide safety or thermodynamic structure quality unless explicitly measured.

```json
{
  "inputs": [
    {
      "name": "material",
      "type": "material",
      "required": true,
      "constraints": {},
      "description": "material"
    }
  ],
  "params": {
    "type": "object",
    "properties": {
      "translation_table": {
        "type": "integer",
        "minimum": 1
      },
      "codon_start": {
        "enum": [
          1,
          2,
          3
        ]
      },
      "partial": {
        "type": "boolean"
      }
    },
    "required": [
      "translation_table"
    ],
    "additionalProperties": false
  },
  "outputs": [
    {
      "name": "report",
      "type": "document",
      "output_role": "analysis",
      "schema_ref": "urn:grt:schema:goal-v1#/$defs/value"
    }
  ],
  "final_checks": []
}
```

## seq.make_material

Construct a kernel material with explicit physical properties or unknowns.

- Version: 0.0.0
- Effects: pure
- Does not establish: Wet-laboratory success, biological function or reaction efficiency.; Genome-wide safety or thermodynamic structure quality unless explicitly measured.

```json
{
  "inputs": [
    {
      "name": "sequence",
      "type": "value",
      "required": true,
      "constraints": {
        "type": "string",
        "pattern": "^[ACGTRYSWKMBDHVNacgtryswkmbdhvn]+$"
      },
      "description": "sequence"
    }
  ],
  "params": {
    "type": "object",
    "properties": {
      "topology": {
        "enum": [
          null,
          "linear",
          "circular"
        ]
      },
      "strandedness": {
        "enum": [
          null,
          "single",
          "double"
        ]
      },
      "ends": {
        "type": [
          "object",
          "null"
        ]
      },
      "features": {
        "type": "array",
        "items": {
          "type": "object"
        }
      }
    },
    "required": [],
    "additionalProperties": false
  },
  "outputs": [
    {
      "name": "material",
      "type": "material",
      "output_role": "component"
    }
  ],
  "final_checks": []
}
```

## seq.replace_region

Replace an explicit nonwrapping interval and retire intersecting annotations.

- Version: 0.0.0
- Effects: pure
- Does not establish: Wet-laboratory success, biological function or reaction efficiency.; Genome-wide safety or thermodynamic structure quality unless explicitly measured.

```json
{
  "inputs": [
    {
      "name": "material",
      "type": "material",
      "required": true,
      "constraints": {},
      "description": "material"
    },
    {
      "name": "insert",
      "type": "material",
      "required": false,
      "constraints": {},
      "description": "insert"
    }
  ],
  "params": {
    "type": "object",
    "properties": {
      "start": {
        "type": "integer",
        "minimum": 0
      },
      "end": {
        "type": "integer",
        "minimum": 0
      }
    },
    "required": [
      "start",
      "end"
    ],
    "additionalProperties": false
  },
  "outputs": [
    {
      "name": "product",
      "type": "material",
      "output_role": "component"
    },
    {
      "name": "report",
      "type": "document",
      "output_role": "analysis",
      "schema_ref": "urn:grt:schema:goal-v1#/$defs/value"
    }
  ],
  "final_checks": []
}
```

## seq.reverse_complement

Compute the IUPAC DNA reverse complement as a document.

- Version: 0.0.0
- Effects: pure
- Does not establish: Wet-laboratory performance or biological function.

```json
{
  "inputs": [
    {
      "name": "sequence",
      "type": "value",
      "required": true,
      "description": "DNA literal, at most 200 bases.",
      "constraints": {
        "type": "string",
        "minLength": 1,
        "maxLength": 200,
        "pattern": "^[ACGTRYSWKMBDHVNacgtryswkmbdhvn]+$"
      }
    }
  ],
  "params": {
    "type": "object",
    "properties": {},
    "additionalProperties": false
  },
  "outputs": [
    {
      "name": "result",
      "type": "document",
      "schema_ref": "urn:grt:schema:goal-v1#/$defs/value",
      "output_role": "analysis"
    }
  ],
  "final_checks": [
    {
      "check": "check.replay"
    },
    {
      "check": "check.lineage"
    },
    {
      "check": "check.dna_value_valid"
    }
  ]
}
```

## seq.rotate

Rotate a declared circle; D9 identity changes with the selected origin.

- Version: 0.0.0
- Effects: pure
- Does not establish: Wet-laboratory success, biological function or reaction efficiency.; Genome-wide safety or thermodynamic structure quality unless explicitly measured.

```json
{
  "inputs": [
    {
      "name": "material",
      "type": "material",
      "required": true,
      "constraints": {},
      "description": "material"
    }
  ],
  "params": {
    "type": "object",
    "properties": {
      "origin": {
        "type": "integer",
        "minimum": 0
      }
    },
    "required": [
      "origin"
    ],
    "additionalProperties": false
  },
  "outputs": [
    {
      "name": "material",
      "type": "material",
      "output_role": "component"
    }
  ],
  "final_checks": []
}
```

## seq.slice

Extract a zero-based half-open interval and transform exact annotations.

- Version: 0.0.0
- Effects: pure
- Does not establish: Wet-laboratory success, biological function or reaction efficiency.; Genome-wide safety or thermodynamic structure quality unless explicitly measured.

```json
{
  "inputs": [
    {
      "name": "material",
      "type": "material",
      "required": true,
      "constraints": {},
      "description": "material"
    }
  ],
  "params": {
    "type": "object",
    "properties": {
      "start": {
        "type": "integer",
        "minimum": 0
      },
      "end": {
        "type": "integer",
        "minimum": 0
      },
      "whole": {
        "type": "boolean"
      },
      "strand": {
        "enum": [
          -1,
          1
        ]
      }
    },
    "required": [
      "start",
      "end"
    ],
    "additionalProperties": false
  },
  "outputs": [
    {
      "name": "material",
      "type": "material",
      "output_role": "component"
    }
  ],
  "final_checks": []
}
```

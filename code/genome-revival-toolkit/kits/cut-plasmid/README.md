# Cut Plasmid

Offline Kit for inspecting or replacing a user-selected 20-base SpCas9 spacer. It checks the sequence-derived transcription direction, 3-prime NGG and self-targets in the supplied vector. It returns complete primers and an independently simulated inverse-PCR/circularization route. It does not enumerate candidate guides.

Load through the Core catalog. This directory has no command entry point, workflow runner, log writer or report renderer. Its contributions are the seven decorated capabilities, frozen selection knowledge, two pipeline templates and English text declared in `kit.json`. Kit document contracts are inline in their capability declarations.

Use [SKILL.md](SKILL.md) for routing and inputs. `template instantiate cut-plasmid.inspect_only` and `template instantiate cut-plasmid.replace_spacer` accept registered GenBank artifact source IDs, goal digest, explicit cassette coordinates and target IDs. The templates include the public GenBank read actions. They contain no gates or final-check overrides.

The 360-base [B2 fixture](examples/b2.json) is constructed from SPEC B2's fixed seed. It tests coordinate geometry and sequence reactions. It has no validated promoter, origin, resistance cassette or wet-laboratory use. All physical PCR, DpnI, KLD, transformation, sequencing and activity steps are `PLANNED` / `NOT_PERFORMED`.

Primer annealing lengths are searched dynamically. The B2 defaults are 18 to 36 bases and 55 to 62 degrees C with the complete DNA_NN3 inputs retained in `primer-set-v1`. The 5-prime guide tail is retained on the reverse primer. Binding cores must be unique on both template strands. Full-oligo hairpins, dimers and purification remain unassessed; a six-base homopolymer is disclosed rather than hidden.

The legacy 519-line selection file contains nine marker rules, yielding ten host-specific source-labelled rows. S2b adds `selection.ble.yeast` for yeast Zeocin selection, bringing the collection to eleven rows while retaining the original ten. Each row retains its citation, locator and scope. Source verification is `unverified`; no new human verification receipt or review is claimed. Missing-source rows belong in `knowledge/drafts/` and cannot load. No source-incomplete row occurred in this migration. Missing recipient genotype yields `UNKNOWN` without a plate recommendation. Genotype-dependent results are conditional on the supplied declaration, not a resistance or growth test.

The ble row matches `ble`, `bler`, `bleor`, `Sh ble`, `zeocin`, `phleomycin` and `bleomycin` case-insensitively at name boundaries. Its plate text retains the task-supplied working range, kill-curve requirement, pH and sorbitol conditions, and the warning against plating spheroplasts directly onto Zeocin medium. The primary source is the Thermo Fisher Scientific / Invitrogen Zeocin manual, 25-0078, Version J, 2002-08-22. The supplementary Drocourt et al. paper is recorded in `parameters.supplementary_sources` with all source fields; it supports only the marker's use in eukaryotes including yeast, not a concentration. Both sources remain `unverified`; the team must check the manual text.

Regenerate [knowledge/SOURCES.md](knowledge/SOURCES.md) from the current knowledge file without rerunning migration:

```powershell
.\.venv\Scripts\python.exe -X utf8 -B tests\oracles\prepare_cut_plasmid.py --sources-only
```

At `integration-1`, required Core annotation/CDS/sanity/reaction/order checks are absent, and the Core primer-quality interface does not consume this Kit's primer document. The Kit cannot complete B2 seal/portable verify on that base. See `QUESTIONS.md` S2-Q1. The end-to-end test retains the real rejected seal; it never replaces those checks or lowers the output role. The generated GenBank file is read back through Core actions; the existing stager exports bound materials/documents as JSON candidates.

From `code/genome-revival-toolkit` in this worktree:

```powershell
$env:PYTHONPATH='src'
$env:GRT_PRIMER3_CORE='<USER>/tools/primer3_core.exe'
.\.venv\Scripts\python.exe -X utf8 -B tools\check_structure.py
.\.venv\Scripts\python.exe -X utf8 -B -m unittest tests.unit.test_cut_plasmid -v
.\.venv\Scripts\python.exe -X utf8 -B -m unittest tests.unit.test_cut_plasmid_selection tests.e2e.test_cut_plasmid_selection -v
.\.venv\Scripts\python.exe -X utf8 -B tests\e2e\run_cut_plasmid.py --out '<WORK>/b2-new-run'
```

Replace `<USER>` with your user directory and `<WORK>` with a new evidence directory.
The executable must already be installed; this command does not download it.
`SUMMARY.json` distinguishes independent sequence/PCR checks from B2 acceptance. The standard-library-only `tests/e2e/independent_check.py` recomputes the spacer-only edit, target NGG, unique primer binding and inverse PCR plus closure from actual output files. It does not import this Kit or Core.

Source metadata was migrated offline. [knowledge/SOURCES.md](knowledge/SOURCES.md) lists references for team review. The technical gate remains for the specification owner to close. Official GitLab CI was not executed; GitHub CI was not run.

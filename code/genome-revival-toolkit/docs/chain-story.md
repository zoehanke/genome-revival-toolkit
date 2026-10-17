# Three sealed Kit runs: a synthetic data chain

Construct, Genome Identity and Revival Evidence were run through the public CLI.
The final case uses a fixed seed (2026101701), an 800 bp random reference with a
constructed 120 bp target ORF, and a distinct 96 bp synthetic marker sequence.
These sequences model roles; no biological gene or marker function is claimed.

The declared edit replaces [300,420). Construct prepares a 196 bp donor with
50 bp arms from [250,300) and [420,470), with a planned PCR/Gibson route. Identity
imports the exact sealed identity-handoff.json without rewriting it and checks
an external flanking pair on the two archived GenBank references. The predicted
products are 260 bp (original) and 236 bp (edited). Evidence imports Identity's
exact sealed expected-results file and synthetic observations (8 fusion-group,
30 control-group colonies, explicitly in colony units, with 100 uL reported
plating volume; two local PCR records). Local agreement is SUPPORTED. Functional
revival and whole-genome elimination remain INSUFFICIENT.

All laboratory operations are **PLANNED / NOT_PERFORMED**. This is developer-
assisted computational evidence, not an experiment, independent host evaluation,
strain-genotype verification or genome-wide specificity assessment.

## Inspect the evidence

- [Independent results](../tests/evidence/chain-story/final-distinct-orf/independent.json)
- [Combined demonstration card](../tests/evidence/chain-story/final-distinct-orf/chain-card.html)
- [Markdown card](../tests/evidence/chain-story/final-distinct-orf/chain-card.md)
- [Requests](../tests/evidence/chain-story/final-distinct-orf/requests/)
- [CLI receipts](../tests/evidence/chain-story/final-distinct-orf/receipts.json)
- [Standard-library checker](../tests/evidence/chain-story/check.py)

Three positive runs seal and verify. Each seal was copied and verified after its
original run path became unavailable. The foreign-background analysis also seals
as an accurately bounded INSUFFICIENT result. The final case contains 42 CLI
calls with a test-only socket guard; connection attempts total zero. File,
manifest and journal checks run on portable records. Construct's existing
format-roundtrip check is declared non-offline and is explicitly not rerun by
verify; the independent checker reads and recomputes the archived DNA directly.

The combined card is an **example projection of three sealed records**, not a
claim that the stock single-run viewer has a cross-run loading feature. Exactly
two solid links compare the producer's output byte SHA-256 with the next run's
registered input byte SHA-256. Remaining interpretation links are dashed. No
scientific causality is inferred. Original single-run cards remain in the seals.

## Failure controls and limits

1. One existing byte of the imported handoff is changed after goal registration.
   Execution returns SOURCE_CHANGED and sealing is refused. Current resolver
   failure state can remain RUNNING before step.started; this lifecycle gap is
   recorded as C13, not mislabeled HALTED.
2. A structurally valid table for different synthetic reference hashes yields
   INSUFFICIENT local agreement rather than silently supporting the observations.
3. A retained target/marker pair with shared junction cores amplifies 90 bp on
   both backgrounds. The junction gate correctly refuses it. A separate positive
   input has distinct target and marker cores. Its scientific expected lengths
   are fixed by construction, not learned from runtime results.

Identity's bundled template assumes FASTA; this host plan explicitly selects
GenBank readers to use Construct's hash-bound files. The Kit is unchanged. The
reference exports are archived format outputs under each seal's work directory;
they were not relabeled as analysis outputs or exempted from role checks.

Earlier setup failures, raw machine-path transcripts and original run directories
are retained under ignored dist/s1c-addendum-prototypes and dist/chain-story-raw.
Public receipts replace only local display paths with <project>; no sealed byte
was edited. No user DNA was read. Official GitLab CI was not executed. GitHub CI
was not run. Development-tree seals are not release evidence.

## Reproduce

Use the provisioned local Python environment, with PYTHONPATH=src, from the
product root. Choose a new output directory so earlier failures remain.

```powershell
python -X utf8 -B tests/e2e/run_chain_story.py --out dist/new-chain-story
python -X utf8 -B tests/evidence/chain-story/check.py dist/new-chain-story
```

To reproduce the shared-primer negative, use --gene-codon AAA with a new output
directory; expect junction-check rejection. The checker for that failed run is
`tests/evidence/chain-story/check_shared_primers.py`. Neither checker imports Core
or any Kit.

On Windows, deep content-addressed record paths may require Git's per-command
`-c core.longpaths=true`. The evidence-local .gitattributes preserves exact
line-ending bytes and recognizes CRLF for whitespace inspection. All 122 files
listed by the four portable manifests were compared with the Git index before
commit; their SHA-256 values match. Do not normalize or reformat sealed files.
